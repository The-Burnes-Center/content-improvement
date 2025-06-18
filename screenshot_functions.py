import requests
import uuid
import os

from constants import SCREENSHOTAPI_API_KEY

def screenshotapinet(url: str, output_dir: str = "/tmp") -> str:
    """
    Takes a screenshot of the given URL using ScreenshotOne API and saves it locally.

    Args:
        url (str): The URL to capture.
        output_dir (str): Directory to save the screenshot. Defaults to '/tmp' (Lambda compatible).

    Returns:
        str: Full file path to the saved screenshot.
    """
    
    response = requests.get(
        "https://shot.screenshotapi.net/screenshot",
        params={
            "token": SCREENSHOTAPI_API_KEY,
            "url": url,
            "output": "image",
            "file_type": "png",
        }
        )

    if response.status_code != 200:
        raise Exception(f"Screenshot API failed: {response.status_code}, {response.text}")

    # Save the image
    file_id = str(uuid.uuid4())
    file_path = os.path.join(output_dir, f"screenshot_{file_id}.png")
    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path




