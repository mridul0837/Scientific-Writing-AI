"""Build the Gradio Blocks layout and wire all events.

Single-dashboard layout: project setup and file uploads live in a collapsed
accordion (secondary, out of the way); chat and manuscript are always visible
side by side as the primary writing workspace.

Event wiring:
  Load Project button   -> project_events.load_project
  Papers .upload()      -> upload_events.process_papers
  Samples .upload()     -> upload_events.process_samples -> (.then) upload_events.learn_style
  Send click / Enter    -> chat_events.respond (generator, streaming)
  Revert button         -> manuscript_events.revert_version
  Add-to-manuscript btn -> manuscript_events.add_last_reply_to_manuscript
  Question popup option -> chat_events.select_option -> (.then) chat_events.respond

The question popup (src/questions.py protocol) has no native Gradio Modal in
this version, so it's a gr.Column toggled visible=True/False and pinned to
the viewport via CSS (see src/ui/theme.py's #question-modal rule).
"""

import gradio as gr

from config import MAX_ASK_OPTIONS
from src.ui import chat_events, manuscript_events, project_events, state as ui_state, upload_events


def build_layout() -> gr.Blocks:
    # theme/css/js are passed to demo.launch() in app.py (moved there in Gradio 6).
    with gr.Blocks(title="Scientific Writing AI") as demo:
        # --- cross-call session state ---
        state_user_project = gr.State(ui_state.initial_user_project())
        state_messages = gr.State(ui_state.initial_messages())
        state_papers = gr.State(ui_state.initial_papers())
        state_samples = gr.State(ui_state.initial_samples())
        state_style_profile = gr.State(ui_state.initial_style_profile())
        state_vector_collection = gr.State(None)
        state_manuscript_text = gr.State(ui_state.initial_manuscript_text())
        state_manuscript_versions = gr.State(ui_state.initial_manuscript_versions())

        with gr.Accordion("Project & Sources", open=False):
            with gr.Row():
                user_box = gr.Textbox(label="User name")
                project_box = gr.Textbox(label="Project name")
                load_btn = gr.Button("Load / Start Project", variant="primary")
            project_status = gr.Markdown()

            with gr.Row():
                with gr.Column():
                    papers_upload = gr.File(
                        label="Research Papers (1-10, PDF)",
                        file_count="multiple",
                        file_types=[".pdf"],
                    )
                    papers_status = gr.Markdown()

                with gr.Column():
                    samples_upload = gr.File(
                        label="Writing Samples (1-10, PDF/TXT/MD)",
                        file_count="multiple",
                        file_types=[".pdf", ".txt", ".md"],
                    )
                    samples_status = gr.Markdown()

        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="Scientific Writing AI", height=600)
                msg_box = gr.Textbox(label="Message", placeholder="Ask, write, rewrite, review...")
                send_btn = gr.Button("Send", variant="primary")
                with gr.Row():
                    section_name_box = gr.Textbox(
                        label="Section name",
                        placeholder="e.g. Introduction",
                        scale=3,
                    )
                    add_section_btn = gr.Button("Add last reply to manuscript", scale=2)

            with gr.Column(scale=1):
                manuscript_display = gr.Textbox(
                    label="Current manuscript", lines=20, interactive=False
                )
                versions_radio = gr.Radio(label="Version history (last 5)", choices=[])
                revert_btn = gr.Button("Revert to selected version")

        with gr.Column(visible=False, elem_id="question-modal") as question_modal:
            with gr.Column(elem_id="question-modal-card"):
                question_text = gr.Markdown()
                option_buttons = [
                    gr.Button(visible=False, elem_classes=["question-option-btn"])
                    for _ in range(MAX_ASK_OPTIONS)
                ]

        # --- Project ---
        load_btn.click(
            project_events.load_project,
            inputs=[user_box, project_box],
            outputs=[
                state_user_project,
                state_messages,
                state_papers,
                state_samples,
                state_style_profile,
                state_vector_collection,
                state_manuscript_text,
                state_manuscript_versions,
                chatbot,
                manuscript_display,
                versions_radio,
                papers_status,
                samples_status,
                project_status,
            ],
        )

        # --- Files ---
        papers_upload.upload(
            upload_events.process_papers,
            inputs=[papers_upload, state_papers, state_vector_collection],
            outputs=[state_papers, state_vector_collection, papers_status],
        )

        samples_upload.upload(
            upload_events.process_samples,
            inputs=[samples_upload, state_samples],
            outputs=[state_samples, samples_status],
        ).then(
            upload_events.learn_style,
            inputs=[state_samples, samples_status],
            outputs=[state_style_profile, samples_status],
        )

        # --- Chat ---
        chat_inputs = [
            msg_box,
            state_messages,
            state_manuscript_text,
            state_style_profile,
            state_vector_collection,
            state_manuscript_versions,
            state_user_project,
        ]
        chat_outputs = [
            chatbot,
            state_messages,
            manuscript_display,
            state_manuscript_text,
            versions_radio,
            state_manuscript_versions,
            msg_box,
            question_modal,
            question_text,
            *option_buttons,
        ]
        send_btn.click(chat_events.respond, inputs=chat_inputs, outputs=chat_outputs)
        msg_box.submit(chat_events.respond, inputs=chat_inputs, outputs=chat_outputs)

        for btn in option_buttons:
            btn.click(
                chat_events.select_option,
                inputs=[btn],
                outputs=[msg_box, question_modal],
            ).then(chat_events.respond, inputs=chat_inputs, outputs=chat_outputs)

        # --- Manuscript ---
        revert_btn.click(
            manuscript_events.revert_version,
            inputs=[versions_radio, state_manuscript_text, state_manuscript_versions, state_user_project],
            outputs=[state_manuscript_text, state_manuscript_versions, manuscript_display, versions_radio],
        )

        add_section_btn.click(
            manuscript_events.add_last_reply_to_manuscript,
            inputs=[section_name_box, state_messages, state_manuscript_text, state_manuscript_versions, state_user_project],
            outputs=[
                state_manuscript_text,
                state_manuscript_versions,
                manuscript_display,
                versions_radio,
                section_name_box,
            ],
        )

    return demo
