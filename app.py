from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import boto3
import os
import json

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"


# Processes PDFs and extracts text
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

pdf1_text = extract_text_from_pdf("2025-chron-general-election.pdf")
pdf2_text = extract_text_from_pdf("2025-chron-primary-election.pdf")
combined_text = pdf1_text + "\n" + pdf2_text

# Splits text into chunks
def chunk_text(text, chunk_size=200):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

chunks = chunk_text(combined_text)

# Embeds chunks using SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)

# Indexes embeddings using Faiss
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

query = "When does voting start for the primary election?"
query_embedding = model.encode([query])
distances, indices = index.search(np.array(query_embedding), k=3)

relevant_chunks = [chunks[i] for i in indices[0]]

context = "\n\n".join(relevant_chunks)
while True: 
    prompt = input ("Enter question (or type 'exit' to quit):") 
            # sample question: "When does voting start for the general election?"
    if query.lower() == "exit":
        print("program exited")
        break
    
inference_profile_arn = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

summary = f"Based on the following context, summarize the main points:\n\n{context}"

input_data = {
    "anthropic_version": "bedrock-2023-05-31",
    "messages": [
        {"role": "user", "content": prompt}  # Directly set the user input
    ],
    "max_tokens": 2048,  # Use `max_tokens` instead of `max_tokens_to_sample`
    "temperature": 0,
}

response = bedrock_client.invoke_model_with_response_stream(
    modelId=model_id,
    body=json.dumps(input_data),
    contentType="application/json"
)
"""
# Read and parse the response body
decoded_response = json.loads(response["body"].read().decode("utf-8"))

# Extract and print only the generated text
# llm_output = decoded_response["outputs"][0]["text"]  # Adjust if the key structure differs
print(decoded_response['content'][0]['text'])"""


event_stream = response["body"]

for event in event_stream:
    event_bytes = event['chunk']['bytes']
    event_str = event_bytes.decode()
    if 'delta' in event_str:
        try:
            delta_index = event_str.index('text\":')
            print(event_str[delta_index:][7:-2])
        except:
            pass
    else:
        pass

print('Stream complete')