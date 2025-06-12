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

if (MODEL_SELECTION): 
    print("Using Bedrock Claude model..")

    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    ANTHROPIC_VERSION = "bedrock-2023-05-31"
    CLIENT_CODE_ACCESSIBILITY   = boto3.client("bedrock-runtime", region_name="us-east-1")

    WEB_DESIGN_CLIENT = instructor.from_anthropic(AnthropicBedrock())

    # use Claude 3.5 sonnet via Bedrock 
  
else:
    print("Using Open AI model..")
    MODEL_ID = "gpt-4.1"
    ANTHROPIC_VERSION = None

    CLIENT_CODE_ACCESSIBILITY = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    WEB_DESIGN_CLIENT = instructor.from_openai(OpenAI(api_key = os.getenv("OPENAI_API_KEY")))