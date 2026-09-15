import getpass
from pathlib import Path

CHAT_MODEL = "qwen2.5:7b-instruct"
EMBED_MODEL = "nomic-embed-text"

# Ollama's default keep_alive (5 min) unloads the model between messages during
# normal back-and-forth chatting, costing a ~7s reload on the next message
# (measured). Keep it warm for the length of a realistic working session instead.
OLLAMA_KEEP_ALIVE = "30m"

DATA_ROOT = Path(__file__).parent / "data" / "Scientific-Writing-AI"

# Single-user local tool (multi-user accounts are out of scope for this MVP) —
# one fixed folder name under DATA_ROOT instead of a UI field to fill in.
try:
    LOCAL_USER = getpass.getuser()
except Exception:
    LOCAL_USER = "local"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
RETRIEVAL_TOP_K = 5
MAX_HISTORY_TURNS = 20
MAX_VERSIONS = 5

MANUSCRIPT_START_MARKER = "<<<MANUSCRIPT_START>>>"
MANUSCRIPT_END_MARKER = "<<<MANUSCRIPT_END>>>"

# Multiple-choice clarifying question, rendered as a popup with option buttons.
ASK_START_MARKER = "<<<ASK_START>>>"
ASK_END_MARKER = "<<<ASK_END>>>"
MAX_ASK_OPTIONS = 4
