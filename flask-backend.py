from flask import Flask, request
from utils import *
from flask_cors import CORS
from accessibilityStructuredPrompt import analyze_accessibility
from webDesignStructuredPrompt import analyze_webdesign
import json

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

#is this also a POST request?
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
    

@app.route('/audience', methods=['POST', 'OPTIONS'])
def audience():
    if request.method == 'OPTIONS':
        return '', 204  # let preflight pass

    data = request.get_json()
    url = data.get('url')
    persona = data.get('persona')
    if url and persona:
        return get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona}.""")
    else:
        return "No URL or persona provided", 400
    

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

@app.route('/webdesign', methods=['POST','OPTIONS'])
def webDesign():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    url = data.get('url')
    if url:
        print(url)
        return json.dumps(analyze_webdesign(url))

    else:
        return "No URL provided", 400
    
@app.route('/accessibility', methods=['POST','OPTIONS'])
def codeAccessibility():  
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    url = data.get('url')
    if url:
        print(url)
        return json.dumps(analyze_accessibility(url))
    
    else: 
        return "No URL provided", 400
        


