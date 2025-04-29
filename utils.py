import requests
from bs4 import BeautifulSoup
import boto3
import os
import json
from playwright.sync_api import sync_playwright
from openai import OpenAI
import re 
import tiktoken



bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

AWS_REGION = os.getenv("AWS_REGION", "us-east-1") 
S3_BUCKET_NAME = "nj-ai-votes-image"

s3_client = boto3.client("s3", region_name="us-east-1")
tokenizer = tiktoken.get_encoding('cl100k_base')

def get_pred(scrapped_data, prompt):
    summary = f"Look at the following website source code: {scrapped_data}. {prompt}"
    input_data = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": summary}  # Directly set the user input
        ],
        "max_tokens": 2048,  # Use `max_tokens` instead of `max_tokens_to_sample`
        "temperature": 0,
    }

    response = bedrock_client.invoke_model_with_response_stream(
        modelId=model_id,
        body=json.dumps(input_data),
        contentType="application/json"
    )

    event_stream = response["body"]
    
    assistant_response = ""
    
    for event in event_stream:
        event_str = event['chunk']['bytes'].decode()
        if 'delta' in event_str:
            try:
                delta_index = event_str.index('text\":')
                str = event_str[delta_index:][7:-3]
                str = str.replace("\\n", "\n")
                str = str.replace("\\\"", "\"")
                str = str.replace("•", "\n•\n")
                assistant_response += str
            except:
                pass
            
    return assistant_response


def read_file_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error: {e}"
    





## Webdesign Functions

#use playwright to capture screen shot 
def capture_screenshot(url, filepath="screenshot.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=filepath, full_page=True)
        browser.close()

        return filepath

#uploads image to s3 bucket 
def upload_to_s3(file_path, bucket_name, object_name=None):
    """Uploads the screenshot to an S3 bucket and returns its URL."""
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})  
    s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
    return s3_url

def process_image_with_openai(image_url):
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    layout = read_file_text("contentlayoutguide.txt")

    #prompt and structured format 
    input_text = f"""Analyze this webpage screenshot and provide improvements for the layout of the page based off of the following guidelines: {layout}. \
                For each suggestion, provide an example of a part of the site that could be improved. Also cite specific guidelines in each suggestion. \
                If you cannot provide a specific element on the webpage as an example, do not include the suggestion. Do not include additional text and 
                Format the output in JSON, using the following structure:
                    
                    const data = [
                        {{
                            key: '1',
                            area: 'Homepage',
                            suggestion: 'Add a clear call-to-action button',
                            reason: 'Improves user engagement and guides users to key content.',
                        }},
                        {{
                            key: '2',
                            area: 'Navigation Menu',
                            suggestion: 'Simplify menu structure',
                            reason: 'Helps users find content faster and reduces cognitive load.',
                        }},
                        {{
                            key: '3',
                            area: 'Accessibility',
                            suggestion: 'Add alt text for all images',
                            reason: 'Ensures compliance with WCAG and improves screen reader support.',
                        }},
                        ] 
    
    
    
    """

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            #if I wanted to add text guidlines, would i edit this or input text
            {"role": "system", "content": "You are an AI expert in web accessibility. Analyze the image and provide WCAG-compliant suggestions."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": input_text},
                    {"type": "image_url", "image_url": {"url": image_url}}
                    #{"type": "text", "text": input_text2}
                ],
            },
        ]
    )

    return completion.choices[0].message.content


def webdesign_extract_text(input_text):
    """
    Extracts all substrings enclosed in square brackets (including the brackets themselves).
    Args:
        input_text (str): The input string containing potential bracketed content.
    Returns:
        str: A single string with only the bracketed content preserved.
    """
    matches = re.findall(r'\[[^\[\]]*\]', input_text)
    return ''.join(matches)

##Code accessibility Functions

def get_pure_source(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        source_code = response.text
        
        return source_code

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")


#content clarity functions

def num_tokens(text):
    """Calculate the number of tokens in a string using tiktoken."""
    return len(tokenizer.encode(text))

def chunk_element(element, max_tokens=5000):
    """Recursively split an element if its text exceeds max_tokens."""
    text = element.get_text(separator=' ', strip=True)
    if num_tokens(text) <= max_tokens:
        return [text]
    
    # If it's too big and has children, try to split further
    chunks = []
    for child in element.find_all(['section', 'div', 'article'], recursive=False):
        child_text = child.get_text(separator=' ', strip=True)
        if child_text and num_tokens(child_text) <= max_tokens:
            chunks.append(child_text)
        elif child_text:
            # Recursively split again if child is still too big
            chunks.extend(chunk_element(child, max_tokens))
    
    # If no children are found, fallback: just forcibly split the text
    if not chunks and text:
        chunks = force_split_text(text, max_tokens)
    
    return chunks

def force_split_text(text, max_tokens):
    """Fallback: split a huge block of text into hard chunks if no more structure."""
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        sub_tokens = tokens[i:i+max_tokens]
        sub_text = tokenizer.decode(sub_tokens)
        chunks.append(sub_text)
    return chunks

def chunk_html(url, max_tokens=5000):
    """Download HTML and chunk it by token size using structural recursion."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    main = soup.find('main')
    if not main:
        main = soup.body  # fallback
    
    chunks = []
    # Only start from direct children
    for elem in main.find_all(['section', 'div', 'article'], recursive=False):
        text = elem.get_text(separator=' ', strip=True)
        if not text:
            continue
        
        if num_tokens(text) <= max_tokens:
            chunks.append(text)
        else:
            # Go deeper recursively
            chunks.extend(chunk_element(elem, max_tokens))
    
    return chunks


