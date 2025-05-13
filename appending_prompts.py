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

                
                - #1 example of the output is: '<img src="images"> alt = " " '
                - #2 example of the output is: '<button></button>'
                - #3 example of the output is: '<a href="#">Click here</a>'
                - #4 example of the output is: '<label>Email</label><input type="email" id="user-email">'
                - #5 example of the output is: '<div onclick="openMenu()">Menu</div>'

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

            - #1 example of the output is: '<img src="images"> alt = "This is an image" '
            - #2 example of the output is: '<button aria-label="Submit form"></button>'
            - #3 example of the output is: '<a href="/reports">View the full election report</a>'
            - #4 example of the output is: '<label for="user-email">Email</label><input type="email" id="user-email">'
            - #5 example of the output is: '<button onclick="openMenu()">Menu</button>'

           


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

                - #1 example of the output is: 'Adding alt text to images provides a text alternative for screen reader users, improving accessibility in accordance with WCAG 2.1 guideline 1.1.1 (Non-text Content).'
                - #2 example of the output is: 'Using an aria-label on buttons without visible text ensures that assistive technology users can understand their function, supporting WCAG 2.1 guideline 4.1.2 (Name, Role, Value).'
                - #3 example of the output is: 'Replacing vague link text like "Click here" with descriptive text improves navigation and comprehension for screen reader users, meeting WCAG 2.1 guideline 2.4.4 (Link Purpose).'
                - #4 example of the output is: 'Using the 'for' attribute ensures labels are programmatically associated with form fields, which is essential for assistive technology users, aligning with WCAG 2.1 guideline 1.3.1 (Info and Relationships).'
                - #5 example of the output is: 'Interactive elements must use semantic HTML like <button> to be properly understood by screen readers and keyboard users, as outlined in WCAG 2.1 guideline 4.1.2 (Name, Role, Value).'




                
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

                - #1 example of the output is: 'Missing alt text for image'
                - #2 example of the output is: 'Button lacks accessible name'
                - #3 example of the output is: 'Non-descriptive link text'
                - #4 example of the output is: 'Label not associated with input field'
                - #5 example of the output is: 'Non-semantic interactive element'

                
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


print("html chunking")
print(chunked_script[0])
for chunk in chunked_script:
     print(f" length of chunk is {num_tokens(chunk)}")





print("text chunking: ")
text_chunks = chunk_html_text(url1)
print(text_chunks[0])

for chunk in text_chunks:
     print(f" length of chunk is {num_tokens(chunk)}")

print(f"number of chunks for html {len(chunked_script)}")
print(f"number of chunks for text {len(text_chunks)}")






# output = threading_code_accessibility(chunked_script)
# print(output)

# print(f"chunked_script: {chunked_script}")
# print("length of chunked_script: ", num_tokens(html_script))
# tokens = 0
# for chunk in chunked_script:
#     print(f' length chunk: {num_tokens(chunk)}')
#     tokens += num_tokens(chunk)

# print(f"total tokens: {tokens}")

# print(f"reviews: {reviews}") 
# # print(len(reviews))

