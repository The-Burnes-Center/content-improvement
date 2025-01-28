from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import ChatCompletion

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

response = ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

print(response["choices"][0]["message"]["content"])
