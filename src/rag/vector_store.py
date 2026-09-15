"""Session-only, in-memory vector store for uploaded papers."""

import uuid

import chromadb

from src.ollama_client import embed


def new_collection():
    """Create a fresh in-memory Chroma collection for this browser session."""
    client = chromadb.EphemeralClient()
    return client.create_collection(name=f"session-{uuid.uuid4().hex}")


def add_chunks(collection, filename: str, chunks: list[dict]) -> None:
    if not chunks:
        return
    ids = [f"{filename}-{i}-{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    embeddings = [embed(text) for text in documents]
    metadatas = [{"filename": filename, "page": c["page"]} for c in chunks]
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
