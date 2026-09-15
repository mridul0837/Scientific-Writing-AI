"""Parse the manuscript-edit protocol out of a completed LLM response.

The model is only supposed to emit a manuscript block when the user explicitly
asked to see/get/compile the manuscript itself — everything else is plain
chat and this returns edit=None.
"""

from config import MANUSCRIPT_END_MARKER, MANUSCRIPT_START_MARKER


def visible_prefix(buffer: str) -> str:
    """The portion of a streaming buffer safe to show before the manuscript marker starts."""
    idx = buffer.find(MANUSCRIPT_START_MARKER)
    return buffer if idx == -1 else buffer[:idx]


def split_reply_and_edit(full_text: str) -> tuple[str, str | None]:
    """Return (visible_reply, new_manuscript_text_or_None).

    If the model emitted a manuscript block, it is stripped out of the visible
    reply (any text before and after the marker is preserved) and returned
    separately so the caller can version/persist it.
    """
    if MANUSCRIPT_START_MARKER not in full_text:
        return full_text.strip(), None

    before, _, rest = full_text.partition(MANUSCRIPT_START_MARKER)
    if MANUSCRIPT_END_MARKER not in rest:
        # Marker started but never closed (e.g. stream cut short) — no edit to apply.
        return before.strip(), None

    manuscript_text, _, after = rest.partition(MANUSCRIPT_END_MARKER)
    reply_parts = [before.strip(), after.strip()]
    reply = "\n\n".join(p for p in reply_parts if p) or "Manuscript updated."
    return reply, manuscript_text.strip()
