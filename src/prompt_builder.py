"""Assemble the Ollama `messages` list for one chat turn."""

from config import MANUSCRIPT_START_MARKER, MANUSCRIPT_END_MARKER, MAX_HISTORY_TURNS
from src.rag.retriever import retrieve_context

_SYSTEM_TEMPLATE = """You are a scientific writing assistant. The user will chat with you \
naturally — infer what they want (research, write, rewrite, explain, summarize, review, \
edit, or format) from their message; do not ask them to pick a mode.

{style_section}

Current manuscript:
---
{manuscript}
---

If the user asks you to modify, write, or add to the manuscript, first give your normal \
conversational reply, then append the FULL new manuscript text (not a diff) wrapped exactly \
like this, with nothing after the closing marker:

{start_marker}
...full new manuscript text...
{end_marker}

Only include this block when you are actually changing the manuscript."""


def _style_section(style_profile: str) -> str:
    if not style_profile:
        return "No writing-style profile is available yet."
    return f"Match the user's writing style using this profile:\n{style_profile}"


def build_messages(
    user_message: str,
    manuscript_text: str,
    style_profile: str,
    history: list[dict],
    collection,
) -> list[dict]:
    system_content = _SYSTEM_TEMPLATE.format(
        style_section=_style_section(style_profile),
        manuscript=manuscript_text or "(empty — no manuscript yet)",
        start_marker=MANUSCRIPT_START_MARKER,
        end_marker=MANUSCRIPT_END_MARKER,
    )

    messages = [{"role": "system", "content": system_content}]
    messages.extend(history[-MAX_HISTORY_TURNS:])

    rag_context = retrieve_context(collection, user_message)
    if rag_context:
        messages.append({"role": "user", "content": f"{rag_context}\n\n{user_message}"})
    else:
        messages.append({"role": "user", "content": user_message})

    return messages
