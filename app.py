from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import boto3
import os
import json
import streamlit as st

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# Processes PDFs and extracts text
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

combined_text = ""


folder_path = "output"  # Change this to your folder path

# Splits text into chunks
def chunk_text(text, chunk_size=30):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

chunks = chunk_text(combined_text)

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # Check if it's a file (not a directory)
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            chunks.append(file.read())

# Embeds chunks using SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)

# Indexes embeddings using Faiss
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

query = "When does voting start for the primary election?"


if prompt := st.chat_input():

    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    query_embedding = model.encode([prompt])
    distances, indices = index.search(np.array(query_embedding), k=3)

    relevant_chunks = [chunks[i] for i in indices[0]]

    context = "\n\n".join(relevant_chunks)

    inference_profile_arn = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    summary = f"Based on the following context:\n\n{context}\n\n answer the following question: {prompt}. Include the link to the source. "
    input_data = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": summary}  # Directly set the user input
        ],
        "max_tokens": 2048,  # Use `max_tokens` instead of `max_tokens_to_sample`
        "temperature": 0,
    }

    response = bedrock_client.invoke_model_with_response_stream(
        modelId=model_id,
        body=json.dumps(input_data),
        contentType="application/json"
    )

    event_stream = response["body"]
    
    # Stream the assistant's response
    assistant_response = ""
    assistant_message = st.chat_message("assistant")
    response_container = assistant_message.empty()
    
    for event in event_stream:
        event_str = event['chunk']['bytes'].decode()
        if 'delta' in event_str:
            try:
                delta_index = event_str.index('text\":')
                str = event_str[delta_index:][7:-3]
                str = str.replace("\\n", "\n")
                str = str.replace("\\\"", "\"")
                assistant_response += str
            except:
                pass
        response_container.write(assistant_response)  # Update the displayed text
    
    # Store the full assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})


