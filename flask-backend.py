from flask import Flask, request
from utils import *

app = Flask(__name__)

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
    