"""Streaming chat handler: builds the prompt, streams the reply, and handles
the two things the model may emit instead of plain text:
  - a manuscript compile block (only when the user explicitly asked for the
    manuscript itself — see src/prompt_builder.py)
  - a multiple-choice clarifying question, rendered as a popup with option
    buttons (src/questions.py)
A plain "write this" request just gets a normal chat reply and triggers neither."""

import gradio as gr

from config import ASK_START_MARKER, MANUSCRIPT_START_MARKER, MAX_ASK_OPTIONS
from src.manuscript.manuscript_state import split_reply_and_edit
from src.manuscript.versioning import add_version, format_label
from src.ollama_client import chat_stream
from src.persistence import chat_store, manuscript_store
from src.prompt_builder import build_messages
from src.questions import split_reply_and_question

_HIDDEN_MODAL = (gr.update(visible=False), gr.update(), *([gr.update(visible=False)] * MAX_ASK_OPTIONS))
_NO_MODAL_CHANGE = (gr.update(),) * (2 + MAX_ASK_OPTIONS)


def _visible_prefix(buffer: str) -> str:
    cut_points = [buffer.find(m) for m in (MANUSCRIPT_START_MARKER, ASK_START_MARKER)]
    cut_points = [c for c in cut_points if c != -1]
    return buffer if not cut_points else buffer[: min(cut_points)]


def _question_modal_outputs(question: dict | None):
    if question is None:
        return _HIDDEN_MODAL
    question_md = gr.update(value=f"**{question['question']}**")
    button_updates = []
    for i in range(MAX_ASK_OPTIONS):
        if i < len(question["options"]):
            button_updates.append(gr.update(value=question["options"][i], visible=True))
        else:
            button_updates.append(gr.update(visible=False))
    return (gr.update(visible=True), question_md, *button_updates)


def respond(user_message, messages, manuscript_text, style_profile, collection, versions, user_project):
    user_message = (user_message or "").strip()
    if not user_message:
        yield messages, messages, manuscript_text, manuscript_text, gr.update(), versions, "", *_NO_MODAL_CHANGE
        return
    if not user_project.get("user") or not user_project.get("project"):
        raise gr.Error("No project loaded — click + New in the sidebar.")

    user, project = user_project["user"], user_project["project"]

    history = list(messages)
    messages = history + [{"role": "user", "content": user_message}]
    chat_store.save(user, project, messages)

    # Show the user's turn immediately; hide any stale question popup from a prior turn.
    messages = messages + [{"role": "assistant", "content": ""}]
    yield messages, messages, manuscript_text, manuscript_text, gr.update(), versions, "", *_HIDDEN_MODAL

    llm_messages = build_messages(user_message, manuscript_text, style_profile, history, collection)

    full_buffer = ""
    for chunk in chat_stream(llm_messages):
        full_buffer += chunk
        messages[-1]["content"] = _visible_prefix(full_buffer) or "…"
        yield messages, messages, manuscript_text, manuscript_text, gr.update(), versions, "", *_NO_MODAL_CHANGE

    question = None
    new_manuscript = None
    if ASK_START_MARKER in full_buffer:
        reply, question = split_reply_and_question(full_buffer)
    elif MANUSCRIPT_START_MARKER in full_buffer:
        reply, new_manuscript = split_reply_and_edit(full_buffer)
    else:
        reply = full_buffer.strip()

    messages[-1]["content"] = reply or "…"

    versions_update = gr.update()
    if new_manuscript is not None:
        versions = add_version(versions, manuscript_text, note="Manuscript compiled")
        manuscript_text = new_manuscript
        manuscript_store.save_current(user, project, manuscript_text)
        manuscript_store.save_versions(user, project, versions)
        messages[-1]["content"] = f"{reply}\n\n_Manuscript updated — see panel._"
        versions_update = gr.update(choices=[format_label(v) for v in versions], value=None)

    chat_store.save(user, project, messages)

    modal_outputs = _question_modal_outputs(question)
    yield messages, messages, manuscript_text, manuscript_text, versions_update, versions, "", *modal_outputs


def select_option(option_text: str):
    """Fired by a popup option button: fills the message box with the chosen
    option and closes the popup; the caller chains this into respond()."""
    return option_text, gr.update(visible=False)
