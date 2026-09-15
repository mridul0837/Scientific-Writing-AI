"""Warm, borderless, spacious theme modeled on Claude.ai's chat + side-panel
look: no visible borders on messages/panels (separation via shade and
whitespace, not lines), soft rounded corners, warm neutral palette instead of
cool gray, no gradients/shadows."""

import gradio as gr

_BG = "#1f1e1d"
_PANEL = "#282725"
_SURFACE = "#33312e"
_BORDER = "#3d3a36"
_TEXT = "#f2efe9"
_TEXT_SUBDUED = "#a39d92"
_ACCENT = "#cc7a54"
_ACCENT_HOVER = "#d98f6c"

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
    color_accent_soft="#3a2e28",
    color_accent_soft_dark="#3a2e28",
    link_text_color=_ACCENT,
    link_text_color_dark=_ACCENT,
    shadow_drop="none",
    shadow_drop_lg="none",
    shadow_spread="0",
    shadow_spread_dark="0",
    # Blocks / panels — no borders by default; panels that need separation get
    # one explicitly via CSS below (e.g. the manuscript card, the popup card)
    block_background_fill="none",
    block_background_fill_dark="none",
    block_border_width="0px",
    block_border_width_dark="0px",
    block_shadow="none",
    block_shadow_dark="none",
    block_label_background_fill="none",
    block_label_background_fill_dark="none",
    block_label_border_width="0px",
    block_label_text_color=_TEXT_SUBDUED,
    block_label_text_color_dark=_TEXT_SUBDUED,
    block_title_text_color=_TEXT,
    block_title_text_color_dark=_TEXT,
    panel_background_fill="none",
    panel_background_fill_dark="none",
    panel_border_width="0px",
    accordion_text_color=_TEXT_SUBDUED,
    accordion_text_color_dark=_TEXT_SUBDUED,
    block_radius="16px",
    layout_gap="20px",
    # Inputs — soft, borderless, pill-friendly
    input_background_fill=_SURFACE,
    input_background_fill_dark=_SURFACE,
    input_border_color=_SURFACE,
    input_border_color_dark=_SURFACE,
    input_border_color_hover=_ACCENT,
    input_border_color_hover_dark=_ACCENT,
    input_border_width="1px",
    input_shadow="none",
    input_shadow_dark="none",
    input_shadow_focus="none",
    input_shadow_focus_dark="none",
    input_placeholder_color=_TEXT_SUBDUED,
    input_placeholder_color_dark=_TEXT_SUBDUED,
    input_radius="18px",
    # Buttons — flat single colors, no gradients, no hover pop/shadow
    button_transform_hover="none",
    button_transform_active="none",
    button_border_width="0px",
    button_large_radius="18px",
    button_medium_radius="14px",
    button_small_radius="10px",
    button_primary_background_fill=_ACCENT,
    button_primary_background_fill_dark=_ACCENT,
    button_primary_background_fill_hover=_ACCENT_HOVER,
    button_primary_background_fill_hover_dark=_ACCENT_HOVER,
    button_primary_text_color="#241c17",
    button_primary_text_color_dark="#241c17",
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

/* --- Top utility bar: project/upload controls, kept small and out of the way --- */
#project-bar {
    border-bottom: 1px solid %(border)s !important;
    margin-bottom: 8px !important;
    padding-bottom: 4px !important;
}
#project-bar .label-wrap {
    font-size: 13px !important;
    color: %(subdued)s !important;
}

/* --- Left sidebar: a Claude-style vertical list of past projects, not a
   row of pill buttons (gr.Radio's default look) --- */
#history-sidebar {
    background: %(panel)s !important;
    border-radius: 16px !important;
    padding: 12px !important;
    align-self: flex-start !important;
}
#sidebar-header-row {
    align-items: center !important;
    margin-bottom: 8px !important;
}
#sidebar-header {
    font-size: 13px !important;
    color: %(subdued)s !important;
    padding: 0 8px !important;
    margin: 0 !important;
}
#new-project-btn {
    min-width: 0 !important;
    background: %(surface)s !important;
    color: %(text)s !important;
}
#projects-list .wrap {
    flex-direction: column !important;
    gap: 2px !important;
}
#projects-list label {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px !important;
    justify-content: flex-start !important;
    font-size: 13px !important;
    color: %(text)s !important;
}
#projects-list label:hover {
    background: %(surface)s !important;
}
#projects-list label.selected {
    background: %(accent_soft)s !important;
}
#projects-list input[type="radio"] {
    display: none !important;
}

/* --- Chat column: no card/border around the log, generous side padding,
   Claude-style messages (right-aligned tinted user bubble, bubble-less
   assistant text) --- */
.chatbot {
    border: none !important;
    background: transparent !important;
}
.chatbot .message-wrap { padding: 0 12px !important; }
.chatbot .message.user {
    background: %(surface)s !important;
    color: %(text)s !important;
    border-radius: 18px !important;
    margin-left: auto !important;
    max-width: 75%% !important;
}
.chatbot .message.bot {
    background: transparent !important;
    color: %(text)s !important;
    border: none !important;
    padding-left: 4px !important;
    max-width: 90%% !important;
}

/* --- Pill-shaped message input row --- */
#chat-input-row {
    background: %(surface)s !important;
    border-radius: 26px !important;
    padding: 6px 6px 6px 20px !important;
    align-items: center !important;
    gap: 8px !important;
}
#chat-input-row textarea, #chat-input-row input {
    background: transparent !important;
    border: none !important;
}
#send-btn {
    min-width: 42px !important;
    width: 42px !important;
    height: 42px !important;
    border-radius: 999px !important;
    padding: 0 !important;
    flex: none !important;
}

/* --- Manuscript panel styled as a Claude-artifact-style card --- */
#manuscript-card {
    background: %(panel)s !important;
    border-radius: 16px !important;
    padding: 16px !important;
}
#manuscript-header {
    font-size: 14px !important;
    color: %(subdued)s !important;
    margin-bottom: 4px !important;
}
#manuscript-card textarea {
    background: transparent !important;
    border: none !important;
    color: %(text)s !important;
}

/* --- "Add to manuscript" — a quiet inline control, not a heavy labeled row --- */
#add-section-row { align-items: center !important; gap: 6px !important; }
#add-section-row input { background: %(surface)s !important; border-radius: 14px !important; }

/* --- Question popup: no native Gradio Modal in this version, so this is a
   Column pinned over the viewport and toggled visible=True/False. --- */
#question-modal {
    position: fixed !important;
    inset: 0 !important;
    background: rgba(20, 18, 16, 0.7) !important;
    z-index: 1000 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
#question-modal-card {
    background: %(panel)s !important;
    border-radius: 20px !important;
    padding: 28px !important;
    max-width: 480px !important;
    width: 90%% !important;
}
.question-option-btn {
    width: 100%% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    margin-top: 8px !important;
    background: %(surface)s !important;
    color: %(text)s !important;
}
.question-option-btn:hover {
    background: %(accent_soft)s !important;
}
""" % {
    "bg": _BG,
    "panel": _PANEL,
    "surface": _SURFACE,
    "border": _BORDER,
    "text": _TEXT,
    "subdued": _TEXT_SUBDUED,
    "accent_soft": "#3a2e28",
}

FORCE_DARK_JS = """
() => {
    document.documentElement.classList.add('dark');
}
"""
