"""Parse a multiple-choice clarifying question out of a completed LLM response.

Format (plain text, not JSON — easier for a small local model to produce reliably):

<<<ASK_START>>>
Question: <the question>
Options: <option 1> | <option 2> | <option 3>
<<<ASK_END>>>

Rendered as a popup with one button per option, capped at MAX_ASK_OPTIONS.
"""

from config import ASK_END_MARKER, ASK_START_MARKER, MAX_ASK_OPTIONS


def visible_prefix(buffer: str) -> str:
    idx = buffer.find(ASK_START_MARKER)
    return buffer if idx == -1 else buffer[:idx]


def split_reply_and_question(full_text: str) -> tuple[str, dict | None]:
    """Return (visible_reply, {"question": str, "options": [str, ...]} or None)."""
    if ASK_START_MARKER not in full_text:
        return full_text.strip(), None

    before, _, rest = full_text.partition(ASK_START_MARKER)
    if ASK_END_MARKER not in rest:
        return before.strip(), None

    body, _, after = rest.partition(ASK_END_MARKER)

    question_text = ""
    options: list[str] = []
    for line in body.strip().splitlines():
        line = line.strip()
        if line.lower().startswith("question:"):
            question_text = line.split(":", 1)[1].strip()
        elif line.lower().startswith("options:"):
            raw = line.split(":", 1)[1].strip()
            options = [opt.strip() for opt in raw.split("|") if opt.strip()]

    reply_parts = [before.strip(), after.strip()]
    reply = "\n\n".join(p for p in reply_parts if p)

    if not question_text or len(options) < 2:
        # Malformed block — fall back to plain text, marker included, rather than losing content.
        return (reply or body.strip()), None

    options = options[:MAX_ASK_OPTIONS]
    return reply or question_text, {"question": question_text, "options": options}
