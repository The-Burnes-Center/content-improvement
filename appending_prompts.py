import boto3
from utils import * 
import json
import time 
from bs4 import BeautifulSoup
import tiktoken
import concurrent.futures

client  = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

tokenizer = tiktoken.get_encoding('cl100k_base') 

url1 = "https://www.nj.gov/state/elections/vote.shtml"
max_issues = 1


def chunk_html_script(html_script, max_tokens = 5000):
    chunks = []


    #whats the best waay to seperate but still maintain structure?
    soup = BeautifulSoup(html_script, "html.parser")
    elements = soup.find_all("li", class_=["list-group-item", "list-group-item-action"])

    chunks = []
    current_chunk = ""
    current_tokens = 0

    for li in elements:
        li_html = str(li)
        li_tokens = num_tokens(li_html)

        if current_tokens + li_tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = li_html
            current_tokens = li_tokens
        else:
            current_chunk += li_html
            current_tokens += li_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def threading_code_accessibility(chunked_html_code):
    suggestions = []
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

    # html_code = get_pure_source(url)
    # print(f"html_code: {html_code}")

    

    start_time = time.time()
    code_issues = []
    accessibility_improvements = []

    for i in range(max_issues):
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
                - Do not include an explanation

                
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
            print(f"code issue already found: {code_issue}")
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
            - Do not include an explanation


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
                print("No suggestion found.")

            else: 

                prompt3 = f'''You are a strict accessibility reviewer analyzing the following HTML: 
                Your task is to provide an explanation for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                Only provide an explanation for the identified code issue: {code_issue} and suggested improvement: {suggestion} based on WCAG 2.1 AA guidelines. 

                - if no explanation can be provided, return an empty string: ""
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
            explanation = response_body3["content"][0]["text"]
            accessibility_review["explanation"] = explanation
            #print(len(accessibility_improvements))

            if explanation == "":
                print("No explanation found.")

            else: 

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

            body["messages"].append({
                "role": "assistant",
                "content": explanation 
            })

            body["messages"].append({
                "role": "user",
                "content": prompt4.strip()
            })
            
            resp3 = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

            response_body4 = json.loads(resp3["body"].read())
            label = response_body4["content"][0]["text"]
            accessibility_review["label"] = label

            if label == "":
                print("No label found.")


            accessibility_improvements.append(accessibility_review)
            appending_time = time.time()
            print(f"appending time: {appending_time - start_time:.2f} seconds")

            #print(len(accessibility_improvements))
            #print(accessibility_review)




    end_time = time.time()
    print(f"completed tasks: {end_time - start_time:.2f} seconds") 
    

    return accessibility_improvements  



# print("here")
# reviews = code_accessibility_review(url1)

#print(chunk_html_script(url1))
html_script = get_pure_source(url1)
chunked_script = chunk_html_script(html_script)

output = threading_code_accessibility(chunked_script)
print(output)

# print(f"chunked_script: {chunked_script}")
# print("length of chunked_script: ", num_tokens(html_script))
# tokens = 0
# for chunk in chunked_script:
#     print(f' length chunk: {num_tokens(chunk)}')
#     tokens += num_tokens(chunk)

# print(f"total tokens: {tokens}")

# print(f"reviews: {reviews}") 
# # print(len(reviews))

