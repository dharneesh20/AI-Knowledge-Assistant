from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    return model.encode([text])[0].astype("float32")

def embed_texts(texts):
    return model.encode(texts).astype("float32")

def embed_query(query: str):
    return model.encode([query])[0].astype("float32")
