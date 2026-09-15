"""Locate and replace one markdown-heading section within the manuscript,
so a chat reply can be inserted as (or merged into) a named section without
touching the rest of the document."""

import re

_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*\S)[ \t]*$", re.MULTILINE)


def _normalize(heading_text: str) -> str:
    return re.sub(r"\s+", " ", heading_text.strip().lower()).lstrip("#").strip()


def _parse_blocks(manuscript: str) -> list[dict]:
    """Each block spans from its heading line to just before the next heading
    at the same or a shallower level (or the end of the document)."""
    matches = list(_HEADING_RE.finditer(manuscript))
    blocks = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        end = len(manuscript)
        for nxt in matches[i + 1 :]:
            if len(nxt.group(1)) <= level:
                end = nxt.start()
                break
        blocks.append({"level": level, "heading": m.group(2), "start": m.start(), "end": end})
    return blocks


def replace_or_append_section(manuscript: str, heading: str, new_section_text: str) -> str:
    """Replace the block whose heading matches `heading` (case/whitespace-insensitive,
    ignoring a leading '#') with `new_section_text`. If no matching heading exists,
    append it to the end of the manuscript instead."""
    target = _normalize(heading)
    new_section_text = new_section_text.strip()

    for block in _parse_blocks(manuscript):
        if _normalize(block["heading"]) == target:
            before = manuscript[: block["start"]]
            after = manuscript[block["end"] :]
            return f"{before}{new_section_text}\n\n{after}".strip() + "\n"

    if not manuscript.strip():
        return new_section_text + "\n"
    return f"{manuscript.rstrip()}\n\n{new_section_text}\n"
