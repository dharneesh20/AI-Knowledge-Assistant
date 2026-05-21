from typing import List

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 200) -> List[str]:
    text = (text or "").strip().replace("\r", "\n")
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start < 0:
            start = 0

        if end == n:
            break

    return chunks
