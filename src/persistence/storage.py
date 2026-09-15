"""Local-disk path resolution, shaped like the eventual Google Drive layout.

Scientific-Writing-AI/<User>/<Project>/{Manuscript,Chat,Versions}

Kept as the single seam to swap in real Google Drive API storage later —
every other module reaches disk only through these functions.
"""

from pathlib import Path

from config import DATA_ROOT


def project_dir(user: str, project: str) -> Path:
    path = DATA_ROOT / user / project
    (path / "Manuscript").mkdir(parents=True, exist_ok=True)
    (path / "Chat").mkdir(parents=True, exist_ok=True)
    (path / "Versions").mkdir(parents=True, exist_ok=True)
    return path


def manuscript_path(user: str, project: str) -> Path:
    return project_dir(user, project) / "Manuscript" / "current.md"


def chat_path(user: str, project: str) -> Path:
    return project_dir(user, project) / "Chat" / "chat_history.json"


def versions_dir(user: str, project: str) -> Path:
    return project_dir(user, project) / "Versions"


def versions_index_path(user: str, project: str) -> Path:
    return versions_dir(user, project) / "versions_index.json"


def list_projects_by_recency(user: str) -> list[str]:
    """This user's project names, most recently active first."""
    user_dir = DATA_ROOT / user
    if not user_dir.exists():
        return []

    entries = []
    for project_dir_path in user_dir.iterdir():
        if not project_dir_path.is_dir():
            continue
        chat_file = project_dir_path / "Chat" / "chat_history.json"
        mtime = chat_file.stat().st_mtime if chat_file.exists() else project_dir_path.stat().st_mtime
        entries.append((mtime, project_dir_path.name))

    entries.sort(key=lambda e: e[0], reverse=True)
    return [project for _, project in entries]
