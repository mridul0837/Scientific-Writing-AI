"""Paragraph-aware, character-based text chunking with overlap."""

from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        if len(para) <= chunk_size:
            current = para
        else:
            # Paragraph itself exceeds chunk_size: hard-split with overlap.
            start = 0
            while start < len(para):
                end = start + chunk_size
                chunks.append(para[start:end])
                start = end - overlap
            current = ""

    if current:
        chunks.append(current)

    # Apply overlap between consecutive chunks for better retrieval context.
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]
    for prev, curr in zip(chunks, chunks[1:]):
        tail = prev[-overlap:]
        overlapped.append(f"{tail}{curr}")
    return overlapped


def chunk_pages(pages: list[dict]) -> list[dict]:
    """Chunk parsed pages, keeping track of which page each chunk came from."""
    chunks = []
    for page in pages:
        for chunk in chunk_text(page["text"]):
            chunks.append({"page": page["page"], "text": chunk})
    return chunks
