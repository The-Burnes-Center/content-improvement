import boto3
import os
from openai import OpenAI
import instructor
from anthropic import AnthropicBedrock
"""
Choosing a Bedrock Model for Application 
"""
#Constants 
MAX_ISSUES_CODE_ACESSIBILITY = 1 
MAX_TOKENS = 5000
S3_BUCKET_NAME = "nj-ai-votes-image"


# Model Selection
MODEL_SELECTION = True 
 # using Claude 3.5 sonnet via Bedrock 
if (MODEL_SELECTION): 
    print("Using Bedrock Claude model..")

    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    ANTHROPIC_VERSION = "bedrock-2023-05-31"
    
    CODE_ACCESSIBILITY_CLIENT   = boto3.client("bedrock-runtime", region_name="us-east-1")
    #webdesign and content clarity use the same client, but for organization purposes a new variable is created 
    WEB_DESIGN_CLIENT = instructor.from_anthropic(AnthropicBedrock())
    CONTENT_CLARITY_CLIENT = instructor.from_anthropic(AnthropicBedrock())

  
else:
    # using OPEN AI 
    print("Using Open AI model..")
    MODEL_ID = "gpt-4.1"
    ANTHROPIC_VERSION = None

    CODE_ACCESSIBILITY_CLIENT = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    WEB_DESIGN_CLIENT = instructor.from_openai(OpenAI(api_key = os.getenv("OPENAI_API_KEY")))
    CONTENT_CLARITY_CLIENT = instructor.from_openai(OpenAI(api_key = os.getenv("OPENAI_API_KEY")))