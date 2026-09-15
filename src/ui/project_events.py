"""Project loading/creation/pin/delete. Single fixed local user
(config.LOCAL_USER) — no user-facing account concept, matching the "no
multi-user accounts" MVP scope. The sidebar (two project name lists: pinned
and everything else) replaces manual name entry:
  - on page load: resume the most recently active project, or create the
    first one if none exist yet
  - "+ New" creates a fresh, auto-named project
  - clicking a sidebar entry loads that project
  - "Pin"/"Delete" act on whichever project is currently loaded
"""

import re

import gradio as gr

from config import LOCAL_USER
from src.manuscript.versioning import format_label
from src.persistence import chat_store, manuscript_store, storage
from src.rag.vector_store import new_collection
from src.ui import state as ui_state

_UNTITLED_RE = re.compile(r"^Untitled (\d+)$")


def _next_untitled_name() -> str:
    existing = storage.list_projects_by_recency(LOCAL_USER)
    numbers = [int(m.group(1)) for name in existing if (m := _UNTITLED_RE.match(name))]
    return f"Untitled {max(numbers, default=0) + 1}"


def _pin_label(project: str, pinned: list[str]) -> str:
    return "📌 Unpin" if project in pinned else "📌 Pin"


def refresh_project_lists(selected: str | None = None):
    all_projects = storage.list_projects_by_recency(LOCAL_USER)
    pinned = storage.load_pinned(LOCAL_USER)
    pinned_ordered = [p for p in pinned if p in all_projects]
    unpinned = [p for p in all_projects if p not in pinned]

    return (
        gr.update(visible=bool(pinned_ordered)),  # pinned_section
        gr.update(choices=pinned_ordered, value=selected if selected in pinned_ordered else None),
        gr.update(choices=unpinned, value=selected if selected in unpinned else None),
    )


def _load(project: str):
    messages = chat_store.load(LOCAL_USER, project)
    manuscript_text = manuscript_store.load_current(LOCAL_USER, project)
    versions = manuscript_store.load_versions(LOCAL_USER, project)
    collection = new_collection()
    pinned = storage.load_pinned(LOCAL_USER)

    versions_choices = [format_label(v) for v in versions]

    return (
        {"user": LOCAL_USER, "project": project},  # state_user_project
        messages,                              # state_messages
        ui_state.initial_papers(),             # state_papers
        ui_state.initial_samples(),            # state_samples
        ui_state.initial_style_profile(),      # state_style_profile
        collection,                            # state_vector_collection
        manuscript_text,                       # state_manuscript_text
        versions,                               # state_manuscript_versions
        messages,                              # chatbot
        manuscript_text,                       # manuscript_display
        gr.update(choices=versions_choices, value=None),  # versions_radio
        "",                                    # papers_status
        "",                                    # samples_status
        f"### {project}",                      # chat_header
        gr.update(value=_pin_label(project, pinned)),  # pin_btn
    )


def select_project(project: str):
    if not project:
        raise gr.Error("Select a project from the list.")
    return (*_load(project), *refresh_project_lists(project))


def create_new_project():
    project = _next_untitled_name()
    storage.project_dir(LOCAL_USER, project)  # creates the on-disk folders
    return (*_load(project), *refresh_project_lists(project))


def startup():
    """Fired on page load: resume the most recent project, or start the first one."""
    projects = storage.list_projects_by_recency(LOCAL_USER)
    if not projects:
        project = _next_untitled_name()
        storage.project_dir(LOCAL_USER, project)
    else:
        project = projects[0]
    return (*_load(project), *refresh_project_lists(project))


def toggle_pin(user_project: dict):
    project = user_project.get("project")
    if not project:
        raise gr.Error("No project loaded.")

    pinned = storage.load_pinned(LOCAL_USER)
    if project in pinned:
        pinned.remove(project)
    else:
        pinned.append(project)
    storage.save_pinned(LOCAL_USER, pinned)

    return (*refresh_project_lists(project), gr.update(value=_pin_label(project, pinned)))


def request_delete(user_project: dict):
    project = user_project.get("project")
    if not project:
        raise gr.Error("No project loaded.")
    return gr.update(visible=True), f"Delete **{project}**? This can't be undone."


def cancel_delete():
    return gr.update(visible=False)


def confirm_delete(user_project: dict):
    project = user_project.get("project")
    if not project:
        raise gr.Error("No project loaded.")

    storage.delete_project(LOCAL_USER, project)

    remaining = storage.list_projects_by_recency(LOCAL_USER)
    if remaining:
        next_project = remaining[0]
    else:
        next_project = _next_untitled_name()
        storage.project_dir(LOCAL_USER, next_project)

    return (*_load(next_project), *refresh_project_lists(next_project), gr.update(visible=False))
