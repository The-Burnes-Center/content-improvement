# from playwright.sync_api import sync_playwright

# def capture_screenshot(url, filepath="screenshot.png"):
#     with sync_playwright() as p:
#         browser = p.chromium.launch()
#         page = browser.new_page()
#         page.goto(url)
#         page.screenshot(path=filepath, full_page=True)
#         browser.close()

# if __name__ == '__main__':
#     capture_screenshot("https://www.nj.gov/state/elections/vote.shtml")

from playwright.sync_api import sync_playwright
from flask import Flask, send_file
import io

app = Flask(__name__)

def capture_screenshot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        img_bytes = io.BytesIO()
        page.screenshot(path=img_bytes, full_page=True)
        browser.close()
        img_bytes.seek(0)
        return img_bytes

@app.route('/screenshot')
def serve_screenshot():
    url = "https://www.nj.gov/state/elections/vote.shtml"
    screenshot_bytes = capture_screenshot(url)
    return send_file(screenshot_bytes, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)