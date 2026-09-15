"""Assemble the Ollama `messages` list for one chat turn."""

from config import MANUSCRIPT_END_MARKER, MANUSCRIPT_START_MARKER, MAX_HISTORY_TURNS
from src.rag.retriever import retrieve_context

_SYSTEM_TEMPLATE = """You are a scientific writing assistant — first and foremost a natural \
conversational writing partner. When the user asks you to write, draft, rewrite, or improve \
something (a sentence, a paragraph, a section, anything), just write it directly in your reply, \
like any chatbot would. That is normal conversation — it does NOT update the manuscript document.

The manuscript is a separate, explicit document. Only touch it when the user clearly asks to see, \
get, compile, or update the manuscript/paper/document itself (e.g. "show me the manuscript," "give \
me the full manuscript," "compile what we have so far," "update the document with this"). When that \
happens, pull together everything that's been written and agreed on in this conversation plus the \
existing manuscript below into one coherent, complete document.

Writing quality is the top priority whenever you write text: be precise, concise, and academically \
rigorous. Avoid filler, hedge only when the evidence genuinely warrants it, prefer active voice and \
concrete claims over vague ones, and keep terminology consistent throughout.

{style_section}

Current manuscript:
---
{manuscript}
---

Only when the user explicitly asks for the manuscript/document itself: give your conversational \
reply first, then output the ENTIRE manuscript (not a diff, not just the new part), wrapped exactly \
like this, with nothing after the closing marker:

{start_marker}
...full manuscript text...
{end_marker}

For every other message — including requests to write or revise something — just reply in words. \
Do not include that block unless the user explicitly asked for the manuscript/document itself."""


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
