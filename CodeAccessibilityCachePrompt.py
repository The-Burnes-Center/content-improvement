import boto3
from utils import * 
import json
import time 
from bs4 import BeautifulSoup
import tiktoken
import concurrent.futures

client  = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

html_code = ''
code_issue = '' 
suggestion = ''

accessibility_review = {}


#prompts 
prompt_code_issue = f'''You are a strict accessibility reviewer analyzing the following HTML: {html_code} 
                Your task is to identify **only real** accessibility issues based on WCAG 2.1 AA guidelines. 
                Do **not** invent problems. Do not include correct code. 
                Only include suggestions when an issue is present in the exact HTML. 

                - Only find a single issue 
                - Cite the exact HTML, if you can not find the exact HTML, do not return it.
                - If you can not find any issues return "DONE"  
                - Do not include extra text
                - Do not include an explanation

                
                An example of the output is: 
                '<img src="images"> alt = " " '

                An example of the output is:
                
                '''

prompt2 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
            Your task is to provide a suggestion for the identified code issue: {code_issue} based on WCAG 2.1 AA guidelines. 
            Only provide the HTML code that would be improving the given code issue. 

            - Only provide the improved HTML code 
            - if no code issue is given, for example an empty string "",  return an empty string: " "
            - if not code improvement is possible, return an empty string: ""
            - Do not include extra text
            - Do not include an explanation


            An example of the output is: 
            '<img src="images"> alt = "This is an image" '
            '''
prompt3 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
                Your task is to provide an explanation for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                Only provide an explanation for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                - if no explanation can be provided, return an empty string: ""
                - if no code issue is given, for example an empty string "",  return an empty string: " "
                - if no suggestion is given, for example an empty string "",  return an empty string: " "


                An example of the output is: 
                'Adding alt text to images provides a text alternative for screen reader users, improving accessibility in accordance with WCAG 2.1 guideline 1.1.1 (Non-text Content).'

                '''


prompt4 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
                Your task is to provide a label for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines and the explanation: {explanation}.
                Only provide a label for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines and the explanation: {explanation}. 


                - if no label can be provided, return an empty string: ""
                - if no code issue is given, for example an empty string "",  return an empty string: " "
                - if no suggestion is given, for example an empty string "",  return an empty string: " "
                - if no explanation is given, for example an empty string "",  return an empty string: " "

                An example of the output is: 
                'Missing alt text for image'

                '''

body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            { "role": "user", "content": prompt_code_issue }
            ],
        "max_tokens": 5000,
        }

response  = client.invoke_model(
    modelId=model_id,
    body=json.dumps(body),
    contentType="application/json"
) 

response_body = json.loads(response["body"].read())

code_issue = response_body["content"][0]["text"]
accessibility_review["original_content"] = code_issue
        

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=5000,
    system=[
      {
        "type": "text",
        "text": "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.\n",
      },
      {
        "type": "text",
        "text": "<the entire contents of 'Pride and Prejudice'>",
        "cache_control": {"type": "ephemeral"}
      }
    ],
    messages=[{"role": "user", "content": "Analyze the major themes in 'Pride and Prejudice'."}],
)
print(response.usage.model_dump_json())

# Call the model again with the same inputs up to the cache checkpoint
response = client.messages.create(.....)
print(response.usage.model_dump_json())
