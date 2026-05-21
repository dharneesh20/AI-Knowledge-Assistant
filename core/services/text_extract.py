import os
import docx2txt
from PyPDF2 import PdfReader

import re

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks
def extract_text_from_upload(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError("Uploaded file not found")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text.strip()

    if ext == ".docx":
        return (docx2txt.process(file_path) or "").strip()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    raise ValueError("Unsupported file type. Upload PDF, DOCX, or TXT only.")
