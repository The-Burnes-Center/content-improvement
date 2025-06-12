import instructor
from pydantic import BaseModel, Field, ValidationError
from instructor.exceptions import InstructorRetryException
from utils import * 
from typing import List
from dotenv import load_dotenv
from anthropic import AnthropicBedrock
import base64

from constants import MODEL_SELECTION, WEB_DESIGN_CLIENT, S3_BUCKET_NAME, MODEL_ID, MAX_TOKENS
load_dotenv()

'''
This script uses the Instructor library to analyze web design suggestions based on a webpage screenshot and layout guidelines.

When using claude models via Bedrock, a base64 encoding is required to process the image. 
Directly passing the s3_url or image will not work. 

'''


class WebSuggestion(BaseModel):
    key: int = Field(..., description = "A unique identifier for this suggestion item." )
    area: str = Field(...,description="A short, descriptive label for the area the suggestion applies to (e.g., 'Homepage').")
    suggestion: str = Field(...,description="A specific suggestion for improving the web design, such as 'Add a clear call-to-action button'.")
    reason: str = Field(...,description="A brief explanation of why this suggestion is important, such as 'Improves user engagement and guides users to key content.'")


def encode_image_to_base64(image_path):
    """
    Reads an image file and returns a base64-encoded string.
    """
    with open(image_path, "rb") as image_file:
        encoded_bytes = base64.b64encode(image_file.read())
        encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


def analyze_webdesign(url, Layout_guidelines): 
    """Using the OpenAI API, analyze the webpage screenshot and provide suggestions for improving the web design.
    Args:
        url (str): The URL of the webpage to analyze.
    Returns:
        output (List[WebSuggestion]) : A list of suggestions for improving the web design, each represented as a WebSuggestion object.
    """


    input_message = f"""Analyze this webpage screenshot and provide improvements for the layout of the page based off of the following guidelines: {Layout_guidelines}. \
                For each suggestion, provide an example of a part of the site that could be improved. Also cite specific guidelines in each suggestion. \
                If you cannot provide a specific element on the webpage as an example, do not include the suggestion. 
                
                Make sure that each suggestion is actionable, specific, and relevant to the webpage. 
                
                Do not include additional text and  
                Format the output in JSON, using the following structure:
                  [{{
                            key: '1',
                            area: 'Homepage',
                            suggestion: 'Add a clear call-to-action button',
                            reason: 'Improves user engagement and guides users to key content.',
                        }},"""

    screenshot_path = capture_screenshot(url)

    if MODEL_SELECTION: 
        #Using claude model 
        image_base64 = encode_image_to_base64(screenshot_path)

        image_payload = {
        "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",  
                "data": image_base64
            }
    }
        try: 

            resp = WEB_DESIGN_CLIENT.messages.create(
                model= MODEL_ID,
                max_tokens= MAX_TOKENS,
                messages=[
                    #if I wanted to add text guidlines, would i edit this or input text
                    {"role": "system", "content": "You are an AI expert in web accessibility. Analyze the image and provide WCAG-compliant suggestions."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": input_message},
                            image_payload
                        ],
                    },
                ], 
                response_model = List[WebSuggestion],
            )
        
            if not isinstance(resp, list):
                raise TypeError(f"Expected list, got {type(resp)}")
        
        #if the response is a list, check each item type for instance of ContentSuggestion
            else: 
                output = []
                for item in resp:
                    assert isinstance(item, WebSuggestion)
                    output.append({"key": item.key,
                                    "area": item.area,
                                    "suggestion": item.suggestion,
                                    "reason": item.reason})  
                    
                return output
        
        except (ValidationError, InstructorRetryException, TypeError) as e:
            print(f"Error processing Claude response:{e} ")
            return []


    else: 
        #Using open AI model 
        s3_url = upload_to_s3(screenshot_path, S3_BUCKET_NAME)

        try: 

            resp = WEB_DESIGN_CLIENT.chat.completions.create(
            model= MODEL_ID,
            messages=[
                #if I wanted to add text guidlines, would i edit this or input text
                {"role": "system", "content": "You are an AI expert in web accessibility. Analyze the image and provide WCAG-compliant suggestions."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": input_message},
                        {"type": "image_url", "image_url": {"url": s3_url}}
                    ],
                },
            ], 
            response_model = List[WebSuggestion],
            ) 

            # Check response type
            if not isinstance(resp, list):
                    raise TypeError(f"Expected list, got {type(resp)}")
            
            #if the response is a list, check each item type for instance of ContentSuggestion
            else: 
                output = []
                for item in resp:
                    assert isinstance(item, WebSuggestion)
                    output.append({"key": item.key,
                                    "area": item.area,
                                    "suggestion": item.suggestion,
                                    "reason": item.reason})  
                    
                return output
            
        except (ValidationError, InstructorRetryException, TypeError) as e:
            print(f"Error processing Claude response:{e} ")
            return []
            
        
# testing    
# url1 = "https://www.nj.gov/state/elections/vote.shtml"
# layout_guidelines1= read_file_text("contentlayoutguide.txt")
# print(analyze_webdesign(url1, layout_guidelines1))

    