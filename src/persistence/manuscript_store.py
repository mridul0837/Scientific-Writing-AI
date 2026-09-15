"""Save/load the current manuscript and its version history."""

import json

from src.persistence.storage import manuscript_path, versions_dir, versions_index_path


def save_current(user: str, project: str, text: str) -> None:
    manuscript_path(user, project).write_text(text, encoding="utf-8")


def load_current(user: str, project: str) -> str:
    path = manuscript_path(user, project)
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _version_file(user: str, project: str, version_number: int):
    return versions_dir(user, project) / f"v{version_number}.md"


def save_versions(user: str, project: str, versions: list[dict]) -> None:
    """Write each version's text to its own file plus an index of metadata,
    and remove any leftover files for versions no longer in the list."""
    v_dir = versions_dir(user, project)
    keep_names = set()

    index = []
    for v in versions:
        _version_file(user, project, v["version"]).write_text(v["text"], encoding="utf-8")
        keep_names.add(f"v{v['version']}.md")
        index.append({"version": v["version"], "timestamp": v["timestamp"], "note": v["note"]})

    versions_index_path(user, project).write_text(json.dumps(index, indent=2), encoding="utf-8")

    for existing in v_dir.glob("v*.md"):
        if existing.name not in keep_names:
            existing.unlink()


def load_versions(user: str, project: str) -> list[dict]:
    index_path = versions_index_path(user, project)
    if not index_path.exists():
        return []

    index = json.loads(index_path.read_text(encoding="utf-8"))
    versions = []
    for entry in index:
        file_path = _version_file(user, project, entry["version"])
        text = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        versions.append({**entry, "text": text})
    return versions
