"""Build the Gradio Blocks layout and wire all events.

No user-facing project-name entry: there's a single fixed local user
(config.LOCAL_USER), and projects are named/switched entirely through the
sidebar — resumed automatically on page load, created via "+ New", switched
by clicking an entry. File uploads live in a collapsed accordion (secondary,
out of the way); chat and manuscript are always visible side by side as the
primary writing workspace.

Event wiring:
  demo.load()            -> project_events.startup (resume most recent, or create the first one)
  "+ New" button         -> project_events.create_new_project
  Sidebar entry click    -> project_events.select_project (pinned or unpinned list)
  Pin/Unpin button       -> project_events.toggle_pin
  Delete button          -> project_events.request_delete -> (confirm) confirm_delete / (cancel) cancel_delete
  Chat-bar attach button -> upload_events.process_papers (papers only; writing samples stay in Files)
  Papers/Samples .upload()  (Files section) -> upload_events.process_papers / process_samples -> (.then) learn_style
  Send click / Enter     -> chat_events.respond (generator, streaming)
  Revert button          -> manuscript_events.revert_version
  Add-to-manuscript btn  -> manuscript_events.add_last_reply_to_manuscript
  Question popup option  -> chat_events.select_option -> (.then) chat_events.respond

Two popups have no native Gradio Modal in this version, so each is a
gr.Column toggled visible=True/False and pinned to the viewport via CSS
(see src/ui/theme.py's #question-modal / #delete-modal rules): the
clarifying-question popup (src/questions.py protocol) and the delete
confirmation.
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

        with gr.Row():
            with gr.Column(scale=1, min_width=200, elem_id="history-sidebar"):
                new_project_btn = gr.Button("+  New", elem_id="new-project-btn")

                with gr.Column(visible=False, elem_id="pinned-section") as pinned_section:
                    gr.Markdown("Pinned", elem_id="sidebar-header")
                    pinned_radio = gr.Radio(choices=[], show_label=False, elem_id="pinned-list")

                gr.Markdown("Chats", elem_id="sidebar-header")
                projects_radio = gr.Radio(choices=[], show_label=False, elem_id="projects-list")

                with gr.Row(elem_id="chat-actions-row"):
                    pin_btn = gr.Button("📌 Pin", size="sm", elem_id="pin-btn")
                    delete_btn = gr.Button("🗑 Delete", size="sm", elem_id="delete-btn")

            with gr.Column(scale=5):
                chat_header = gr.Markdown("", elem_id="chat-header")
                with gr.Accordion("📎 Files", open=False, elem_id="project-bar"):
                    with gr.Row():
                        with gr.Column():
                            papers_upload = gr.File(
                                label="Research papers (1-10, PDF)",
                                file_count="multiple",
                                file_types=[".pdf"],
                            )
                            papers_status = gr.Markdown()

                        with gr.Column():
                            samples_upload = gr.File(
                                label="Writing samples (1-10, PDF/TXT/MD)",
                                file_count="multiple",
                                file_types=[".pdf", ".txt", ".md"],
                            )
                            samples_status = gr.Markdown()

                with gr.Row():
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(label="Scientific Writing AI", show_label=False, height=560)
                        with gr.Row(elem_id="chat-input-row"):
                            attach_btn = gr.UploadButton(
                                "📎",
                                file_count="multiple",
                                file_types=[".pdf"],
                                scale=0,
                                elem_id="attach-btn",
                            )
                            msg_box = gr.Textbox(
                                show_label=False,
                                placeholder="Ask, write, rewrite, review...",
                                scale=6,
                                container=False,
                            )
                            send_btn = gr.Button("↑", variant="primary", scale=0, elem_id="send-btn")
                        attach_status = gr.Markdown(elem_id="attach-status")
                        with gr.Row(elem_id="add-section-row"):
                            section_name_box = gr.Textbox(
                                show_label=False,
                                placeholder="Section name (e.g. Introduction)",
                                scale=3,
                                container=False,
                            )
                            add_section_btn = gr.Button("+ Add to manuscript", variant="secondary", scale=2, size="sm")
                        gr.Markdown(
                            "This assistant can make mistakes — check important information.",
                            elem_id="chat-disclaimer",
                        )

                    with gr.Column(scale=1, elem_id="manuscript-card"):
                        gr.Markdown("📄 Manuscript", elem_id="manuscript-header")
                        manuscript_display = gr.Textbox(
                            show_label=False, lines=18, interactive=False, container=False
                        )
                        with gr.Accordion("Version history", open=False, elem_id="versions-accordion"):
                            versions_radio = gr.Radio(show_label=False, choices=[])
                            revert_btn = gr.Button("Revert to selected version", variant="secondary", size="sm")

        with gr.Column(visible=False, elem_id="question-modal") as question_modal:
            with gr.Column(elem_id="question-modal-card"):
                question_text = gr.Markdown()
                option_buttons = [
                    gr.Button(visible=False, elem_classes=["question-option-btn"])
                    for _ in range(MAX_ASK_OPTIONS)
                ]

        with gr.Column(visible=False, elem_id="delete-modal") as delete_modal:
            with gr.Column(elem_id="delete-modal-card"):
                delete_confirm_text = gr.Markdown()
                with gr.Row():
                    cancel_delete_btn = gr.Button("Cancel", variant="secondary")
                    confirm_delete_btn = gr.Button("Delete permanently", variant="stop")

        # --- Project ---
        load_outputs = [
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
            chat_header,
            pin_btn,
        ]
        project_switch_outputs = [*load_outputs, pinned_section, pinned_radio, projects_radio]

        demo.load(project_events.startup, outputs=project_switch_outputs)

        new_project_btn.click(project_events.create_new_project, outputs=project_switch_outputs)

        pinned_radio.change(
            project_events.select_project,
            inputs=[pinned_radio],
            outputs=project_switch_outputs,
        )
        projects_radio.change(
            project_events.select_project,
            inputs=[projects_radio],
            outputs=project_switch_outputs,
        )

        pin_btn.click(
            project_events.toggle_pin,
            inputs=[state_user_project],
            outputs=[pinned_section, pinned_radio, projects_radio, pin_btn],
        )

        delete_btn.click(
            project_events.request_delete,
            inputs=[state_user_project],
            outputs=[delete_modal, delete_confirm_text],
        )
        cancel_delete_btn.click(project_events.cancel_delete, outputs=[delete_modal])
        confirm_delete_btn.click(
            project_events.confirm_delete,
            inputs=[state_user_project],
            outputs=[*project_switch_outputs, delete_modal],
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

        attach_btn.upload(
            upload_events.process_papers,
            inputs=[attach_btn, state_papers, state_vector_collection],
            outputs=[state_papers, state_vector_collection, attach_status],
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
