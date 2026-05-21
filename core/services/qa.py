from dataclasses import dataclass
from django.db.models import Q
from ..models import DocumentChunk
from .embeddings import embed_query
from .vector_store import search


@dataclass
class RetrievalHit:
    chunk_id: int
    score: float
    document_title: str
    snippet: str
    chunk_index: int


def retrieve(owner_id: int, query: str, top_k: int = 5) -> list[RetrievalHit]:
    qv = embed_query(query)
    matches = search(owner_id, qv, top_k=top_k)

    if not matches:
        return []

    chunk_ids = [m[0] for m in matches]
    score_by_id = {cid: score for cid, score in matches}

    chunks = (
        DocumentChunk.objects.select_related("document")
        .filter(id__in=chunk_ids, document__owner_id=owner_id)
    )
     # Keep FAISS order
    chunks_by_id = {c.id: c for c in chunks}

    hits: list[RetrievalHit] = []
    for cid in chunk_ids:
        c = chunks_by_id.get(cid)
        if not c:
            continue
        snippet = c.content
        if len(snippet) > 380:
            snippet = snippet[:380].rstrip() + "…"

        hits.append(
            RetrievalHit(
                chunk_id=c.id,
                score=score_by_id.get(c.id, 0.0),
                document_title=c.document.title,
                snippet=snippet,
                chunk_index=c.chunk_index,
            )
        )

    return hits

def naive_answer(query: str, hits: list[RetrievalHit]) -> str:
    """Offline answer (no LLM). Creates a concise answer by summarizing top snippets."""
    if not hits:
        return (
            "I couldn’t find anything relevant in your uploaded documents. "
            "Try uploading more files or rephrasing your question."
        )

    # This is intentionally simple: the UI shows sources.
    # If you want an LLM later, replace this with a prompt call.
    best = hits[0]

    answer = (
        f"Based on your documents, the most relevant information is from: "
        f"\"{best.document_title}\" (chunk #{best.chunk_index}).\n\n"
        f"Key excerpt:\n{best.snippet}\n\n"
        "Open the sources below to verify and read more context."
    )
    return answer