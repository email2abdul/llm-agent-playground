"""
Simple in-memory RAG with Gemini embeddings.

Usage:
  python3 rag.py index           # docs/ se index banao (har baar docs change ho to chalao)
  python3 rag.py search "query"  # CLI se search test karo
"""

import os
import sys
import pickle
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ============================================================
# CONFIG
# ============================================================
DOCS_DIR = Path(__file__).parent / "docs"
INDEX_FILE = Path(__file__).parent / "rag_index.pkl"
EMBED_MODEL = "gemini-embedding-001"   # 3072-dim vectors
CHUNK_SIZE = 500      # characters per chunk
CHUNK_OVERLAP = 100   # overlap — concepts adhe me na kate
TOP_K = 3             # search me kitne chunks return karne hain

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ============================================================
# CHUNKING — bade document ko chhote pieces me todna
# ============================================================
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Text ko fixed-size chunks me todo (slight overlap ke saath)."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start += size - overlap
    return chunks


# ============================================================
# EMBEDDING — text ko vector me convert karna
# ============================================================
def embed_texts(texts: list) -> np.ndarray:
    """Texts ki list → numpy 2D array (rows = chunks, cols = embedding dims)."""
    result = client.models.embed_content(model=EMBED_MODEL, contents=texts)
    vectors = [e.values for e in result.embeddings]
    return np.array(vectors, dtype=np.float32)


# ============================================================
# INDEX — build, save, load
# ============================================================
def build_index() -> dict:
    """docs/ ke saare .md aur .txt files load karo, chunk + embed karo."""
    if not DOCS_DIR.exists():
        DOCS_DIR.mkdir()
        print(f"  Created {DOCS_DIR.name}/ — add .md or .txt files and re-run")
        return {"chunks": [], "sources": [], "embeddings": np.zeros((0, 0))}

    files = sorted(list(DOCS_DIR.glob("*.md")) + list(DOCS_DIR.glob("*.txt")))
    if not files:
        print(f"  No .md or .txt files in {DOCS_DIR.name}/")
        return {"chunks": [], "sources": [], "embeddings": np.zeros((0, 0))}

    all_chunks, all_sources = [], []
    for f in files:
        text = f.read_text()
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        all_sources.extend([f.name] * len(chunks))
        print(f"  {f.name}: {len(chunks)} chunks")

    print(f"  Embedding {len(all_chunks)} chunks via {EMBED_MODEL}...")
    embeddings = embed_texts(all_chunks)

    index = {"chunks": all_chunks, "sources": all_sources, "embeddings": embeddings}
    with open(INDEX_FILE, "wb") as fp:
        pickle.dump(index, fp)
    print(f"  Saved {INDEX_FILE.name} ({len(all_chunks)} chunks, dim={embeddings.shape[1]})")
    return index


def load_index():
    if not INDEX_FILE.exists():
        return None
    with open(INDEX_FILE, "rb") as fp:
        return pickle.load(fp)


# ============================================================
# SEARCH — cosine similarity se top-k chunks
# ============================================================
def cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """1D query vector vs 2D matrix → 1D similarity scores (between -1 aur 1)."""
    q = query_vec / np.linalg.norm(query_vec)
    m = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return m @ q


def search_docs(query: str, k: int = TOP_K) -> str:
    """Query ke against top-k chunks return karo (agent.py ka tool yahi call karega)."""
    index = load_index()
    if index is None or len(index["chunks"]) == 0:
        return "No documents indexed. Run: python3 rag.py index"

    query_vec = embed_texts([query])[0]
    scores = cosine_similarity(query_vec, index["embeddings"])
    top_idx = np.argsort(-scores)[:k]

    parts = []
    for i in top_idx:
        parts.append(
            f"[Source: {index['sources'][i]} | score: {scores[i]:.3f}]\n{index['chunks'][i]}"
        )
    return "\n\n---\n\n".join(parts)


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "index":
        build_index()
    elif cmd == "search":
        if len(sys.argv) < 3:
            print('Usage: python3 rag.py search "your query"')
            sys.exit(1)
        print(search_docs(sys.argv[2]))
    else:
        print(__doc__)
