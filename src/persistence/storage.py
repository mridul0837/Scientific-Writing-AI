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


def list_users() -> list[str]:
    if not DATA_ROOT.exists():
        return []
    return sorted(p.name for p in DATA_ROOT.iterdir() if p.is_dir())


def list_projects(user: str) -> list[str]:
    user_dir = DATA_ROOT / user
    if not user_dir.exists():
        return []
    return sorted(p.name for p in user_dir.iterdir() if p.is_dir())
