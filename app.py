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
def chunk_text(text, chunk_size=500):
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

query = "What is the filing deadline for objections to nominating petitions?"
query_embedding = model.encode([query])
distances, indices = index.search(np.array(query_embedding), k=3)

relevant_chunks = [chunks[i] for i in indices[0]]

context = "\n\n".join(relevant_chunks)
prompt = f"Based on the following context, answer the query: {query}\n\nContext:\n{context}"

inference_profile_arn = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

query = f"Based on the following context, summarize the main points:\n\n{context}"

input_data = {
    "anthropic_version": "bedrock-2023-05-31",
    "messages": [
        {"role": "user", "content": query}  # Directly set the user input
    ],
    "max_tokens": 2048,  # Use `max_tokens` instead of `max_tokens_to_sample`
    "temperature": 0,
}

response = bedrock_client.invoke_model(
    modelId=model_id,
    body=json.dumps(input_data),
    contentType="application/json"
)
print(response["body"].read().decode("utf-8"))
