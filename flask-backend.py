from flask import Flask, request
from utils import *
from flask_cors import CORS
from accessibilityStructuredPrompt import analyze_accessibility
import json

app = Flask(__name__)
CORS(app)

@app.route('/generate-sample-persona')
def generate_sample_persona():
    url = request.args.get('url')
    # should format 
    if url:
        generate_user_persona = get_pred(url,f"""Based on the url provided, please create one user persona of someone who would navigate the website. 
                                     Include their age, gender, occupation, income level, education level, tech savviness, needs or end goals from the website, 
                                     challenges they may have using the website.""" )
        
        return generate_user_persona
    
    else: 
        return "No URL provided", 400
    
@app.route('/audience', methods=['POST'])
def audience():
    data = request.get_json()
    url = data.get('url')
    persona = data.get('persona')
    if url and persona:
        return get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona}.""")
    else:
        return "No URL or persona provided", 400
    

@app.route('/content', methods=['POST'])
def improveContent():
    data = request.get_json()
    url = data.get('url')
    if url:
        scrapped_data = get_text_chunks(url)

        content_guidlines = read_file_text("contentclarityguide.txt")

        suggestions = []

        for section in scrapped_data:
            suggestions.append(get_pred(section, f"Provide suggestions for improving the clarity of the provided website text to align with {content_guidlines}. Cite specific examples of text that could be improved. Cite every single instance of text that could be improved that you find. Show the original and provide a revised version. "))
        
        output = {"oringalText": scrapped_data, "suggestions": suggestions}

        return output
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
    
@app.route('/accessibility', methods=['POST'])
def codeAccessibility(): 
    data = request.get_json()
    url = data.get('url')
    if url:
        print(url)
        return json.dumps(analyze_accessibility(url))

    else: 
        return "No URL provided", 400
        
        
    


