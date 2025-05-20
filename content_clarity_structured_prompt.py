import instructor
from anthropic import AnthropicBedrock
from pydantic import BaseModel, Field, ValidationError
from utils import * 
from typing import List
from instructor.exceptions import InstructorRetryException

"""
This module provides a function to analyze the clarity of website content and suggest improvements.
It uses the Anthropic Claude model to generate suggestions based on provided content guidelines."""

# Define the ContentSuggestion model
class ContentSuggestion(BaseModel):
    original_content: str = Field(..., description="The original text that does not meet content clarity standards." )
    suggestion: str = Field(..., description="The revised text that meets content clarity standards." )
    

def anaylze_content_clarity(section, content_guidlines):
    """Analyze a section of text for content clarity and suggest improvements.
    Args:
        section (str): The section of text to analyze.
        content_guidlines (str): The content clarity guidelines to follow.
    Returns:
        output (List[ContentSuggestion]): A list of suggestions for improving content clarity."""
   
    input_message =  f'''
        You are a professional content clarity editor. Analyze the following website section:{section}
        Your task is to suggest improvements to the **clarity** of the website text according to the 
        following content guidelines:{content_guidlines}

        You must:
        - Identify **real examples** where clarity can be improved (e.g., vague language, long sentences, jargon).
        - **Only include suggestions where improvement is clearly necessary**.
        - Limit the output to a **maximum of 5 suggestions**.
        - Do **not** include any explanation, reasoning, or commentary.
        - Do **not** suggest changes if the original content is already clear.
        Return your response as ** ONLY* a raw JSON list, not a string or block of code. 
        Do not format as Markdown or enclose in backticks.
        Do NOT return the list as a string or enclose it in quotes or Markdown.

        Return your response **only** as a JSON list in this format:

        [
        {{
            "original_content": "<p>...</p>",
            "suggestion": "<p>...</p>"
        }},
        ...
        ]

        If there are **no suggestions**, return an **empty list**: [].
        '''
    

    client = instructor.from_anthropic(AnthropicBedrock())
    try: 
    # note that client.chat.completions.create will also work
        resp = client.messages.create(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens= 5000,
            messages=[
                {
                    "role": "user",
                    "content": input_message
                }
            ],
            response_model = List[ContentSuggestion],
            
        )
        # Check response type
        if not isinstance(resp, list):
                raise TypeError(f"Expected list, got {type(resp)}")
        
        #if the response is a list, check each item type for instance of ContentSuggestion
        else: 
            output = []
            for item in resp:
                if isinstance(item, ContentSuggestion): 
                    #if the item is an instance of ContentSuggestion, append it to the output list
                    output.append({
                                "original_content": item.original_content,
                                "suggestion": item.suggestion})
                else: 
                    raise TypeError("Invalid item type in response list.")
                
            return output
   
    except (ValidationError, InstructorRetryException, TypeError) as e:
        print(f"Error processing Claude response:{e} ")
        return []


        









