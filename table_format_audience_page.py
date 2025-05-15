import boto3
from utils import * 



url = "https://www.nj.gov/state/elections/vote.shtml"

client  = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

persona = " Victor a student at Rutgers university looking to register for the first time . confused if he should vote in his home county or at his college county"

ouput_list = []
source_code = get_pure_source(url)

challenges_prompt = f"""

                    You are an expert accessibility and usability reviewer. 
                    Analyze the following website source code and evaluate it from the perspective of the given user persona.

                    - **HTML Source Code**: {source_code}
                    - **User Persona**: {persona}

                    Your task is to identify specific **usability or accessibility challenges** this user may face when interacting with the website, based on their age, tech-savviness, goals, and potential limitations.

                    Each challenge should:
                    - Reflect the user’s specific needs or difficulties
                    - Be concise but descriptive
                   
                    """









                


body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            { "role": "user", "content": challenges_prompt }
            ],
        "max_tokens": 5000,

        }

resp = client.invoke_model(
    modelId=model_id,
    body=json.dumps(body),
    contentType="application/json"
) 

response_body = json.loads(resp["body"].read())

challenges_list = response_body["content"][0]["text"]
print(challenges_list)

if type(challenges_list) is str: 
    seperated_by_comma = challenges_list.strip('[]').split(" , ")


    for suggestion in seperated_by_comma: 
        print(f"suggestion: {suggestion}")

print(type(challenges_list))






#challenges_output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona}. """)

#print(f"auditing website based on victor: {challenges_output} ")

