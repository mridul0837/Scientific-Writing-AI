"""Streaming chat handler: builds the prompt, streams the reply, and applies
any manuscript edit the model emits via the MANUSCRIPT_START/END marker protocol."""

import gradio as gr

from config import MANUSCRIPT_START_MARKER
from src.manuscript.manuscript_state import split_reply_and_edit
from src.manuscript.versioning import add_version, format_label
from src.ollama_client import chat_stream
from src.persistence import chat_store, manuscript_store
from src.prompt_builder import build_messages


def respond(user_message, messages, manuscript_text, style_profile, collection, versions, user_project):
    user_message = (user_message or "").strip()
    if not user_message:
        yield messages, messages, manuscript_text, manuscript_text, gr.update(), versions, ""
        return
    if not user_project.get("user") or not user_project.get("project"):
        raise gr.Error("Load a project first (Project tab).")

    user, project = user_project["user"], user_project["project"]

    history = list(messages)
    messages = history + [{"role": "user", "content": user_message}]
    chat_store.save(user, project, messages)

    # Show the user's turn immediately, with an empty assistant bubble to fill in.
    messages = messages + [{"role": "assistant", "content": ""}]
    yield messages, messages, manuscript_text, manuscript_text, gr.update(), versions, ""

    llm_messages = build_messages(user_message, manuscript_text, style_profile, history, collection)

    full_buffer = ""
    for chunk in chat_stream(llm_messages):
        full_buffer += chunk
        visible = full_buffer.split(MANUSCRIPT_START_MARKER)[0]
        messages[-1]["content"] = visible or "…"
        yield messages, messages, manuscript_text, manuscript_text, gr.update(), versions, ""

    reply, new_manuscript = split_reply_and_edit(full_buffer)
    messages[-1]["content"] = reply

    versions_update = gr.update()
    if new_manuscript is not None:
        versions = add_version(versions, manuscript_text, note="AI edit")
        manuscript_text = new_manuscript
        manuscript_store.save_current(user, project, manuscript_text)
        manuscript_store.save_versions(user, project, versions)
        messages[-1]["content"] = f"{reply}\n\n_Manuscript updated — see panel._"
        versions_update = gr.update(choices=[format_label(v) for v in versions], value=None)

    chat_store.save(user, project, messages)

    yield messages, messages, manuscript_text, manuscript_text, versions_update, versions, ""
