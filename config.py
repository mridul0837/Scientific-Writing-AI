from pathlib import Path

CHAT_MODEL = "qwen2.5:7b-instruct"
EMBED_MODEL = "nomic-embed-text"

DATA_ROOT = Path(__file__).parent / "data" / "Scientific-Writing-AI"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
RETRIEVAL_TOP_K = 5
MAX_HISTORY_TURNS = 20
MAX_VERSIONS = 5

MANUSCRIPT_START_MARKER = "<<<MANUSCRIPT_START>>>"
MANUSCRIPT_END_MARKER = "<<<MANUSCRIPT_END>>>"
