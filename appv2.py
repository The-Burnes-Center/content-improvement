from openai import OpenAI # Import the OpenAI package
import os # Import the os package
import streamlit as st # UI lib 
from playwright.sync_api import sync_playwright # processing image lib
import boto3

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

def upload_to_s3(file_path, bucket_name, object_name=None):
    """Uploads the screenshot to an S3 bucket and returns its URL."""
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})  
    s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
    return s3_url


def process_image_with_openai(image_url):
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    #input text 
    input_text = "Analyze this webpage screenshot and provide accessibility improvements. Provide suggestions for improving accessability of the page. Reference WCAG guidelines.\
                For each suggeston,  provide an example of a part of the site that could be improved  Also cite specific WCAG guidelines in each suggestion. \
                If you cannot provide a specific element on the webpage as an example, do not include the suggestion. "
    
    #input_text2 = "Analyze this webpage screenshot and based on the most important information for intented audience, please suggest feature rearrangements for the website"

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



st.title("Content Managment Tool")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Provide a link to the website you want to analyze."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input():
    #print(prompt)
    if prompt.startswith("http"):
        st.write(prompt)
        screenshot_path = capture_screenshot(prompt)
        s3_url = upload_to_s3(screenshot_path, S3_BUCKET_NAME)
        st.image(s3_url, caption="Website Screenshot")
        result = process_image_with_openai(s3_url)
        st.write("OpenAI Response:\n", result)


# prompt chat to rearrange wesbite based on what is most useful to constitents 
# chat produces glossary 