# Scientific Writing AI — Agent Instructions

Local-first assistant for scientific writing: a Gradio chat UI backed by a local Ollama LLM, with RAG over uploaded papers, writing-style mimicry, and direct manuscript editing with version history. See `Features.md` for the full product vision and `~/.claude/plans` history for how the current milestone was scoped (or just read this file — it's kept current).

## Current milestone

This is the **first local MVP**, not the full `Features.md` spec. Built and working:

- Gradio chat (streaming) against Ollama
- RAG over uploaded PDF papers (session-only, never persisted)
- Style mimicry from uploaded writing samples (session-only)
- Direct manuscript editing via a text-marker protocol, with a 5-version history and revert
- Local-disk persistence shaped like the eventual Google Drive layout

**Not built yet** — don't assume these exist: citations/APA workflow, language/scientific review modes, web-research toggle, Word/LaTeX/PDF export, real Google Drive API integration, multi-user accounts, fine-tuning, multi-agent orchestration. If asked to add one of these, treat it as new work, not a bug fix.

## Stack

- Python 3.11, conda env named `sciwriting`
- UI: `gradio` (Blocks) — **not** Streamlit, despite `Features.md` saying Streamlit; that decision was overridden early on
- LLM: local Ollama, model `qwen2.5:7b-instruct`, embeddings via `nomic-embed-text` (both configured in `config.py`)
- Vector store: `chromadb` `EphemeralClient` (in-memory, per-session, never written to disk)
- PDF parsing: `pypdf`
- No RAG/agent framework (no LangChain/LlamaIndex) — everything is hand-rolled and direct. Keep it that way unless the scope genuinely outgrows it; don't introduce a framework for its own sake.

## Project structure

```
app.py                  entrypoint — builds the Blocks layout, demo.queue().launch()
config.py                model names, paths, chunk size/overlap, top_k, max_versions
src/
  ollama_client.py       thin wrapper: chat_stream(), embed() — the ONLY place that calls Ollama.
                          Keep it that way: it's the seam for swapping in a hosted API later.
  prompt_builder.py       assembles the per-turn messages list (system + style + manuscript + RAG + history)
  rag/                    pdf_parser.py, chunker.py, vector_store.py, retriever.py
  style/style_profile.py  LLM-based style summarization from writing samples
  manuscript/
    manuscript_state.py   parses the <<<MANUSCRIPT_START>>>/<<<MANUSCRIPT_END>>> marker protocol
    versioning.py          in-memory version list management, capped at MAX_VERSIONS (5)
  persistence/
    storage.py             path resolution + list_users()/list_projects() — the ONLY place that
                            builds on-disk paths. Keep it that way: it's the seam for swapping in
                            real Google Drive later.
    chat_store.py, manuscript_store.py   save/load JSON and manuscript files through storage.py
  ui/
    state.py               initial values for gr.State components (Gradio has no session_state)
    layout.py               builds the gr.Blocks layout, wires every event — read this first to see
                             how the pieces connect
    chat_events.py          respond() — the streaming generator that drives the whole chat turn
    upload_events.py, manuscript_events.py, project_events.py
data/                      local persistence root, gitignored — never commit this
```

## Conventions

- Data flow for one chat turn: `chat_events.respond()` → `prompt_builder.build_messages()` (pulls in RAG context via `retriever.py` and style profile) → `ollama_client.chat_stream()` → `manuscript_state.split_reply_and_edit()` to detect an edit → `versioning.add_version()` + `persistence/manuscript_store.py` to save it. Trace this path before changing any one piece of it.
- Gradio has **no ambient session state**. Every value that must survive between event handlers is an explicit `gr.State` in `layout.py`, threaded through `inputs=`/`outputs=` on every handler. When adding a new piece of cross-call state, add it to `ui/state.py` and thread it through in `layout.py` — don't reach for globals.
- The manuscript-edit protocol is plain text (`<<<MANUSCRIPT_START>>>` / `<<<MANUSCRIPT_END>>>`), not function-calling — quantized 7B models are unreliable at tool-calling. The model can (and does) write follow-up text after the closing marker; `manuscript_state.split_reply_and_edit()` folds that back into the visible reply rather than discarding it. Don't reintroduce that bug.
- Uploaded papers and writing samples are session-only by design (matches `Features.md`). Never add code that writes them under `data/`.
- No comments explaining *what* code does — only ones explaining a non-obvious *why* (there are a couple already, e.g. in `ollama_client.py` and `manuscript_state.py`). Match that style.
- Don't add a feature from the "not built yet" list above without it being an explicit ask — this file will be out of date the moment one of them lands, so update it in the same change.

## Setup

```
conda create -n sciwriting python=3.11 -y
conda activate sciwriting
pip install -r requirements.txt
ollama pull qwen2.5:7b-instruct
ollama pull nomic-embed-text
```

## Running

```
conda activate sciwriting
python app.py
```
Opens at `http://127.0.0.1:7860`.

## Verifying a change

There is no automated test suite yet — verify manually:

1. Launch the app, load a project (user + project name) — confirms `data/Scientific-Writing-AI/<user>/<project>/{Manuscript,Chat,Versions}` gets created.
2. Upload a PDF paper, ask a question about its content — confirms parsing/chunking/embedding/retrieval.
3. Upload a writing sample, ask for a rewrite "in my style" — confirms style extraction.
4. Ask for a manuscript edit — confirms the manuscript panel updates and a version is added.
5. Make 6+ edits — confirms only the last 5 versions are kept.
6. Revert to an older version — confirms it restores correctly and is itself recorded as a new version.
7. Restart the app, reload the browser, reload the same project — confirms chat/manuscript/versions reload from disk, and papers/samples do **not** persist.

For quick non-UI checks, `gradio_client.Client` can hit the app's endpoints directly (`/load_project`, `/respond`, `/revert_version`, etc.) without a browser — see git history around the initial scaffold commit for example usage.

## Git

- Remote: `https://github.com/mridul0837/Scientific-Writing-AI.git`, branch `main`.
- `data/` and `.claude/` are gitignored — never commit either.
