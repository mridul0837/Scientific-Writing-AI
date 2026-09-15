"""Flat, dark, matte theme — the default Gradio look uses gradients and drop
shadows on buttons/blocks; every override below exists to flatten one of those."""

import gradio as gr

_BG = "#111317"
_PANEL = "#1a1d22"
_SURFACE = "#20242b"
_BORDER = "#2a2f37"
_TEXT = "#e6e7ea"
_TEXT_SUBDUED = "#9096a1"
_ACCENT = "#5b7ca8"
_ACCENT_HOVER = "#6d8fbc"

THEME = gr.themes.Base(
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    # Page + panels
    body_background_fill=_BG,
    body_background_fill_dark=_BG,
    body_text_color=_TEXT,
    body_text_color_dark=_TEXT,
    body_text_color_subdued=_TEXT_SUBDUED,
    body_text_color_subdued_dark=_TEXT_SUBDUED,
    background_fill_primary=_PANEL,
    background_fill_primary_dark=_PANEL,
    background_fill_secondary=_SURFACE,
    background_fill_secondary_dark=_SURFACE,
    border_color_primary=_BORDER,
    border_color_primary_dark=_BORDER,
    border_color_accent=_ACCENT,
    border_color_accent_dark=_ACCENT,
    color_accent=_ACCENT,
    color_accent_soft="#2a3542",
    color_accent_soft_dark="#2a3542",
    link_text_color=_ACCENT,
    link_text_color_dark=_ACCENT,
    # Flatten every shadow — this is the main source of the "shiny" look
    shadow_drop="none",
    shadow_drop_lg="none",
    shadow_spread="0",
    shadow_spread_dark="0",
    # Blocks / panels
    block_background_fill=_PANEL,
    block_background_fill_dark=_PANEL,
    block_border_color=_BORDER,
    block_border_color_dark=_BORDER,
    block_border_width="1px",
    block_shadow="none",
    block_shadow_dark="none",
    block_label_background_fill=_PANEL,
    block_label_background_fill_dark=_PANEL,
    block_label_border_color=_BORDER,
    block_label_border_color_dark=_BORDER,
    block_label_text_color=_TEXT_SUBDUED,
    block_label_text_color_dark=_TEXT_SUBDUED,
    block_title_text_color=_TEXT,
    block_title_text_color_dark=_TEXT,
    panel_background_fill=_PANEL,
    panel_background_fill_dark=_PANEL,
    panel_border_color=_BORDER,
    panel_border_color_dark=_BORDER,
    accordion_text_color=_TEXT,
    accordion_text_color_dark=_TEXT,
    block_radius="8px",
    # Inputs
    input_background_fill=_SURFACE,
    input_background_fill_dark=_SURFACE,
    input_border_color=_BORDER,
    input_border_color_dark=_BORDER,
    input_border_color_hover=_ACCENT,
    input_border_color_hover_dark=_ACCENT,
    input_shadow="none",
    input_shadow_dark="none",
    input_shadow_focus="none",
    input_shadow_focus_dark="none",
    input_placeholder_color=_TEXT_SUBDUED,
    input_placeholder_color_dark=_TEXT_SUBDUED,
    input_radius="6px",
    # Buttons — flat single colors, no gradients, no hover pop/shadow
    button_transform_hover="none",
    button_transform_active="none",
    button_large_radius="6px",
    button_medium_radius="6px",
    button_small_radius="6px",
    button_primary_background_fill=_ACCENT,
    button_primary_background_fill_dark=_ACCENT,
    button_primary_background_fill_hover=_ACCENT_HOVER,
    button_primary_background_fill_hover_dark=_ACCENT_HOVER,
    button_primary_border_color=_ACCENT,
    button_primary_border_color_dark=_ACCENT,
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
    button_primary_shadow="none",
    button_primary_shadow_hover="none",
    button_primary_shadow_active="none",
    button_primary_shadow_dark="none",
    button_primary_shadow_hover_dark="none",
    button_primary_shadow_active_dark="none",
    button_secondary_background_fill=_SURFACE,
    button_secondary_background_fill_dark=_SURFACE,
    button_secondary_background_fill_hover=_BORDER,
    button_secondary_background_fill_hover_dark=_BORDER,
    button_secondary_border_color=_BORDER,
    button_secondary_border_color_dark=_BORDER,
    button_secondary_text_color=_TEXT,
    button_secondary_text_color_dark=_TEXT,
    button_secondary_shadow="none",
    button_secondary_shadow_hover="none",
    button_secondary_shadow_active="none",
    button_secondary_shadow_dark="none",
    button_secondary_shadow_hover_dark="none",
    button_secondary_shadow_active_dark="none",
)

CSS = """
.gradio-container {
    background: %(bg)s !important;
    max-width: 1400px !important;
}
.gradio-container * {
    box-shadow: none !important;
}
#component-0 { background: %(bg)s !important; }
.chatbot { border-color: %(border)s !important; }

/* Claude-style messages: user gets a right-aligned tinted bubble, the
   assistant is plain text with no bubble — closer to a document than a
   chat log, which fits a writing tool better than two rows of bubbles. */
.chatbot .message.user {
    background: %(surface)s !important;
    color: %(text)s !important;
    border-radius: 14px !important;
    margin-left: auto !important;
}
.chatbot .message.bot {
    background: transparent !important;
    color: %(text)s !important;
    border: none !important;
    padding-left: 0 !important;
}

/* Question popup: no native Gradio Modal in this version, so this is a
   Column pinned over the viewport and toggled visible=True/False. */
#question-modal {
    position: fixed !important;
    inset: 0 !important;
    background: rgba(0, 0, 0, 0.6) !important;
    z-index: 1000 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
#question-modal-card {
    background: %(panel)s !important;
    border: 1px solid %(border)s !important;
    border-radius: 12px !important;
    padding: 24px !important;
    max-width: 480px !important;
    width: 90%% !important;
}
.question-option-btn {
    width: 100%% !important;
    text-align: left !important;
    margin-top: 8px !important;
}
""" % {"bg": _BG, "panel": _PANEL, "surface": _SURFACE, "border": _BORDER, "text": _TEXT}

FORCE_DARK_JS = """
() => {
    document.documentElement.classList.add('dark');
}
"""
