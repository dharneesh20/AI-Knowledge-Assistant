import os
import pickle
import numpy as np
import faiss

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORE_DIR = os.path.join(BASE_DIR, "vector_store")

INDEX_PATH = os.path.join(STORE_DIR, "faiss.index")
META_PATH = os.path.join(STORE_DIR, "meta.pkl")

DIM = 384


def _ensure_store():
    os.makedirs(STORE_DIR, exist_ok=True)


def _load_meta():
    if not os.path.exists(META_PATH):
        return []
    with open(META_PATH, "rb") as f:
        return pickle.load(f)


def _save_meta(meta):
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)


def _load_index():
    _ensure_store()
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    return faiss.IndexFlatL2(DIM)


def _save_index(index):
    faiss.write_index(index, INDEX_PATH)


def add_chunks_to_index(chunk_meta, embeddings):
    """
    chunk_meta: list of dicts:
    {
        "chunk_id": int,
        "document_id": int,
        "owner_id": int,
        "text": str,
        "chunk_index": int,
        "document_title": str
    }
    embeddings: numpy array (n, 384)
    """

    if not chunk_meta:
        return

    embeddings = np.array(embeddings, dtype="float32")

    index = _load_index()
    meta = _load_meta()

    index.add(embeddings)
    meta.extend(chunk_meta)

    _save_index(index)
    _save_meta(meta)


def search(owner_id, query_embedding, top_k=5):
    """
    Returns list of meta dicts (filtered by owner_id)
    """
    query_embedding = np.array(query_embedding, dtype="float32").reshape(1, -1)

    meta = _load_meta()
    if len(meta) == 0:
        return []

    index = _load_index()

    # search more then filter by user
    D, I = index.search(query_embedding, top_k * 20)

    hits = []
    for idx in I[0]:
        if idx == -1:
            continue
        if idx < len(meta):
            m = meta[idx]
            if m.get("owner_id") == owner_id:
                hits.append(m)

        if len(hits) >= top_k:
            break

    return hits


def rebuild_user_index(exclude_document_id=None):
    """
    Clears FAISS index and meta.
    exclude_document_id is ignored in this simple implementation.
    """
    _ensure_store()

    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)

    if os.path.exists(META_PATH):
        os.remove(META_PATH)


def remove_document_from_index(document_id):
    """
    Simple approach: clear and rebuild later.
    """
    rebuild_user_index()
