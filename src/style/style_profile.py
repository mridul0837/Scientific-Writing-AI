"""Derive a reusable style-guidance string from the user's writing samples."""

import ollama

from config import CHAT_MODEL

_STYLE_PROMPT = """You are analyzing writing samples to build a concise style guide \
for an AI assistant that will later write or rewrite text to match this author's voice.

Read the samples below and produce a short, actionable style profile covering: \
tone/formality, typical sentence length and structure, vocabulary tendencies, \
use of hedging/certainty, paragraph structure, and any distinctive habits. \
Write it as instructions the assistant should follow, not as a description of the samples.

Writing samples:
{samples}

Style profile (instructions for imitating this author):"""


def build_style_profile(samples: list[dict]) -> str:
    """samples: list of {"filename": str, "text": str}. Returns a style-guidance string."""
    if not samples:
        return ""

    combined = "\n\n---\n\n".join(
        f"[{s['filename']}]\n{s['text'][:4000]}" for s in samples
    )
    prompt = _STYLE_PROMPT.format(samples=combined)

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()
