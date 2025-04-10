import boto3
import json
import streamlit as st
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from openai import OpenAI
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1") 
S3_BUCKET_NAME = "nj-ai-votes-image"

s3_client = boto3.client("s3", region_name="us-east-1")

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

    #input text 
    # input_text = "Analyze this webpage screenshot and provide accessibility improvements. Provide suggestions for improving accessability of the page. Reference WCAG guidelines.\
    #             For each suggeston,  provide an example of a part of the site that could be improved  Also cite specific WCAG guidelines in each suggestion. \
    #             If you cannot provide a specific element on the webpage as an example, do not include the suggestion. "
    
    #input_text2 = "Analyze this webpage screenshot and based on the most important information for intented audience, please suggest feature rearrangements for the website"

    input_text = f"Analyze this webpage screenshot and provide improvements for the layout of the page based off of the following guidelines: {layout}. \
                For each suggestion, provide an example of a part of the site that could be improved. Also cite specific guidelines in each suggestion. \
                If you cannot provide a specific element on the webpage as an example, do not include the suggestion. "

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


def get_pure_source(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        source_code = response.text
        
        return source_code

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")

# Helper function to scrape the given website
def get_text_chunks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Focus on the main content area only
    main = soup.find('main')
    if not main:
        main = soup.body  # Fallback if no <main> tag

    chunks = []

    # Go through direct child elements inside <main> that might represent sections
    for elem in main.find_all(['section', 'div', 'article'], recursive=False):
        # Ignore elements likely to be navigation or footers by class/id
        if any(keyword in (elem.get('class') or []) + [elem.get('id') or ''] 
            for keyword in ['nav', 'navbar', 'footer', 'sidebar']):
            continue

        # Get cleaned text
        text = elem.get_text(separator=' ', strip=True)
        if text:
            chunks.append(text)

    # Remove duplicates or overlapping text chunks
    seen = set()
    unique_chunks = []
    for chunk in chunks:
        if chunk not in seen:
            seen.add(chunk)
            unique_chunks.append(chunk)
    
    print(len(unique_chunks))

    return unique_chunks


# Reads in a file and returns the text
def read_file_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error: {e}"

# Takes scrapped website data and a prompt, returns Claude 3.5 Sonnet's response
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
    
    # Stream the assistant's response
    assistant_response = ""
    assistant_message = st.chat_message("assistant")
    response_container = assistant_message.empty()
    
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
        response_container.write(assistant_response)  # Update the displayed text
    
    # Store the full assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Provide a link to the website you want to analyze."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    scrapped_data = scrape_result = get_text_chunks(prompt)

    content_guidlines = read_file_text("contentclarityguide.txt")

    for section in scrapped_data:
        get_pred(section, f"Provide suggestions for improving the clarity of the provided website text to align with {content_guidlines}. Cite specific examples of text that could be improved. Cite every single instance of text that could be improved that you find. Show the original and provide a revised version. ")

    # takes a picture and saves to s3 bucket 
    screenshot_path = capture_screenshot(prompt)
    s3_url = upload_to_s3(screenshot_path, S3_BUCKET_NAME)
    st.image(s3_url, caption="Website Screenshot")
    result = process_image_with_openai(s3_url)
    st.write("OpenAI Response:\n", result)

    get_pred(get_pure_source(prompt), f"Provide suggestions for improving the provided HTML to align with WCAG 2.1 AA standards. Cite specific examples of HTML that could be improved. Cite every single instance of HTML that could be improved that you find. Show the original and provide a revised version. ")