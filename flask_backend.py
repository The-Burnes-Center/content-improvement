from flask import Flask, request
from utils import *
from flask_cors import CORS
from web_design_structured_prompt import analyze_webdesign
from content_clarity_structured_prompt import anaylze_content_clarity
from appending_prompts_code_accessibility import chunk_html_script, threading_code_accessibility
from format_audience_page import audience_page_postives, audience_page_challenges
import json
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os
import concurrent.futures
import time



load_dotenv()

app = Flask(__name__)
CORS(app)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
mysql.init_app(app)


#############################

## Generative AI Endpoints ##

#############################

@app.route('/generate-sample-persona')
def generate_sample_persona():
    """
    GET /generate-sample-persona
    -----------------------------
    Generates a sample user persona based on the content and purpose of a given website.

    Query Parameters:
        url (str): The URL of the website to analyze.

    Behavior:
    - Retrieves the 'url' query parameter.
    - Uses a predictive model (`get_pred`) to generate a realistic user persona based on the site's content.
    - The persona includes key demographic and behavioral details:
        - Age, gender, occupation, income level, education level
        - Tech savviness
        - User needs or goals from the website
        - Challenges they may face while navigating the site

    Returns:
        str: A generated user persona as a text description.

    Error:
        - Returns HTTP 400 if no URL is provided.

    Notes:
        - Ensure that the predictive model used in `get_pred` has access to and properly interprets the content at the given URL.
        - Consider sanitizing and validating the URL for robustness.
    """
    url = request.args.get('url')
    # should format 
    if url:

        generate_user_persona = get_pred(url,
                    f"""Based on the url provided, please create one user persona of someone who would navigate the website. 
                        Include their age, gender, occupation, income level, education level, tech savviness, needs or end goals from the website, 
                        challenges they may have using the website.
                    

                        An example of a user persona and formatting is: 

                        Name: '  '
                        Age: ' '
                        Gender: '  '
                        Occupation:  ''
                        Income Level:  XX per year
                        Education Level: '   '
                        Tech Savviness: Beginner/ Moderate / Intermediate / Advance 

                        Example Goals and Needs: 

                        Goals and Needs: 
                        1. Register to vote in New Jersey
                        2. Check voter registration status
                        3. Find the polling place
                        4. Understand early voting options
                        5. Request and submit a mail-in ballot

                        Example Challenges Using the Website:

                        Challenges Using the Website: 
                        1. Navigating through multiple pages to find specific information
                        2. Understanding legal or technical terminology related to voting procedures
                        3. Locating and downloading necessary forms for voter registration or mail-in ballots
                        4. Identifying the most up-to-date information, especially if there are changes to voting procedures
                        5. Finding clear instructions on how to complete and submit various forms
                        6. Accessing mobile-friendly versions of the website while using her smartphone

                        Example Summary: 
                        X  wants to ensure they are properly registered and informed about the voting process in New Jersey. 
                        They are civic-minded and wants to participate in elections but may struggle with finding time to thoroughly research voting procedures. 
                        They would benefit from clear, concise information and easy-to-follow instructions on the website.

                                
                                 
                        """ )
        
        
        return generate_user_persona
    
    else: 
        return "No URL provided", 400
    
@app.route('/audience', methods=['POST', 'OPTIONS'])
def audience():
    """
    POST /audience
    ----------------
    Audits a website's content and design from the perspective of a specific user persona.

    Expected JSON payload:
    {
        "url": str,       # The URL of the website to audit
        "persona": str    # A description of the target user persona (e.g., "first-time voter", "elderly user")
        "personaAuditId": int # The ID of the persona audit to update
    }

    Behavior:
    - Extracts the 'url' and 'persona' from the request body.
    - Retrieves the raw source content of the webpage using `get_pure_source(url)`.
    - Uses a predictive model (`get_pred`) to generate a user-specific audit based on the provided persona.
    - Updates the PersonaAudit table in the database with the new persona and audit output.
    - Returns the generated audit commentary.

    Returns:
        str: AI-generated audit commentary tailored to the persona and website content.

    Error:
        - Returns HTTP 400 if either 'url' or 'persona' is missing from the request.

    Notes:
        - This endpoint assumes that `get_pred` handles prompt execution and returns a string response.
        - Consider validating the URL format and sanitizing persona input to avoid prompt injection.
    """
    if request.method == 'OPTIONS':
        return '', 204  # let preflight pass
    data = request.get_json()
    url = data.get('url')
    print(f" loading audience for: {url} ...")
    persona = data.get('persona')
    
    personaAuditId = data.get('personaAuditId')
    
    if url and persona:
        output = f" Postives:\n{audience_page_postives(url, persona)} \nUser Challenges:\n {audience_page_challenges(url, persona)}"
        #output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona}.""")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE PersonaAudit SET persona = %s, output = %s WHERE personaAuditId = %s", (persona, output, personaAuditId))
        conn.commit()
        cursor.close()
        conn.close()

        return output, 200
    else:
        return "No URL or persona provided", 400
    

@app.route('/content', methods=['POST', 'OPTIONS'])
def improveContent():
    """
    POST /content
    ----------------
    Analyzes the textual content of a webpage and provides suggestions to improve clarity based on predefined guidelines.

    Expected JSON payload:
    {
        "url": str,        # The URL of the webpage whose content should be analyzed
        "projectId": int   # The ID of the project associated with the audit
    }

    Behavior:
    - Scrapes and chunks text content from the provided URL.
    - Loads clarity guidelines from a local file ("contentclarityguide.txt").
    - Uses an AI model to analyze each section and generate clarity suggestions.
    - Saves the suggestions to the database, linked to a new ContentClarityAudit entry.

    Returns:
        - A list of clarity suggestions if a valid URL is provided.
        - 400 Bad Request error if the URL is missing.

    Notes:
        - The model responses include original content and an improved version.
        - Suggestions are stored in the ContentClaritySuggestion table, linked via a ContentClarityAudit ID.
        - Ensure scraping, AI model access, and DB connection are properly configured.
    """
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    url = data.get('url')
    projectId = data.get('projectId')

    if not url or not projectId:
        return "Missing 'url' or 'projectId'", 400
    
    print(f" loading content for: {url} ...")

    scrapped_data = chunk_html_text(url)
    content_guidelines = read_file_text("contentclarityguide.txt")

    suggestions = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_section = {
            executor.submit(anaylze_content_clarity, section, content_guidelines): section
            for section in scrapped_data
        }

        for future in concurrent.futures.as_completed(future_to_section):
            try:
                result = future.result()
                suggestions.extend(result)
            except Exception as e:
                print(f"Error processing a section: {e}")

    # Save to database
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ContentClarityAudit (projectId) VALUES (%s)", (projectId,))
    conn.commit()

    cursor.execute(
        "SELECT contentClarityAuditId FROM ContentClarityAudit WHERE projectId = %s ORDER BY contentClarityAuditId DESC LIMIT 1",
        (projectId,)
    )
    contentClarityAuditId = cursor.fetchone()[0]

    for item in suggestions:
        #print(item)
        original = item.get("original_content", "")
        revised = item.get("suggestion", "")
        cursor.execute(
            "INSERT INTO ContentClaritySuggestion (contentClarityAuditId, original, suggestion) VALUES (%s, %s, %s)",
            (contentClarityAuditId, original, revised)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return suggestions

@app.route('/webdesign', methods=['POST', 'OPTIONS'])
def webDesign():
    """
    POST /webdesign
    ----------------
    Analyzes the design of a webpage by capturing a screenshot and processing it with an AI model.

    Expected JSON payload:
    {
        "url": str  # The URL of the webpage whose content should be analyzed
        "projectId": int # The ID of the project associated with the audit
    }


    Behavior:
    - Retrieves the 'url' query parameter.
    - Captures a screenshot of the provided URL.
    - Uploads the screenshot to an S3 bucket.
    - Sends the image URL to an OpenAI model for analysis.
    - Extracts and cleans up the design feedback from the model output.
    - Saves the feedback to the database.
    - Returns the cleaned feedback as a JSON response.

    Returns:
        - A cleaned string containing web design feedback if a valid URL is provided.
        - 400 Bad Request error if the URL is missing.

    Notes:
        - The response format from OpenAI is expected to be in markdown-style code blocks (```json [...] ```), 
          and must be parsed by `webdesign_extract_text`.
        - Ensure S3 bucket configuration and OpenAI API credentials are properly set.
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()

    url = data.get('url')
    projectId = data.get('projectId')

    if projectId is None:
        print("Bad request: projectId missing")
        return "error projectId",  400

    if url:
        print(f"loading web design for {url}...")
        layout_guidelines = read_file_text("contentlayoutguide.txt")
        output = json.dumps(analyze_webdesign(url, layout_guidelines))
        output = json.loads(output)
        

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO WebDesignAudit (projectId) VALUES (%s)", (projectId,))
        conn.commit()
        cursor.close()
        conn.close()

        # Retrieve the ID of the newly created WebDesignAudit
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT webDesignAuditId FROM WebDesignAudit WHERE projectId = %s ORDER BY webDesignAuditId DESC LIMIT 1", (projectId,))
        webDesignAuditId = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        # Insert each suggestion into the WebDesignSuggestion table
        conn = mysql.connect()
        cursor = conn.cursor()
        for suggestion in output:
            area = suggestion["area"]
            suggestion_text = suggestion["suggestion"]
            reason = suggestion["reason"]
            cursor.execute(
            "INSERT INTO WebDesignSuggestion (webDesignAuditId, area, suggestion, reason) VALUES (%s, %s, %s, %s)",
            (webDesignAuditId, area, suggestion_text, reason)
            )
        conn.commit()
        cursor.close()
        conn.close()


        return output

    else:
        return "No URL provided", 400
    
    
@app.route('/accessibility', methods=['POST', 'OPTIONS'])
def codeAccessibility(): 
    """
    POST /accessibility
    --------------------
    Analyzes the accessibility of the webpage at the given URL and saves the output to the database.

    Expected JSON payload:
    {
        "url": str  # The URL of the webpage to be analyzed,
        "projectId": int # The ID of the project associated with the audit
    }

    Behavior:
    - Extracts the 'url' from the request JSON.
    - If a URL is provided, calls the `analyze_accessibility(url)` function and returns the results as JSON.
    - If no URL is provided, returns a 400 Bad Request response.
    - Inserts a new record into the AccessibilityAudit table in the database with the projectId.
    - Retrieves the ID of the newly created AccessibilityAudit.
    - Inserts each suggestion into the AccessibilitySuggestion table.
    - Returns the accessibility analysis results as JSON.

    Returns:
        - JSON containing accessibility analysis results if a valid URL is provided.
        - 400 Bad Request error message if the 'url' is missing.
    """
    if request.method == 'OPTIONS':
        return '', 204  # let preflight pass
    data = request.get_json()
    url = data.get('url')
    projectId = data.get('projectId')
    if url:
        print(f" loading code accessibility for: {url} ...")
        html_script = get_pure_source(url)
        chunked_script = chunk_html_script(html_script)
        suggestions = threading_code_accessibility(chunked_script)
        output = json.dumps(suggestions)
        output = json.loads(output)

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO AccessibilityAudit (projectId) VALUES (%s)", (projectId,))
        conn.commit()
        cursor.close()
        conn.close()

        # Retrieve the AccessibilityAudit with the highest ID for the given projectId
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT accessibilityAuditId FROM AccessibilityAudit WHERE projectId = %s ORDER BY accessibilityAuditId DESC LIMIT 1", (projectId,))
        accessibilityAuditId = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        # Insert each suggestion into the AccessibilitySuggestion table
        conn = mysql.connect()
        cursor = conn.cursor()
        for suggestion in output:
            #print(suggestion)
            label = suggestion["label"]
            original = suggestion["original_content"]
            revised = suggestion["revised_content"]
            explanation = suggestion["explanation"]
            cursor.execute(
                "INSERT INTO AccessibilitySuggestion (accessibilityAuditId, label, original, revised, explanation) VALUES (%s, %s, %s, %s, %s)",
                (accessibilityAuditId, label, original, revised, explanation)
            )
        conn.commit()
        cursor.close()
        conn.close()

        return output

    else: 
        return "No URL provided", 400



########################

## Database Endpoints ##

########################

@app.route('/add_project', methods=['POST'])
def add_project():
    """
    POST /add_project
    ------------------
    Adds a new project entry to the Project table in the database.

    Expected JSON payload:
    {
        "userId": int,   # ID of the user who owns the project
        "url": str,      # URL associated with the project
        "name": str      # Name of the project
    }

    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `userId`, `url`, and `name` fields.
    - Inserts the new project record into the Project table.
    - Returns a success message and HTTP status code 201 on successful insertion.

    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.

    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
        
    data = request.get_json()
    userId = data.get('userId')
    url = data.get('url')
    name = data.get('name')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Project (userId, url, name) VALUES (%s, %s, %s)", (userId, url, name))
    conn.commit()
    cursor.execute("SELECT * FROM Project WHERE projectId = LAST_INSERT_ID()")
    created_project = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"project": created_project}, 201

@app.route('/get_projects', methods=['GET'])
def get_projects():
    """
    GET /get_projects
    -----------------
    Retrieves all projects for a given userId from the Project table in the database.

    Query Parameters:
    - userId (int): The ID of the user to filter projects by.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch all records from the Project table for the given userId.
    - Returns the list of projects as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the list of projects and HTTP 200 status code.

    Note:
        This function assumes that the Project table exists and has valid data.
    """
    user_id = request.args.get('userId')
    if not user_id:
        return "No userId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Project WHERE userId = %s", (user_id,))
    projects = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"projects": projects}, 200

@app.route('/create_persona_audit', methods=['POST'])
def create_persona():
    """
    POST /create_persona_audit
    ---------------------
    Creates a new persona entry in the PersonaAudit table in the database.

    Expected JSON payload:
    {
        "name": str,
        "projectId": int,     
    }

    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `name` and `projectId` fields.
    - Inserts the new persona record into the PersonaAudit table.
    - Returns a success message and HTTP status code 201 on successful insertion.
    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.
    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    name = data.get('name')
    projectId = data.get('projectId')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PersonaAudit (name, projectId) VALUES (%s, %s)", (name, projectId))

    conn.commit()
    new_id = cursor.lastrowid
    
    cursor.close()
    conn.close()

    return {"id": new_id }, 201


@app.route('/get_personas', methods=['GET'])
def get_personas():
    """
    GET /get_personas
    -----------------
    Retrieves all personas for a given projectId from the PersonaAudit table in the database.

    Query Parameters:
    - projectId (int): The ID of the user to filter personas by.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch all records from the PersonaAudit table for the given projectId.
    - Returns the list of personas as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the list of personas and HTTP 200 status code.

    Note:
        This function assumes that the PersonaAudit table exists and has valid data.
    """
    projectId = request.args.get('projectId')
    if not projectId:
        return "No userId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PersonaAudit WHERE projectId = %s", (projectId,))
    personas = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"personas": personas}, 200

@app.route('/update_persona_audit', methods=['POST'])
def update_persona_audit():
    """
    POST /update_persona_audit
    ----------------------
    Updates an existing persona entry in the PersonaAudit table in the database.
    Expected JSON payload:
    {
        "personaAuditId": int, 
        "persona": str,      
        "output": str,       
    }

    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `personaAuditId`, `persona`, and `output` fields.
    - Updates the existing persona record in the PersonaAudit table.
    - Returns a success message and HTTP status code 200 on successful update.

    Returns:
        Tuple[str, int]: A success message and HTTP 200 status code if update is successful.
    Note:

        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    personaAuditId = data.get('personaAuditId')
    persona = data.get('persona')
    output = data.get('output')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE PersonaAudit SET persona = %s, output = %s WHERE personaAuditId = %s", (persona, output, personaAuditId))
    conn.commit()
    cursor.close()
    conn.close()

    return "Persona updated successfully", 200

@app.route('/create_webdesign_audit', methods=['POST'])
def create_webdesign_audit():
    """
    POST /create_webdesign_audit
    ----------------------
    Creates a new web design audit entry in the WebDesignAudit table in the database.

    Expected JSON payload:
    {
        "projectId": int,     
    }
    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `projectId` field.
    - Inserts the new web design audit record into the WebDesignAudit table.
    - Returns a success message and HTTP status code 201 on successful insertion.
    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.
    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    projectId = data.get('projectId')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO WebDesignAudit (projectId) VALUES (%s)", (projectId,))
    conn.commit()
    cursor.close()
    conn.close()

    return "Web design audit created successfully", 201

@app.route('/get_webdesign_audit', methods=['GET'])
def get_webdesign_audit():
    """
    GET /get_webdesign_audit
    -----------------
    Retrieves the web design audit associated with a given projectId from the WebDesignAudit table in the database.

    Query Parameters:
    - projectId (int): The ID of the project to retrieve the web design audit for.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch the record from the WebDesignAudit table for the given projectId.
    - Returns the web design audit as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the web design audit and HTTP 200 status code.

    Note:
        This function assumes that the WebDesignAudit table exists and has valid data.
    """
    
    project_id = request.args.get('projectId')
    if not project_id:
        return "No projectId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM WebDesignAudit WHERE projectId = %s", (project_id,))
    web_design_audit = cursor.fetchone()
    cursor.close()
    conn.close()

    if not web_design_audit:
        return "No web design audit found for the given projectId", 404

    return {"web_design_audit": web_design_audit}, 200

@app.route('/create-web-design-suggestion', methods=['POST'])
def create_web_design_suggestion():
    """
    POST /create-web-design-suggestion
    ----------------------
    Creates a new web design suggestion entry in the WebDesignSuggestion table in the database.

    Expected JSON payload:
    {
        "webDesignAuditId": int, 
        "area": str,      
        "suggestion": str,   
        "reason": str
    }

    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `webDesignAuditId`, `area`, `suggestion`, and `reason` fields.
    - Inserts the new web design suggestion record into the WebDesignSuggestion table.
    - Returns a success message and HTTP status code 201 on successful insertion.

    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.

    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    webDesignAuditId = data.get('webDesignAuditId')
    area = data.get('area')
    suggestion = data.get('suggestion')
    reason = data.get('reason')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO WebDesignSuggestion (webDesignAuditId, area, suggestion, reason) VALUES (%s, %s, %s, %s)", (webDesignAuditId, area, suggestion, reason))
    conn.commit()
    cursor.close()
    conn.close()

    return "Web design suggestion created successfully", 201

@app.route('/get_webdesign_suggestions', methods=['GET'])
def get_webdesign_suggestions():
    """
    GET /get_webdesign_suggestions
    -----------------
    Retrieves all web design suggestions associated with a given webDesignAuditId from the WebDesignSuggestion table in the database.

    Query Parameters:
    - webDesignAuditId (int): The ID of the web design audit to retrieve suggestions for.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch all records from the WebDesignSuggestion table for the given webDesignAuditId.
    - Returns the list of suggestions as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the list of suggestions and HTTP 200 status code.

    Note:
        This function assumes that the WebDesignSuggestion table exists and has valid data.
    """
    web_design_audit_id = request.args.get('webDesignAuditId')
    if not web_design_audit_id:
        return "No webDesignAuditId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM WebDesignSuggestion WHERE webDesignAuditId = %s", (web_design_audit_id,))
    suggestions = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"suggestions": suggestions}, 200
    
@app.route('/create_accessibility_audit', methods=['POST'])
def create_accessibility_audit():
    """
    POST /create_accessibility_audit
    ----------------------
    Creates a new accessibility audit entry in the AccessibilityAudit table in the database.

    Expected JSON payload:
    {
        "projectId": int,
    }

    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `projectId` field.
    - Inserts the new accessibility audit record into the AccessibilityAudit table.
    - Returns a success message and HTTP status code 201 on successful insertion.

    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.

    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    projectId = data.get('projectId')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO AccessibilityAudit (projectId) VALUES (%s)", (projectId,))
    conn.commit()
    cursor.close()
    conn.close()

    return "Accessibility audit created successfully", 201

@app.route('/get_accessibility_audit', methods=['GET'])
def get_accessibility_audit():
    """
    GET /get_accessibility_audit
    -----------------
    Retrieves the accessibility audit associated with a given projectId from the AccessibilityAudit table in the database.

    Query Parameters:
    - projectId (int): The ID of the project to retrieve the accessibility audit for.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch the record from the AccessibilityAudit table for the given projectId.
    - Returns the accessibility audit as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the accessibility audit and HTTP 200 status code.

    Note:
        This function assumes that the AccessibilityAudit table exists and has valid data.
    """
    
    project_id = request.args.get('projectId')
    if not project_id:
        return "No projectId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AccessibilityAudit WHERE projectId = %s ORDER BY accessibilityAuditId DESC LIMIT 1", (project_id,))
    accessibility_audit = cursor.fetchone()
    cursor.close()
    conn.close()

    if not accessibility_audit:
        return "No accessibility audit found for the given projectId", 404

    return {"accessibility_audit": accessibility_audit}, 200

@app.route('/create_accessibility_suggestion', methods=['POST'])
def create_accessibility_suggestion():
    """
    POST /create_accessibility_suggestion
    ----------------------
    Creates a new accessibility suggestion entry in the AccessibilitySuggestion table in the database.

    Expected JSON payload:
    {
        "accessibilityAuditId": int,  
        "label": str,   
        "original": str,
        "revised": str,
        "explination": str
    }
    
    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `accessibilityAuditId`, `label`, `original`, `revised`, and `explination` fields.
    - Inserts the new accessibility suggestion record into the AccessibilitySuggestion table.
    - Returns a success message and HTTP status code 201 on successful insertion.

    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.

    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    accessibilityAuditId = data.get('accessibilityAuditId')
    label = data.get('label')
    original = data.get('original')
    revised = data.get('revised')
    explanation = data.get('explination')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO AccessibilitySuggestion (accessibilityAuditId, label, original, revised, explanation) VALUES (%s, %s, %s, %s, %s)", (accessibilityAuditId, label, original, revised, explanation))
    conn.commit()
    cursor.close()
    conn.close()

    return "Accessibility suggestion created successfully", 201


@app.route('/get_accessibility_suggestions', methods=['GET'])
def get_accessibility_suggestions():
    """
    GET /get_accessibility_suggestions
    -----------------
    Retrieves all accessibility suggestions associated with a given accessibilityAuditId from the AccessibilitySuggestion table in the database.

    Query Parameters:
    - accessibilityAuditId (int): The ID of the accessibility audit to retrieve suggestions for.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch all records from the AccessibilitySuggestion table for the given accessibilityAuditId.
    - Returns the list of suggestions as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the list of suggestions and HTTP 200 status code.

    Note:
        This function assumes that the AccessibilitySuggestion table exists and has valid data.
    """
    accessibility_audit_id = request.args.get('accessibilityAuditId')
    if not accessibility_audit_id:
        return "No accessibilityAuditId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AccessibilitySuggestion WHERE accessibilityAuditId = %s", (accessibility_audit_id,))
    suggestions = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"suggestions": suggestions}, 200

@app.route('/create_content_clairity_audit', methods=['POST'])
def create_content_clairity_audit():
    """
    POST /create_content_clairity_audit
    ----------------------
    Creates a new content clarity audit entry in the ContentClarityAudit table in the database.

    Expected JSON payload:
    {
        "projectId": int,
    }
    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `projectId` field.
    - Inserts the new content clarity audit record into the ContentClarityAudit table.
    - Returns a success message and HTTP status code 201 on successful insertion.
    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.
    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    projectId = data.get('projectId')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ContentClarityAudit (projectId) VALUES (%s)", (projectId,))
    conn.commit()
    cursor.close()
    conn.close()

    return "Content clarity audit created successfully", 201

@app.route('/get_content_clarity_audit', methods=['GET'])
def get_content_clarity_audit():
    """
    GET /get_content_clarity_audit
    -----------------
    Retrieves the content clarity audit associated with a given projectId from the ContentClarityAudit table in the database.

    Query Parameters:
    - projectId (int): The ID of the project to retrieve the content clarity audit for.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch the record from the ContentClarityAudit table for the given projectId.
    - Returns the content clarity audit as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the content clarity audit and HTTP 200 status code."""
    project_id = request.args.get('projectId')
    if not project_id:
        return "No projectId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ContentClarityAudit WHERE projectId = %s", (project_id,))
    content_clarity_audit = cursor.fetchone()
    cursor.close()
    conn.close()

    if not content_clarity_audit:
        return "No content clarity audit found for the given projectId", 404

    return {"content_clarity_audit": content_clarity_audit}, 200

@app.route('/create_content_clarity_suggestion', methods=['POST'])
def create_content_clarity_suggestion():
    """
    POST /create_content_clarity_suggestion
    ----------------------
    Creates a new content clarity suggestion entry in the ContentClaritySuggestion table in the database.
    Expected JSON payload:
    {
        "contentClarityAuditId": int,  
        "original": str,   
        "suggestion": str
    }

    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `contentClarityAuditId`, `original`, and `suggestion` fields.
    - Inserts the new content clarity suggestion record into the ContentClaritySuggestion table.
    - Returns a success message and HTTP status code 201 on successful insertion.

    Returns:
        Tuple[str, int]: A success message and HTTP 201 status code if insertion is successful.

    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    contentClarityAuditId = data.get('contentClarityAuditId')
    original = data.get('original')
    suggestion = data.get('suggestion')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ContentClaritySuggestion (contentClarityAuditId, original, suggestion) VALUES (%s, %s, %s)", (contentClarityAuditId, original, suggestion))
    conn.commit()
    cursor.close()
    conn.close()

    return "Content clarity suggestion created successfully", 201

@app.route('/get_content_clarity_suggestions', methods=['GET'])
def get_content_clarity_suggestions():
    """
    GET /get_content_clarity_suggestions
    -----------------
    Retrieves all content clarity suggestions associated with a given contentClarityAuditId from the ContentClaritySuggestion table in the database.
    Query Parameters:
    - contentClarityAuditId (int): The ID of the content clarity audit to retrieve suggestions for.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch all records from the ContentClaritySuggestion table for the given contentClarityAuditId.
    - Returns the list of suggestions as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the list of suggestions and HTTP 200 status code.

    Note:
        This function assumes that the ContentClaritySuggestion table exists and has valid data.
    """
    content_clarity_audit_id = request.args.get('contentClarityAuditId')
    if not content_clarity_audit_id:
        return "No contentClarityAuditId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ContentClaritySuggestion WHERE contentClarityAuditId = %s", (content_clarity_audit_id,))
    suggestions = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"suggestions": suggestions}, 200

@app.route('/delete_project', methods=['DELETE'])
def delete_project():
    """
    DELETE /delete_project
    ----------------------
    Deletes a project entry from the Project table in the database.

    Expected JSON payload:
    {
        "projectId": int
    }
    Behavior:
    - Parses the incoming JSON payload from the request body.
    - Extracts `projectId` field.
    - Deletes the project record from the Project table.
    - Returns a success message and HTTP status code 200 on successful deletion.
    Returns:
        Tuple[str, int]: A success message and HTTP 200 status code if deletion is successful.
    Note:
        This function assumes valid input and does not currently handle errors or validation.
    """
    data = request.get_json()
    projectId = data.get('projectId')

    conn = mysql.connect()
    cursor = conn.cursor()

    # Delete ContentClaritySuggestion and ContentClarityAudit associated with this project
    cursor.execute("SELECT contentClarityAuditId FROM ContentClarityAudit WHERE projectId = %s", (projectId,))
    content_clarity_audits = cursor.fetchall()
    for audit in content_clarity_audits:
        contentClarityAuditId = audit[0]
        cursor.execute("DELETE FROM ContentClaritySuggestion WHERE contentClarityAuditId = %s", (contentClarityAuditId,))
    cursor.execute("DELETE FROM ContentClarityAudit WHERE projectId = %s", (projectId,))

    # Delete WebDesignSuggestion and WebDesignAudit associated with this project
    cursor.execute("SELECT webDesignAuditId FROM WebDesignAudit WHERE projectId = %s", (projectId,))
    web_design_audits = cursor.fetchall()
    for audit in web_design_audits:
        webDesignAuditId = audit[0]
        cursor.execute("DELETE FROM WebDesignSuggestion WHERE webDesignAuditId = %s", (webDesignAuditId,))
    cursor.execute("DELETE FROM WebDesignAudit WHERE projectId = %s", (projectId,))

    # Delete AccessibilitySuggestion and AccessibilityAudit associated with this project
    cursor.execute("SELECT accessibilityAuditId FROM AccessibilityAudit WHERE projectId = %s", (projectId,))
    accessibility_audits = cursor.fetchall()
    for audit in accessibility_audits:
        accessibilityAuditId = audit[0]
        cursor.execute("DELETE FROM AccessibilitySuggestion WHERE accessibilityAuditId = %s", (accessibilityAuditId,))
    cursor.execute("DELETE FROM AccessibilityAudit WHERE projectId = %s", (projectId,))

    # Delete PersonaAudit associated with this project
    cursor.execute("DELETE FROM PersonaAudit WHERE projectId = %s", (projectId,))
    
    cursor.execute("DELETE FROM Project WHERE projectId = %s", (projectId,))
    conn.commit()
    cursor.close()
    conn.close()

    return "Project deleted successfully", 200