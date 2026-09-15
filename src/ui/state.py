"""Initial values for the gr.State components that hold cross-call session data.

Gradio has no ambient session dict like Streamlit's session_state — every
piece of data that must survive between event handlers is threaded through
explicit gr.State components (created in layout.py) using these defaults.
"""


def initial_user_project() -> dict:
    return {"user": None, "project": None}


def initial_messages() -> list:
    return []


def initial_papers() -> list:
    return []


def initial_samples() -> list:
    return []


def initial_style_profile() -> str:
    return ""


def initial_manuscript_text() -> str:
    return ""


def initial_manuscript_versions() -> list:
    return []
