import requests
from bs4 import BeautifulSoup
import boto3
import os
import json


bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

AWS_REGION = os.getenv("AWS_REGION", "us-east-1") 
S3_BUCKET_NAME = "nj-ai-votes-image"

s3_client = boto3.client("s3", region_name="us-east-1")

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