import instructor
from anthropic import AnthropicBedrock
from pydantic import BaseModel, Field 
from utils import * 
from typing import List


class ContentSuggestion(BaseModel):
    #key: int = Field(..., description = "A unique identifier for this suggestion item." )
    original_content: str = Field(..., description="The original text that does not meet content clarity standards." )
    suggestion: str = Field(..., description="The revised text that meets content clarity standards." )
    

def anaylze_content_clarity(section, content_guidlines):
    # client = instructor.from_anthropic(AnthropicBedrock())
   
    input_message = f'''{section}, Provide suggestions for improving the clarity of the provided website text to align with {content_guidlines}. Cite specific examples of text that could be improved. Cite every single instance of text that could be improved that you find. Show the original and provide a revised version. 
    Do not include any text and only include necessary feedback. The maximum amount is 5 sugesstions.Please' use the format and return a JSON list: 
        [    
        {{
            "original_content": "<p>text</p>",
            "suggestion": "<p>text</p>"
        }}
        ] 
        '''
    client = instructor.from_anthropic(AnthropicBedrock())
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

   
    output = []

    for item in resp:
        assert isinstance(item, ContentSuggestion)
     
        output.append({
                        #"key": item.key,
                        "original_content": item.original_content,
                        "suggestion": item.suggestion})
        
    #print(output)

    return output







