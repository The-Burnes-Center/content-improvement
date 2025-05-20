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
    input_message = f'''You are a strict accessibility reviewer analyzing the following HTML: {get_pure_source(url)} 
        Your task is to identify **only real** accessibility issues based on WCAG 2.1 AA guidelines. 
        Do **not** invent problems. 
        Only include suggestions when an issue is present in the exact HTML. Cite every single instance of HTML. 
        Include the original version and provide a revised version of the HTML.
        For each suggestion, provide a brief explanation of why this change improves accessibility, ideally referencing WCAG principles.

        If something is already accessible, DO NOT INLCUDE IT. If it is already accessible, say nothing about it.


        Respond **only** in the following JSON array format. Each object should include:
        [{{
                    key: '1',
                    label: 'This is panel header 1',
                    original_content: <p>text</p>, 
                    revised_content: <p>text</p>,
                    explanation: <p>text</p> }}
                    ]


        If there are **no issues**, return an **empty list**: [].
        Do not inlcude correct original HTML where there is no issue. 
        For example DO NOT include the following:

        [{{'key': index, 
        'label': 'Missing language attribute',
        'original_content': '<html lang="en">', 
        'revised_content': '<html lang="en">', 
        'explanation': 'The HTML tag already includes the lang attribute, which is correct. 
         This helps screen readers determine the language of the page content, meeting WCAG 2.1 guideline 3.1.1 (Language of Page).'}}]


        Do not include any additional text or explanations outside of the JSON format.
        
        The key should be a unique identifier for each suggestion, starting from 1 and incrementing by 1 for each subsequent suggestion.
        For the label of the issue, use a short description of the accessibility issue and ensure that it matches the explaination of issue. 
        The original_content is the exact HTML that does not meet WCAG 2.1 AA standards. 
        The revised_content is a revision of the HTML content that improves accessibility compliance. 
        The explanation should be a brief description of why this change improves accessibility, ideally referencing WCAG principles.

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
        response_model = List[AccessibilitySuggestion],
        
    )

    output = []


    for item in resp:
        if isinstance(item, AccessibilitySuggestion): 
            output.append({"key": item.key,
                            "label": item.label,
                            "original_content": item.original_content,
                            "revised_content": item.revised_content,
                            "explanation": item.explanation})

    return output