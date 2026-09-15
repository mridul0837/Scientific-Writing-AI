from src.ui.layout import build_layout
from src.ui.theme import CSS, FORCE_DARK_JS, THEME

if __name__ == "__main__":
    demo = build_layout()
    demo.queue()
    demo.launch(theme=THEME, css=CSS, js=FORCE_DARK_JS)
