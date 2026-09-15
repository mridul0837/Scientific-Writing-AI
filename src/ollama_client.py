"""Thin wrapper around the Ollama python client.

Kept as the single seam between the app and the LLM runtime, so swapping
Ollama for a hosted API later (e.g. deploying the UI to Hugging Face Spaces)
only requires changing this file.
"""

import ollama

from config import CHAT_MODEL, EMBED_MODEL


def chat_stream(messages: list[dict]):
    """Yield successive text chunks from a streaming chat completion."""
    stream = ollama.chat(model=CHAT_MODEL, messages=messages, stream=True)
    for part in stream:
        content = part.get("message", {}).get("content", "")
        if content:
            yield content


def embed(text: str) -> list[float]:
    response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]
