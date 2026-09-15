"""Manuscript panel actions: revert to a previous version, and add the last
chat reply into the manuscript as a named section (verbatim — no re-generation,
so what you approved in chat is exactly what lands in the manuscript)."""

import gradio as gr

from src.manuscript.sections import replace_or_append_section
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


def add_last_reply_to_manuscript(section_name, messages, manuscript_text, versions, user_project):
    section_name = (section_name or "").strip()
    if not section_name:
        raise gr.Error("Enter a section name first.")
    if not user_project.get("user") or not user_project.get("project"):
        raise gr.Error("No project loaded — click + New in the sidebar.")

    last_reply = next(
        (m["content"] for m in reversed(messages) if m["role"] == "assistant" and m["content"].strip()),
        None,
    )
    if not last_reply:
        raise gr.Error("No assistant reply to add yet.")

    user, project = user_project["user"], user_project["project"]

    section_text = f"## {section_name}\n\n{last_reply.strip()}"
    versions = add_version(versions, manuscript_text, note=f"Added section: {section_name}")
    new_text = replace_or_append_section(manuscript_text, section_name, section_text)

    manuscript_store.save_current(user, project, new_text)
    manuscript_store.save_versions(user, project, versions)

    choices = [format_label(v) for v in versions]
    return new_text, versions, new_text, gr.update(choices=choices, value=None), ""
