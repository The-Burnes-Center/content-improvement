import boto3
from utils import * 
import json
import time 

client  = boto3.client("bedrock-runtime", region_name="us-east-1")
#model_id = "anthropic.claude-3-7-sonnet-20250219-v1:0"
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

url1 = "https://www.nj.gov/state/elections/vote.shtml"

def code_accessibility_review(url): 

    html_code = get_pure_source(url)
    start_time = time.time()
    code_issues = []
    accessibility_improvements = []

    for i in range(10):
        #print(f"\n Iteration {i+1}: Finding next issue")
        accessibility_review = {}

        #if the issue is already in {code_issues}, do not include it.

        prompt1 = f'''You are a strict accessibility reviewer analyzing the following HTML: {html_code} 
                Your task is to identify **only real** accessibility issues based on WCAG 2.1 AA guidelines. 
                Do **not** invent problems. Do not include correct code. 
                Only include suggestions when an issue is present in the exact HTML. 

                - Only find a single issue 
                - Cite the exact HTML, if you can not find the exact HTML, do not return it.
                - If you can not find any issues return "DONE"  
                - Do not include extra text
                - Do not include an explaination

                
                An example of the output is: 
                '<img src="images"> alt = " " '

                An example of the output is:
                '''

        body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            { "role": "user", "content": prompt1 }
            ],
        "max_tokens": 5000,

        }

        resp = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json"
        ) 

        response_body = json.loads(resp["body"].read())

        code_issue = response_body["content"][0]["text"]
        accessibility_review["original_content"] = code_issue
        
        #print(f"code issue: {code_issue}")

        if code_issue not in code_issues:
            code_issues.append(code_issue)
        else:
            print("Repeating issue, No new accessibility issue found.")
            #end_time = time.time()
            continue
            # print(f"completed tasks: {end_time - start_time:.2f} seconds")   
            # return accessibility_improvements

        if "done" in code_issue.lower():  
            print(" Done: No accessibility issue found.")
            break 
            # end_time = time.time()
            # print(f"completed tasks: {end_time - start_time:.2f} seconds")  
            # return accessibility_improvements

        else: 
            prompt2 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
            Your task is to provide a suggestion for the identified code issue: {code_issue} based on WCAG 2.1 AA guidelines. 
            Only provide the HTML code that would be improving the given code issue. 

            - Only provide the improved HTML code 
            - if no code issue is given, for example an empty string "",  return an empty string: " "
            - if not code improvement is possible, return an empty string: ""
            - Do not include extra text
            - Do not include an explaination


            An example of the output is: 
            '<img src="images"> alt = "This is an image" '
            '''

            body["messages"].append({
                "role": "assistant",
                "content": code_issue
            })

            body["messages"].append({
                "role": "user",
                "content": prompt2.strip()
            })
            
            resp2 = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

        
            response_body2 = json.loads(resp2["body"].read())
            suggestion = response_body2["content"][0]["text"]
            accessibility_review["revised_content"] = suggestion
        #print(f"suggestion: {suggestion}")

            if suggestion == "":
                print("No accessibility issue found.")

            else: 

                prompt3 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
                Your task is to provide an explaination for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                Only provide an explaination for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                - if not explaination can be provided, return an empty string: ""
                - if no code issue is given, for example an empty string "",  return an empty string: " "
                - if no suggestion is given, for example an empty string "",  return an empty string: " "


                An example of the output is: 
                'Adding alt text to images provides a text alternative for screen reader users, improving accessibility in accordance with WCAG 2.1 guideline 1.1.1 (Non-text Content).'

                '''

            body["messages"].append({
                "role": "assistant",
                "content": suggestion 
            })

            body["messages"].append({
                "role": "user",
                "content": prompt3.strip()
            })
            
            resp3 = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

        
            response_body3 = json.loads(resp3["body"].read())
            explaination = response_body3["content"][0]["text"]
            accessibility_review["explaination"] = explaination
            #print(len(accessibility_improvements))

            accessibility_improvements.append(accessibility_review)

            #print(len(accessibility_improvements))
            #print(accessibility_review)




    end_time = time.time()
    print(f"completed tasks: {end_time - start_time:.2f} seconds") 
    

    return accessibility_improvements  

# print("here")
# reviews = code_accessibility_review(url1)

# print(f"reviews: {reviews}") 
# print(len(reviews))

