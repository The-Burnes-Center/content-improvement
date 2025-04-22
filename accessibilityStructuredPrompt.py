import instructor
from anthropic import AnthropicBedrock
from pydantic import BaseModel
from utils import * 
from typing import List

url = 'https://www.nj.gov/state/elections/vote.shtml'

#print(get_pure_source(url))

#add format to prompt 
input_message = f'''{get_pure_source(url)}, Provide suggestions for improving the provided HTML to align with WCAG 2.1 AA standards. Cite specific examples of HTML that could be improved. Cite every single instance of HTML that could be improved that you find. Show the original and provide a revised version. 
            Do not include any text. Please' use the format: 
            {{
                key: '1',
                label: 'This is panel header 1',
                original content: <p>text</p>,
                revised content: <p>text</p>,
                explanation: <p>text</p> }}'''

class AccessibilitySuggestion(BaseModel):
    key: int
    label: str
    original_content: str
    revised_content: str
    explanation: str

client = instructor.from_anthropic(AnthropicBedrock())

# note that client.chat.completions.create will also work
resp = client.messages.create(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    max_tokens= 2048,
    messages=[
        {
            "role": "user",
            "content": input_message
        }
    ],
    response_model = List[AccessibilitySuggestion],
    #response_model = AccessibilitySuggestion,
)

#assert isinstance(resp, AccessibilitySuggestion)

print(resp)








