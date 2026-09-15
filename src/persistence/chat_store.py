"""Save/load chat history for a project."""

import json

from src.persistence.storage import chat_path


def save(user: str, project: str, messages: list[dict]) -> None:
    chat_path(user, project).write_text(json.dumps(messages, indent=2), encoding="utf-8")


def load(user: str, project: str) -> list[dict]:
    path = chat_path(user, project)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
