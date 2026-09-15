"""In-memory version list management (capped at MAX_VERSIONS).

Persistence to disk is handled separately by persistence/manuscript_store.py;
this module only manages the list structure and numbering.
"""

from datetime import datetime

from config import MAX_VERSIONS


def add_version(versions: list[dict], text: str, note: str = "") -> list[dict]:
    """Prepend a new version snapshot of `text`, then truncate to MAX_VERSIONS."""
    next_number = (versions[0]["version"] + 1) if versions else 1
    new_version = {
        "version": next_number,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "text": text,
        "note": note or "manuscript updated",
    }
    updated = [new_version] + versions
    return updated[:MAX_VERSIONS]


def format_label(version: dict) -> str:
    return f"v{version['version']} — {version['timestamp']} — {version['note']}"


def find_by_label(versions: list[dict], label: str) -> dict | None:
    for v in versions:
        if format_label(v) == label:
            return v
    return None
