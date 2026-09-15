"""Explicit project load — Gradio has no auto-resume, so this is a real button click."""

import gradio as gr

from src.persistence import chat_store, manuscript_store
from src.manuscript.versioning import format_label
from src.rag.vector_store import new_collection
from src.ui import state as ui_state


def load_project(user: str, project: str):
    user = (user or "").strip()
    project = (project or "").strip()

    if not user or not project:
        raise gr.Error("Enter both a user name and a project name.")

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
