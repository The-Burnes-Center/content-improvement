import instructor
from pydantic import BaseModel, Field 
from utils import * 
from typing import List

url1 = 'https://www.nj.gov/state/elections/vote.shtml'
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = instructor.from_openai(openai_client)

class WebSuggestion(BaseModel):
    key: int = Field(..., description = "A unique identifier for this suggestion item." )
    area: str = Field(...,description="A short, descriptive label for the area the suggestion applies to (e.g., 'Homepage').")
    suggestion: str = Field(...,description="A specific suggestion for improving the web design, such as 'Add a clear call-to-action button'.")
    reason: str = Field(...,description="A brief explanation of why this suggestion is important, such as 'Improves user engagement and guides users to key content.'")
    

def analyze_webdesign(url): 
    layout = read_file_text("contentlayoutguide.txt")

    input_message = f"""Analyze this webpage screenshot and provide improvements for the layout of the page based off of the following guidelines: {layout}. \
                For each suggestion, provide an example of a part of the site that could be improved. Also cite specific guidelines in each suggestion. \
                If you cannot provide a specific element on the webpage as an example, do not include the suggestion. Do not include additional text and 
                Format the output in JSON, using the following structure:
                  [{{
                            key: '1',
                            area: 'Homepage',
                            suggestion: 'Add a clear call-to-action button',
                            reason: 'Improves user engagement and guides users to key content.',
                        }},"""
    
    screenshot_path = capture_screenshot(url)
    s3_url = upload_to_s3(screenshot_path, S3_BUCKET_NAME)

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            #if I wanted to add text guidlines, would i edit this or input text
            {"role": "system", "content": "You are an AI expert in web accessibility. Analyze the image and provide WCAG-compliant suggestions."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": input_message},
                    {"type": "image_url", "image_url": {"url": s3_url}}
                    #{"type": "text", "text": input_text2}
                ],
            },
        ], 
        response_model = List[WebSuggestion],
    )

    print()
    output = []


    for item in resp:
        assert isinstance(item, WebSuggestion)
        # print(f"Key: {item.key}")
        # print(f"Area: {item.area}")
        # print(f"Suggestion: {item.suggestion}")
        # print(f"Reason: {item.reason}")
        # print()
        output.append({"key": item.key,
                        "area": item.area,
                        "suggestion": item.suggestion,
                        "reason": item.reason})

    return output

    

    