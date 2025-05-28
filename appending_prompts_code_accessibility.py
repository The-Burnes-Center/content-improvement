import boto3
from utils import * 
import json
import time 
from bs4 import BeautifulSoup
import tiktoken
import concurrent.futures

"""
This script uses the Claude AI model to analyze HTML code for accessibility issues and suggest improvements based on WCAG 2.1 AA guidelines.
Four API calls are used to create a structured response  which includes the original code issue, the suggested improvement, the explanation, and the label for the suggested improvement.
"""


client  = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

tokenizer = tiktoken.get_encoding('cl100k_base') 

url1 = "https://www.nj.gov/state/elections/vote.shtml"
max_issues = 1


def chunk_html_script(html_script, max_tokens = 5000):
    """
    This function takes a HTML script and chunks it into smaller pieces based on the max number of tokens.
    Args:
        html_script (str): The HTML script to be chunked.
        max_tokens (int): The maximum number of tokens allowed in each chunk. 

    Returns:
        list: A list of HTML chunks.

    """
    chunks = []

    soup = BeautifulSoup(html_script, 'html.parser')
    full_html = soup.html

    chunks = []

    #iterates though direct children of <html> 
    for top_ele in full_html.find_all(['head', 'body'], recursive= False):
        #iterates though direct children of <head. and <body> maintaining structure 
        for elem in top_ele.find_all(['section', 'div', 'article', 'li'], recursive=False):
            html_chunk = str(elem)
            if not html_chunk:
                continue
            
            if num_tokens(html_chunk) <= max_tokens:
                chunks.append(html_chunk)
            else:
                # Go deeper recursively
                chunks.extend(chunk_element(elem, max_tokens))

    return chunks

    

def threading_code_accessibility(chunked_html_code):
    """
    This function takes a list of HTML code chunks and processes them in parallel to find accessibility issues.
    Args:
        chunked_html_code (list): A list of HTML code chunks.
    Returns:
        list: A list of suggestions for accessibility improvements.
    """
    suggestions = []
    # Use ThreadPoolExecutor to process the HTML code chunks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_section = {
            executor.submit(code_accessibility_review, section): section
            for section in chunked_html_code
        }

        for future in concurrent.futures.as_completed(future_to_section):
            try:
                result = future.result()
                suggestions.extend(result)
            except Exception as e:
                print(f"Error processing a section: {e}")

    return suggestions


def code_accessibility_review(html_code): 
    """
    Using Claude AI, analyze the HTML code to provide suggestions for improving accessibility. 
    This function identifies accessibility issues in the provided HTML code and suggests improvements based on WCAG 2.1 AA guidelines.
    The function uses Claude AI and appends messages in conversation to relationally find the orginal code issue, the suggested improvement, the explanation, and the label for the suggested improvement.

    Args:
        html_code (str): The HTML code to be analyzed.
    Returns:
        list: A list of suggestions for accessibility improvements.The list contains dictionaries with the following keys:
            - original_content: The original HTML code with the accessibility issue.
            - revised_content: The suggested improvement for the HTML code.
            - explanation: An explanation of why the suggested improvement is necessary.
            - label: A label for the identified code issue and suggested improvement.
    """

    code_issues = []
    accessibility_improvements = []

    for i in range(max_issues):

        # Initialize the accessibility review dictionary
        accessibility_review = {}

        #prompt for finding the code issue
        prompt1 = f'''You are a strict accessibility reviewer analyzing the following HTML: {html_code} 
                Your task is to identify **only real** accessibility issues based on WCAG 2.1 AA guidelines. 
                Do **not** invent problems. Do not include correct code. 
                Only include suggestions when an issue is present in the exact HTML. 

                - Only find a single issue 
                - Cite the exact HTML, if you can not find the exact HTML, do not return it.
                - If you can not find any issues return "DONE"  
                - Do not include extra text
                - Do not include an explanation

                
                - #1 example of the output is: '<img src="images"> alt = " " '
                - #2 example of the output is: '<button></button>'
                - #3 example of the output is: '<a href="#">Click here</a>'
                - #4 example of the output is: '<label>Email</label><input type="email" id="user-email">'
                - #5 example of the output is: '<div onclick="openMenu()">Menu</div>'

                '''
        # Create the body for the request
        body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            { "role": "user", "content": prompt1 }
            ],
        "max_tokens": 5000,

        }
        # Send the request to the model
        resp = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json"
        ) 


        # Read the response
        response_body = json.loads(resp["body"].read())
        code_issue = response_body["content"][0]["text"]

        # add the code issue to the accessibility review dictionary
        accessibility_review["original_content"] = code_issue
        
        # Check if the code issue is already in the list
        if code_issue not in code_issues:
            code_issues.append(code_issue)

        else:
            # if code  issue is already in the list, continue to the next iteration
            continue
    
        # Check if the code issue is "DONE"
        if "done" in code_issue.lower():  
            break 
           
        #if code issue found, countinue to find the suggestion, explanation, and label
        else: 
            #prompt for finding the code suggestion
            prompt2 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
            Your task is to provide a suggestion for the identified code issue: {code_issue} based on WCAG 2.1 AA guidelines. 
            Only provide the HTML code that would be improving the given code issue. 

            - Only provide the improved HTML code 
            - if no code issue is given, for example an empty string "",  return an empty string: " "
            - if not code improvement is possible, return an empty string: ""
            - Do not include extra text
            - Do not include an explanation

            - #1 example of the output is: '<img src="images"> alt = "This is an image" '
            - #2 example of the output is: '<button aria-label="Submit form"></button>'
            - #3 example of the output is: '<a href="/reports">View the full election report</a>'
            - #4 example of the output is: '<label for="user-email">Email</label><input type="email" id="user-email">'
            - #5 example of the output is: '<button onclick="openMenu()">Menu</button>'



            '''
            #append the code issue to the body
            body["messages"].append({
                "role": "assistant",
                "content": code_issue
            })
            #append the prompt to the body
            body["messages"].append({
                "role": "user",
                "content": prompt2.strip()
            })
            # Send the request to the model
            resp2 = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

            # Read the response and add the suggestion to the accessibility review dictionary
            response_body2 = json.loads(resp2["body"].read())
            suggestion = response_body2["content"][0]["text"]
            accessibility_review["revised_content"] = suggestion
    
            # if suggestion is not found, print a message
            if suggestion == "":
                continue
        
            #if suggestion is found, continue to find the explanation 
            else: 
                #prompt for finding the code explanation
                prompt3 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
                Your task is to provide an explanation for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                Only provide an explanation for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                - if no explanation can be provided, return an empty string: ""
                - if no code issue is given, for example an empty string "",  return an empty string: " "
                - if no suggestion is given, for example an empty string "",  return an empty string: " "

                - #1 example of the output is: 'Adding alt text to images provides a text alternative for screen reader users, improving accessibility in accordance with WCAG 2.1 guideline 1.1.1 (Non-text Content).'
                - #2 example of the output is: 'Using an aria-label on buttons without visible text ensures that assistive technology users can understand their function, supporting WCAG 2.1 guideline 4.1.2 (Name, Role, Value).'
                - #3 example of the output is: 'Replacing vague link text like "Click here" with descriptive text improves navigation and comprehension for screen reader users, meeting WCAG 2.1 guideline 2.4.4 (Link Purpose).'
                - #4 example of the output is: 'Using the 'for' attribute ensures labels are programmatically associated with form fields, which is essential for assistive technology users, aligning with WCAG 2.1 guideline 1.3.1 (Info and Relationships).'
                - #5 example of the output is: 'Interactive elements must use semantic HTML like <button> to be properly understood by screen readers and keyboard users, as outlined in WCAG 2.1 guideline 4.1.2 (Name, Role, Value).'




                
                '''
            #append the suggestion to the body
            body["messages"].append({
                "role": "assistant",
                "content": suggestion 
            })
            #append the prompt to the body
            body["messages"].append({
                "role": "user",
                "content": prompt3.strip()
            })
            
            # Send the request to the model
            resp3 = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

            
            # Read the response and add the explanation to the accessibility review dictionary
            response_body3 = json.loads(resp3["body"].read())
            explanation = response_body3["content"][0]["text"]
            accessibility_review["explanation"] = explanation
 

            if explanation == "":
                continue

            else: 
                #prompt for producing the label
                prompt4 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
                Your task is to provide a label for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines and the explanation: {explanation}.
                Only provide a label for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines and the explanation: {explanation}. 


                - if no label can be provided, return an empty string: ""
                - if no code issue is given, for example an empty string "",  return an empty string: " "
                - if no suggestion is given, for example an empty string "",  return an empty string: " "
                - if no explanation is given, for example an empty string "",  return an empty string: " "

                - #1 example of the output is: 'Missing alt text for image'
                - #2 example of the output is: 'Button lacks accessible name'
                - #3 example of the output is: 'Non-descriptive link text'
                - #4 example of the output is: 'Label not associated with input field'
                - #5 example of the output is: 'Non-semantic interactive element'

                
                '''
            #append the explanation to the body
            body["messages"].append({
                "role": "assistant",
                "content": explanation 
            })
            #append the prompt to the body
            body["messages"].append({
                "role": "user",
                "content": prompt4.strip()
            })

            # Send the request to the model
            resp3 = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            # Read the response and add the label to the accessibility review dictionary
            response_body4 = json.loads(resp3["body"].read())
            label = response_body4["content"][0]["text"]
            accessibility_review["label"] = label

            if label == "":
                continue
            #if label is found, append the accessibility review dictionary to the list of accessibility improvements
            elif (accessibility_review["original_content"]!= "" and 
                  accessibility_review["revised_content"] != "" and 
                  accessibility_review["original_content"]!= "" and 
                  accessibility_review["explanation"] != "") :
            
                #append the accessibility review dictionary to the list of accessibility improvements
                accessibility_improvements.append(accessibility_review)
          
    

    return accessibility_improvements  




# correct print statemments for chunking and threading 
# html_script = get_pure_source(url1)
# chunked_script = chunk_html_script(html_script)
# suggestions = threading_code_accessibility(chunked_script)
# print(suggestions)


