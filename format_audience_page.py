import boto3
from utils import * 

'''
This script uses the Bedrock API to analyze a webpage's source code and provide feedback on the positives and challenges of user interaction with the website.
'''
client  = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"


'''
 An example of the challenges and output format is:
                        Confusing information about XXXX
                        Complex navigation with multiple dropdown menus and links
                        Overwhelming amount of information 
                        Small font size and low contrast may be difficult to read
                        No obvious search functionality to find specific information
                        Mobile responsiveness issues may hinder use on smartphone
                        Jargon and legal terminology without plain language explanations
                        No clear way to get personalized help or ask questions
                        Distracting social media feeds and non-essential content
'''

def audience_page_postives(source_code, persona):
    """Using the Bedrock API, using the persona annd the source code to provide feedback on the postives of User interaction with the website.
    Args:
        source_code (str): The source code of the webpage to analyze.
        persona (str): The persona to guide the analysis.
    Returns:
        str: The response from the model of the postives based on the provided source code and persona.
    """
    postives_prompt = f"""

                    You are an expert accessibility and usability reviewer. 
                    Analyze the following website source code and evaluate it from the perspective of the given user persona.

                    - **HTML Source Code**: {source_code}
                    - **User Persona**: {persona}

                    Your task is to identify specific **usability or accessibility postives ** this user may like when interacting with the website, based on their age, tech-savviness, goals, and potential limitations.

                    Each postive should:
                    - Reflect the user’s specific needs 
                    - Be concise but detailed enough to provide actionable insights
                    - Only include the postive itself, without any additional text or context
                    - return a list of the challenges, each challenge should be on a new line with no bullet points or numbers
                    - limit the postives to 3-5 insights

                    An example of postives and the output format is:
                    Clear navigation menu with simple, descriptive labels for different sections
                    Prominent search bar to quickly find specific information
                    Ability to download and save important forms as PDFs for later reference

            
                """

    body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    { "role": "user", "content": postives_prompt }
                    ],
                "max_tokens": 5000,

                }

    resp_postives = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json"
    )

    response_body = json.loads(resp_postives["body"].read())
    positives = response_body["content"][0]["text"]


    # Split the response into individual postives
    positives = positives.strip().split('\n')
    # Remove any leading/trailing whitespace from each postive
    positives_list = [positive.strip() for positive in positives if positive.strip()]


    return positives_list


def audience_page_challenges(source_code, persona):
    """Using the Bedrock API, using the persona annd the source code to provide feedback on the challenges of User interaction with the website.
    Args:
        source_code (str): The source code of the webpage to analyze.
        persona (str): The persona to guide the analysis.
    Returns:
        str: The response from the model of the challenges based on the provided source code and persona.
    """


    challenges_prompt = f"""

                        You are an expert accessibility and usability reviewer. 
                        Analyze the following website source code and evaluate it from the perspective of the given user persona.

                        - **HTML Source Code**: {source_code}
                        - **User Persona**: {persona}

                        Your task is to identify specific **usability or accessibility challenges** this user may face when interacting with the website, based on their age, tech-savviness, goals, and potential limitations.

                        Each challenge should:
                        - Reflect the user’s specific needs or difficulties
                        - The challenge should be actionable and specific to the user persona
                        - Be concise but detailed enough to provide actionable insights
                        - Only include the challenge itself, without any additional text or context
                        - return a list of the challenges, each challenge should be on a new line with no bullet points or numbers
                        - limit the challenges to 3-5 insights

                        An example of the challenges and output format is:

                        Complex navigation structure may overwhelm a first-time voter
                        Lengthy text content could be difficult to quickly scan for key information
                        Lack of clear, prominent call-to-action for mail-in voting process
                        Candidate information not readily accessible from the main page
                        Small font size may strain eyes during extended reading sessions
                    
                        """
    body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    { "role": "user", "content": challenges_prompt }
                    ],
                "max_tokens": 5000,

                }




    resp_challenges = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json"
    ) 





    response_body = json.loads(resp_challenges["body"].read())
    challenges = response_body["content"][0]["text"]


    # Split the response into individual challenges
    challenges = challenges.strip().split('\n')
    # Remove any leading/trailing whitespace from each challenge
    challenges_list = [challenge.strip() for challenge in challenges if challenge.strip()]

    return challenges_list


# url1 = "https://www.nj.gov/state/elections/vote.shtml"
# source_code = get_pure_source(url1)

# persona = " Victor a student at Rutgers university looking to register for the first time . confused if he should vote in his home county or at his college county"

# persona = get_pred(url1,
#                     f"""Based on the url provided, please create one user persona of someone who would navigate the website. 
#                         Include their age, gender, occupation, income level, education level, tech savviness, needs or end goals from the website, 
#                         challenges they may have using the website.
                    

#                         An example of a user persona and formatting is: 

#                         Name: '  '
#                         Age: ' '
#                         Gender: '  '
#                         Occupation:  ''
#                         Income Level:  XX per year
#                         Education Level: '   '
#                         Tech Savviness: Beginner/ Moderate / Intermediate / Advance 

#                         Example Goals and Needs: 

#                         Goals and Needs: 
#                         1. Register to vote in New Jersey
#                         2. Check voter registration status
#                         3. Find the polling place
#                         4. Understand early voting options
#                         5. Request and submit a mail-in ballot

#                         Example Challenges Using the Website:

#                         Challenges Using the Website: 
#                         1. Navigating through multiple pages to find specific information
#                         2. Understanding legal or technical terminology related to voting procedures
#                         3. Locating and downloading necessary forms for voter registration or mail-in ballots
#                         4. Identifying the most up-to-date information, especially if there are changes to voting procedures
#                         5. Finding clear instructions on how to complete and submit various forms
#                         6. Accessing mobile-friendly versions of the website while using her smartphone

#                         Example Summary: 
#                         X  wants to ensure they are properly registered and informed about the voting process in New Jersey. 
#                         They are civic-minded and wants to participate in elections but may struggle with finding time to thoroughly research voting procedures. 
#                         They would benefit from clear, concise information and easy-to-follow instructions on the website.

                                
                                 
#                         """ )


# print(f"postives:\n{ audience_page_postives(source_code, persona)}" )
# print(f"challenges:\n {audience_page_challenges(source_code, persona)}" )
