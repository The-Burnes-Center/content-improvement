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
ANTHROPIC_VERSION = "bedrock-2023-05-31"
BOTO3_CLIENT = boto3.client("bedrock-runtime", region_name="us-east-1")
OPEN_AI_CLIENT = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
S3_CLIENT = boto3.client("s3", region_name="us-east-1")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1") 
SCREENSHOTAPI_API_KEY = os.getenv("SCREENSHOTAPI_API_KEY")  


# Model Selection
MODEL_SELECTION = False    
 # using Claude 3.5 sonnet via Bedrock 
if (MODEL_SELECTION): 
    print("Using Bedrock Claude model..")
    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    INSTRUCTOR_CLIENT = instructor.from_anthropic(AnthropicBedrock())

  
else:
    # using OPEN AI 
    print("Using Open AI model..")
    MODEL_ID = "gpt-4.1"
    INSTRUCTOR_CLIENT = instructor.from_openai(OpenAI(api_key = os.getenv("OPENAI_API_KEY")))
   