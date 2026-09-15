"""Parse the manuscript-edit protocol out of a completed LLM response."""

from config import MANUSCRIPT_START_MARKER, MANUSCRIPT_END_MARKER


def split_reply_and_edit(full_text: str) -> tuple[str, str | None]:
    """Return (visible_reply, new_manuscript_text_or_None).

    If the model emitted a manuscript block, it is stripped out of the visible
    reply and returned separately so the caller can apply/version/persist it.
    """
    if MANUSCRIPT_START_MARKER not in full_text:
        return full_text.strip(), None

    before, _, rest = full_text.partition(MANUSCRIPT_START_MARKER)
    if MANUSCRIPT_END_MARKER not in rest:
        # Marker started but never closed (e.g. stream cut short) — no edit to apply.
        return before.strip(), None

    manuscript_text, _, _after = rest.partition(MANUSCRIPT_END_MARKER)
    reply = before.strip() or "Manuscript updated."
    return reply, manuscript_text.strip()
