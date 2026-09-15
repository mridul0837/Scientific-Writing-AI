"""Revert the manuscript to a previously saved version."""

import gradio as gr

from src.manuscript.versioning import add_version, find_by_label, format_label
from src.persistence import manuscript_store


def revert_version(label, manuscript_text, versions, user_project):
    if not label:
        raise gr.Error("Select a version to revert to.")

    target = find_by_label(versions, label)
    if target is None:
        raise gr.Error("That version could no longer be found.")

    user, project = user_project["user"], user_project["project"]

    versions = add_version(versions, manuscript_text, note="reverted to earlier version")
    new_text = target["text"]

    manuscript_store.save_current(user, project, new_text)
    manuscript_store.save_versions(user, project, versions)

    choices = [format_label(v) for v in versions]
    return new_text, versions, new_text, gr.update(choices=choices, value=None)
