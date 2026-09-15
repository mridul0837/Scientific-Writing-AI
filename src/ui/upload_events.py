"""Handle paper/writing-sample uploads. Nothing here ever touches disk under data/ —
uploaded content lives only in gr.State and the ephemeral Chroma collection."""

import os

import gradio as gr

from src.rag.pdf_parser import parse_pdf
from src.rag.chunker import chunk_pages
from src.rag.vector_store import add_chunks
from src.style.style_profile import build_style_profile

MAX_FILES = 10


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def process_papers(files, papers, collection):
    if not files:
        return papers, collection, "No papers uploaded."
    if len(files) > MAX_FILES:
        raise gr.Error(f"Please upload at most {MAX_FILES} papers at a time.")

    papers = list(papers)
    for path in files:
        filename = os.path.basename(path)
        pages = parse_pdf(path)
        chunks = chunk_pages(pages)
        add_chunks(collection, filename, chunks)
        papers.append({"filename": filename, "pages": len(pages), "chunk_count": len(chunks)})

    summary = "\n".join(f"- {p['filename']}: {p['pages']} pages, {p['chunk_count']} chunks" for p in papers)
    return papers, collection, f"Loaded {len(papers)} paper(s):\n{summary}"


def process_samples(files, samples):
    if not files:
        return samples, "No writing samples uploaded."
    if len(files) > MAX_FILES:
        raise gr.Error(f"Please upload at most {MAX_FILES} writing samples at a time.")

    samples = list(samples)
    for path in files:
        filename = os.path.basename(path)
        if path.lower().endswith(".pdf"):
            text = "\n\n".join(p["text"] for p in parse_pdf(path))
        else:
            text = _read_text_file(path)
        samples.append({"filename": filename, "text": text})

    return samples, f"Loaded {len(samples)} writing sample(s)."


def learn_style(samples, samples_status):
    if not samples:
        return "", samples_status
    profile = build_style_profile(samples)
    return profile, f"{samples_status}\n\nStyle profile learned from {len(samples)} sample(s)."
