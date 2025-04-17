from flask import Flask, request
from utils import *

app = Flask(__name__)


@app.route('/audience')
def Audience():
    pass

@app.route('/content')
def improveContent():
    url = request.args.get('url')
    if url:
        scrapped_data = get_text_chunks(url)

        content_guidlines = read_file_text("contentclarityguide.txt")

        suggestions = []

        for section in scrapped_data:
            suggestions.append(get_pred(section, f"Provide suggestions for improving the clarity of the provided website text to align with {content_guidlines}. Cite specific examples of text that could be improved. Cite every single instance of text that could be improved that you find. Show the original and provide a revised version. "))
        
        return suggestions

    else:
        return "No URL provided", 400

@app.route('/webdesign')
def webDesign():
    url = request.args.get('url')
    if url:
        #create screenshot 
        screenshot_path = capture_screenshot(url)
       
        #upload screenshot to S3 bucket 
        s3_url = upload_to_s3(screenshot_path, S3_BUCKET_NAME)
        
        #process image with open AI
        result = process_image_with_openai(s3_url)

        #result is format  ```json [...] ``` need to do testing 
        clean_webdesign_text= webdesign_extract_text(result)

        return clean_webdesign_text
    else:
        return "No URL provided", 400
    
@app.route('/accessability')
def codeAccessibility(): 

    url = request.args.get('url')
    if url:
        accessibility = get_pred(get_pure_source(url), f"""Provide suggestions for improving the provided HTML to align with WCAG 2.1 AA standards. Cite specific examples of HTML that could be improved. Cite every single instance of HTML that could be improved that you find. Show the original and provide a revised version. 
            Do not include any text. Please format as: 
             const items: CollapseProps['items'] = [
            {{
                key: '1',
                label: 'This is panel header 1',
                original content: <p>text</p>,
                revised content: <p>text</p>,
                explanation: <p>text</p>,
            }},
            {{
                key: '2',
                label: 'This is panel header 2',
                original content: <p>text</p>,
                revised content: <p>text</p>,
                explanation: <p>text</p>,
            }},
            {{
                key: '3',
                label: 'This is panel header 3',
                original content: <p>text</p>,
                revised content: <p>text</p>,
                explanation: <p>text</p>,
            }},
        ];"""
    ) 
        return accessibility


    else: 
        return "No URL provided", 400
        
        
    


