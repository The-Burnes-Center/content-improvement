import instructor
from anthropic import AnthropicBedrock
from pydantic import BaseModel, Field 
from utils import * 
from typing import List

url1 = 'https://www.nj.gov/state/elections/vote.shtml'

class AccessibilitySuggestion(BaseModel):
    key: int = Field(..., description = "A unique identifier for this suggestion item." )
    label: str = Field(...,description="A short, descriptive label for the type of accessibility issue (e.g., 'Missing alt text').")
    original_content: str = Field(..., description="The original HTML content that does not meet WCAG 2.1 AA standards." )
    revised_content: str = Field(...,description="The suggested revision of the HTML content that improves accessibility compliance.")
    explanation: str = Field(...,description="A brief explanation of why this change improves accessibility, ideally referencing WCAG principles.")

# function and expose it 
# chang to sonnet 

#print(get_pure_source(url))
def analyze_accessibility(url): #add format to prompt 
    input_message = f'''{get_pure_source(url)}, Provide suggestions for improving the provided HTML to align with WCAG 2.1 AA standards. Cite specific examples of HTML that could be improved. Cite every single instance of HTML that could be improved that you find. Show the original and provide a revised version. 
                Do not include any text. Please' use the format: 
                [{{
                    key: '1',
                    label: 'This is panel header 1',
                    original_content: <p>text</p>,
                    revised_content: <p>text</p>,
                    explanation: <p>text</p> }}
                    ] '''



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
        response_model = List[AccessibilitySuggestion],
        #response_model = AccessibilitySuggestion,
    )

    output = []


    for item in resp:
        assert isinstance(item, AccessibilitySuggestion)
        # print(f"Key: {item.key}")
        # print(f"Label: {item.label}")
        # print(f"Original Content: {item.original_content}")
        # print(f"Revised Content: {item.revised_content}")
        # print(f"Explanation: {item.explanation}")
        # print()
        output.append({"key": item.key,
                        "label": item.label,
                        "original_content": item.original_content,
                        "revised_content": item.revised_content,
                        "explanation": item.explanation})

    return output