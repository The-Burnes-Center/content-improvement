import requests
from bs4 import BeautifulSoup
import boto3
import os
import json
from playwright.sync_api import sync_playwright
from openai import OpenAI
import re 
import tiktoken

from constants import S3_CLIENT, AWS_REGION, ANTHROPIC_VERSION, MAX_TOKENS, MODEL_SELECTION
from constants import BOTO3_CLIENT, OPEN_AI_CLIENT, MODEL_ID




# bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
# model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"


tokenizer = tiktoken.get_encoding('cl100k_base')

def get_pred(scrapped_data, prompt):
    """Analyzing the webpage source code and provide suggestions for improving the web design.
    Args:
        scrapped_data (str): The source code of the webpage to analyze.
        prompt (str): The prompt to guide the analysis.
    Returns:
        str: The response from the model based on the provided source code and prompt.
    """

    summary = f"Look at the following website source code: {scrapped_data}. {prompt}"

    if MODEL_SELECTION:

        body = {
            "anthropic_version": ANTHROPIC_VERSION,
            "messages": [
                { "role": "user", "content": summary }
                ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0,

            }
        
    
        resp = BOTO3_CLIENT.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(body),
            contentType="application/json"
        ) 
    


        # Read the response
        response_body = json.loads(resp["body"].read())
        assistant_response = response_body["content"][0]["text"]
       

        return assistant_response
        
    else: 
        #using open AI Model 
        body = {
            "messages": [
                { "role": "user", "content": summary }
                ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0,

            }
        
    
        resp = OPEN_AI_CLIENT.chat.completions.create(
            model=MODEL_ID,
            messages= body["messages"],
            max_tokens= body["max_tokens"],
            temperature= body["temperature"],
        ) 

        assistant_response = resp.choices[0].message.content 

        return assistant_response


def read_file_text(file_path):
    """Reads the content of a text file and returns it as a string.
    Args:
        file_path (str): The path to the text file.
    Returns:
        str: The content of the file as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error: {e}"
    



## Webdesign Functions
def capture_screenshot(url, filepath="screenshot.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # try headless=False
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()
        page.goto(url, timeout=60000)
        page.screenshot(path=filepath, full_page=True)
        browser.close()
        return filepath


def upload_to_s3(file_path, bucket_name, object_name=None):
    """Uploads the screenshot to an S3 bucket and returns its URL."""
    if object_name is None:
        object_name = os.path.basename(file_path)

    S3_CLIENT.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})  
    s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
    return s3_url


##Code accessibility Functions

def get_pure_source(url):
    """Fetch the source code of a webpage and return it as plain text.
    Args:
        url (str): The URL of the webpage to fetch.
    Returns:
        str: The source code of the webpage as plain text.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        source_code = response.text
        return source_code
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")


# Chunking Functions 
def num_tokens(text):
    """Calculate the number of tokens in a string using tiktoken."""
    return len(tokenizer.encode(text))

def chunk_element(element, max_tokens=5000):
    """Recursively split an element if its text exceeds max_tokens.
    Args:
        element (BeautifulSoup element): The HTML element to process.
        max_tokens (int): The maximum number of tokens allowed in a chunk.
    Returns:
        list: A list of text chunks, each within the token limit.
        """
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

def chunk_html_text(url, max_tokens=5000):
    """Download HTML and chunk it by token size using structural recursion Used for chunking the HTML text."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
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



