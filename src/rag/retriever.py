"""Retrieve and format relevant paper chunks for a query."""

from config import RETRIEVAL_TOP_K
from src.ollama_client import embed


def retrieve_context(collection, query: str, top_k: int = RETRIEVAL_TOP_K) -> str:
    """Return a formatted context block of the most relevant chunks, or "" if none."""
    if collection is None or collection.count() == 0:
        return ""

    query_embedding = embed(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    if not documents:
        return ""

    lines = ["Context from uploaded papers:"]
    for doc, meta in zip(documents, metadatas):
        source = meta.get("filename", "unknown")
        page = meta.get("page", "?")
        lines.append(f"\n[{source}, p.{page}]\n{doc}")
    return "\n".join(lines)
