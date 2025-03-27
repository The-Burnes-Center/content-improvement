import boto3
import json
import streamlit as st
import requests
from bs4 import BeautifulSoup




#reads in the file guides 
def read_multiple_css(css_files):
    combined_css = ""
    for file_path in css_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                combined_css += f.read() + "\n"  # Append each CSS file's content
        except Exception as e:
            combined_css += f"/* Error loading {file_path}: {e} */\n"
    return combined_css

# Define the list of CSS files (Update with your actual file names)
css_files = ("bootstrap.min.css","engage.css", "njvote.css", "site-base.css", "sonj-components.css" )
css_styles = read_multiple_css(css_files)



# Helper function to scrape the given website
def get_source_code(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        assistant_message = st.chat_message("assistant")
        response_container = assistant_message.empty()
        response_container.write("Please enter a valid URL.")

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

    return assistant_response
    
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

    scrapped_data = get_source_code(prompt)

    content_guidlines = read_file_text("contentclarityguide.txt")

    #get_pred(scrapped_data, f"Provide suggestions for improving content clarity of the website to align with {content_guidlines}. Feel free to rewrite sections of the website that do not align with the guidelines. For each suggestion, provide an example of a part of the site that could be improved. Do not include HTML in the output, only look at the actual content.")
    # get_pred(scrapped_data, "Provide suggestions for improving accessability of the page. Reference WCAG guidelines. For each suggeston, provide an example of a part of the site that could be improved. Also cite specific WCAG guidelines in each suggestion. If you cannot provide a specific element on the webpage as an example, do not include the suggestion. You can include the HTML tags in the output, and your suggestion for how to fix them. Make sure to clearly indicate what part of the website the HTML tags are from.")
    # get_pred(scrapped_data, "Check if there is repetitve content on the given website. Provide examples of the repetitive content and suggest how to improve it. For example, if there are multiple parts of the website where the general election date is given, flag those and suggest a single place for this information.")
    
    output = get_pred(scrapped_data, "Provide suggestions for improving accessability of the page. Reference WCAG guidelines."
            "For each suggeston,  provide an example of a part of the site that could be improved  Also cite specific WCAG guidelines in each suggestion."
            "If you cannot provide a specific element on the webpage as an example, do not include the suggestion.  "
            "Find the id  html code relating to the suggestion and label the beginning and end of the html code with <HTML>. Make sure to clearly indicate what part of the website the HTML tags are from.")


    # output2 = get_pred(scrapped_data, "provide specific elements of the wesbite that could be improved based on the Reference WCAG guidelines.\
    #                     Tag the elements with <Title> at the beginning and at end ") 
                       
    # soup = BeautifulSoup(output, "html.parser")
    # html_tags = soup.find_all("html")
    # for tag in html_tags:

    #     extracted_content = tag.decode_contents().strip() # Extract inner content
    #     print(extracted_content)
    #     full_content = full_html = f"""
    #     <!DOCTYPE html>
    #     <html lang="en">
    #     <head>
    #         <style>
    #             {css_styles}  /* Embed the Local CSS */
    #         </style>
    #     </head>
    #     <body>
    #         {extracted_content}  <!-- Insert the extracted HTML content -->
    #     </body>
    #     </html>
    #     """
    #     st.components.v1.html(full_content, height=400, scrolling=True)
    #     #exit()


    # html content is currently only looking for Important dates for NJ Voters based on the prompted 
    '''
    html_content = get_pred(scrapped_data, f"Based on this html code, find the html code relating to Important dates for NJ Voters") 

    full_content = full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <style>
                {css_styles}  /* Embed the Local CSS */
            </style>
        </head>
        <body>
            {html_content}  <!-- Insert the extracted HTML content -->
        </body>
        </html>
        """

    

    #st.markdown(f"```html\n{full_content}\n```")
    
    #print(f"the content is {html_content}")

    st.components.v1.html(full_content, height=400, scrolling=True)
    '''

    """
     <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>" "</title>
    """


    """
    webscraping open ai agent sdk 
    
    """