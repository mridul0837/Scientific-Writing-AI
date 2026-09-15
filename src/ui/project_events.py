"""Explicit project load — Gradio has no auto-resume, so this is a real button
click (or a click on a project in the sidebar list)."""

import gradio as gr

from src.manuscript.versioning import format_label
from src.persistence import chat_store, manuscript_store, storage
from src.rag.vector_store import new_collection
from src.ui import state as ui_state

_LABEL_SEP = "  —  "


def _project_label(user: str, project: str) -> str:
    return f"{project}{_LABEL_SEP}{user}"


def _parse_label(label: str) -> tuple[str, str]:
    project, _, user = label.partition(_LABEL_SEP)
    return user.strip(), project.strip()


def refresh_project_list():
    choices = [_project_label(user, project) for user, project in storage.list_all_projects()]
    return gr.update(choices=choices)


def _load(user: str, project: str):
    messages = chat_store.load(user, project)
    manuscript_text = manuscript_store.load_current(user, project)
    versions = manuscript_store.load_versions(user, project)
    collection = new_collection()

    versions_choices = [format_label(v) for v in versions]
    status = f"Loaded project **{project}** for **{user}**. Papers/writing samples are session-only and start empty."

    return (
        {"user": user, "project": project},   # state_user_project
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
        status,                                # project_status
    )


def load_project(user: str, project: str):
    user = (user or "").strip()
    project = (project or "").strip()

    if not user or not project:
        raise gr.Error("Enter both a user name and a project name.")

    return _load(user, project)


def select_project(label: str):
    if not label:
        raise gr.Error("Select a project from the list.")

    user, project = _parse_label(label)
    return (*_load(user, project), user, project)
