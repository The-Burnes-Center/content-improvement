from flask import Flask, request
from utils import *
from flask_cors import CORS
from accessibilityStructuredPrompt import analyze_accessibility
from webDesignStructuredPrompt import analyze_webdesign
import json
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os

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
        generate_user_persona = get_pred(url,f"""Based on the url provided, please create one user persona of someone who would navigate the website. 
                                     Include their age, gender, occupation, income level, education level, tech savviness, needs or end goals from the website, 
                                     challenges they may have using the website.""" )
        
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
    persona = data.get('persona')
    personaAuditId = data.get('personaAuditId')
    if url and persona:
        output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona}.""")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE PersonaAudit SET persona = %s, output = %s WHERE personaAuditId = %s", (persona, output, personaAuditId))
        conn.commit()
        cursor.close()
        conn.close()

        return output
    else:
        return "No URL or persona provided", 400
    

@app.route('/content', methods=['POST', 'OPTIONS'])
def improveContent():
    """
    POST /content
    ----------------
    Analyzes and improves the clarity of webpage content based on predefined guidelines.

    Expected JSON payload:
    {
        "url": str  # The URL of the webpage whose content should be analyzed
    }

    Behavior:
    - Extracts the 'url' from the request body.
    - Scrapes and chunks text content from the provided URL.
    - Loads content clarity guidelines from a local file ("contentclarityguide.txt").
    - For each content section, uses a predictive model to generate suggestions for clarity improvements.
    - Each suggestion includes specific original text and a revised version.

    Returns:
        dict:
        {
            "oringalText": List[str],    # List of scraped content sections
            "suggestions": List[str]     # List of improvement suggestions per section
        }

    Error:
        - Returns HTTP 400 if the URL is missing from the request.

    Notes:
        - Suggestions are generated by the `get_pred` function using a prompt informed by the loaded content guidelines.
        - Consider adding validation for the URL and exception handling for scraping/model failures.
    """
    if request.method == 'OPTIONS':
        return '', 204  # let preflight pass
    data = request.get_json()
    url = data.get('url')
    if url:
        scrapped_data = get_text_chunks(url)

        content_guidlines = read_file_text("contentclarityguide.txt")

        suggestions = []

        for section in scrapped_data:
            suggestions.append(get_pred(section, f"Provide suggestions for improving the clarity of the provided website text to align with {content_guidlines}. Cite specific examples of text that could be improved. Cite every single instance of text that could be improved that you find. Show the original and provide a revised version. "))
        
        output = {"originalText": scrapped_data, "suggestions": suggestions}

        return output
    else:
        return "No URL provided", 400

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
    if url:
        print(url)
        output = json.dumps(analyze_webdesign(url))
        output = json.loads(output)
        print(output)

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO WebDesignAudit (projectId) VALUES (%s)", (projectId,))
        conn.commit()
        cursor.close()
        conn.close()

        # Retrieve the ID of the newly created WebDesignAudit
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
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
    Analyzes the accessibility of the webpage at the given URL.

    Expected JSON payload:
    {
        "url": str  # The URL of the webpage to be analyzed
    }

    Behavior:
    - Extracts the 'url' from the request JSON.
    - If a URL is provided, calls the `analyze_accessibility(url)` function and returns the results as JSON.
    - If no URL is provided, returns a 400 Bad Request response.

    Returns:
        - JSON containing accessibility analysis results if a valid URL is provided.
        - 400 Bad Request error message if the 'url' is missing.
    """
    if request.method == 'OPTIONS':
        return '', 204  # let preflight pass
    data = request.get_json()
    url = data.get('url')
    if url:
        print(url)
        return json.dumps(analyze_accessibility(url))

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
    cursor.close()
    conn.close()

    return "Project added successfully", 201

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
    cursor.close()
    conn.close()

    return "Persona created successfully", 201


@app.route('/get_personas', methods=['GET'])
def get_personas():
    """
    GET /get_personas
    -----------------
    Retrieves all personas for a given projectId from the PersonaAudit table in the database.

    Query Parameters:
    - projectId (int): The ID of the project to filter personas by.

    Behavior:
    - Connects to the MySQL database.
    - Executes a SELECT query to fetch all records from the PersonaAudit table for the given projectId.
    - Returns the list of personas as a JSON response.

    Returns:
        Tuple[dict, int]: A JSON object containing the list of personas and HTTP 200 status code.

    Note:
        This function assumes that the PersonaAudit table exists and has valid data.
    """
    project_id = request.args.get('projectId')
    if not project_id:
        return "No projectId provided", 400

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PersonaAudit WHERE projectId = %s", (project_id,))
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
    cursor.execute("SELECT * FROM AccessibilityAudit WHERE projectId = %s", (project_id,))
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