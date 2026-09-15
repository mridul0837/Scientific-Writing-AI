# Scientific Writing AI — Agent Instructions

Local-first assistant for scientific writing: a Gradio chat UI backed by a local Ollama LLM, with RAG over uploaded papers, writing-style mimicry, and an incrementally-built manuscript with version history. See `Features.md` for the full product vision and `~/.claude/plans` history for how the current milestone was scoped (or just read this file — it's kept current).

## Current milestone

This is the **first local MVP**, not the full `Features.md` spec. Built and working:

- Gradio chat (streaming) against Ollama, single dark dashboard (no tabs) — see `src/ui/theme.py`, `src/ui/layout.py`
- RAG over uploaded PDF papers (session-only, never persisted)
- Style mimicry from uploaded writing samples (session-only)
- A manuscript built up deliberately, not automatically — see "Manuscript model" below — with a 5-version history and revert
- Local-disk persistence shaped like the eventual Google Drive layout

**Not built yet** — don't assume these exist: citations/APA workflow, language/scientific review modes, web-research toggle, Word/LaTeX/PDF export, real Google Drive API integration, multi-user accounts, fine-tuning, multi-agent orchestration. If asked to add one of these, treat it as new work, not a bug fix.

## Stack

- Python 3.11, conda env named `sciwriting`
- UI: `gradio` (Blocks) — **not** Streamlit, despite `Features.md` saying Streamlit; that decision was overridden early on
- LLM: local Ollama, model `qwen2.5:7b-instruct`, embeddings via `nomic-embed-text` (both configured in `config.py`)
- Vector store: `chromadb` `EphemeralClient` (in-memory, per-session, never written to disk)
- PDF parsing: `pypdf`
- No RAG/agent framework (no LangChain/LlamaIndex) — everything is hand-rolled and direct. Keep it that way unless the scope genuinely outgrows it; don't introduce a framework for its own sake.
- No user-facing account system — `config.LOCAL_USER` (defaults to the OS username) is the one fixed folder name under `DATA_ROOT`. There is no username/project-name entry in the UI at all; projects are entirely sidebar-driven (see `project_events.py`). Don't reintroduce manual name entry — multi-user accounts are explicitly out of scope.
- On this dev machine, `qwen2.5:7b-instruct` doesn't fully fit in the RTX 3060 Laptop's 6GB VRAM (`ollama ps` shows an ~18%/82% CPU/GPU split) — inference is inherently slower than a fully-GPU model, and that's a hardware limit, not an app bug. Ollama's default `keep_alive` (5 min) was also unloading the model between messages during normal chat pauses, costing a measured ~7s reload on the next message; `config.OLLAMA_KEEP_ALIVE` ("30m") fixes that specific cost. If someone reports slowness, check `ollama ps` for the CPU/GPU split and whether the model is still loaded before assuming it's a code problem.

## Project structure

```
app.py                  entrypoint — builds the Blocks layout, demo.queue().launch(theme=..., css=..., js=...)
config.py                model names, paths, chunk size/overlap, top_k, max_versions
src/
  ollama_client.py       thin wrapper: chat_stream(), embed() — the ONLY place that calls Ollama.
                          Keep it that way: it's the seam for swapping in a hosted API later.
  prompt_builder.py       assembles the per-turn messages list (system + style + manuscript + RAG + history)
  rag/                    pdf_parser.py, chunker.py, vector_store.py, retriever.py
  style/style_profile.py  LLM-based style summarization from writing samples
  questions.py             parses the <<<ASK_START>>>/<<<ASK_END>>> clarifying-question popup protocol
  manuscript/
    manuscript_state.py   parses the <<<MANUSCRIPT_START>>>/<<<MANUSCRIPT_END>>> full-compile marker
    sections.py            finds/replaces one markdown-heading section, for the incremental "add to
                            manuscript" path — merges without touching the rest of the document
    versioning.py          in-memory version list management, capped at MAX_VERSIONS (5)
  persistence/
    storage.py             path resolution + list_projects_by_recency() — the ONLY place that builds
                            on-disk paths. Keep it that way: it's the seam for swapping in real
                            Google Drive later.
    chat_store.py, manuscript_store.py   save/load JSON and manuscript files through storage.py
  ui/
    theme.py                neutral near-black theme modeled directly on a Claude desktop app
                             screenshot (true gray, not warm-tinted; borderless spacious messages;
                             green accent kept by explicit request over the reference's blue),
                             gr.Theme overrides + CSS + force-dark JS, passed into demo.launch() in
                             app.py — not into gr.Blocks() (moved in Gradio 6)
    state.py                initial values for gr.State components (Gradio has no session_state)
    layout.py               builds the gr.Blocks layout, wires every event — read this first to see
                             how the pieces connect. Layout: a persistent left sidebar (Pinned section
                             + Chats list, "+ New" button, Pin/Delete row) next to the main column (a
                             collapsed "📎 Files" accordion for uploads above an always-visible
                             chat+manuscript row), plus two popup Columns pinned over the viewport
                             via CSS (clarifying-question, delete-confirmation)
    chat_events.py          respond() — the streaming generator that drives the whole chat turn;
                             select_option() — fired by a popup button, feeds its label back into respond()
    project_events.py       startup() (demo.load — resume most recent project or create the first
                             one), create_new_project() ("+ New"), select_project() (sidebar click),
                             toggle_pin(), request_delete()/cancel_delete()/confirm_delete() — all
                             funnel through a shared _load() helper and refresh_project_lists()
    upload_events.py        process_papers() also backs the chat-bar attach button (gr.UploadButton),
                             not just the Files-section upload — same handler, two entry points
    manuscript_events.py
data/                      local persistence root, gitignored — never commit this
```

## Manuscript model

Chat and the manuscript are deliberately decoupled — a "write X" request is answered in chat only, on purpose:

- **Default: plain chat.** Asking the model to write, rewrite, or improve something (a paragraph, a section, anything) just gets a normal chat reply. It does **not** touch the manuscript. This was a deliberate correction — an earlier version treated any writing-sounding request as an implicit edit, and the 7B model started rewriting sections unprompted (even on pure feedback questions like "what's missing here?"). Do not reintroduce silent/inferred edits.
- **Explicit full compile.** Only when the user clearly asks to see/get/compile the manuscript itself (e.g. "show me the manuscript") does the model emit the `<<<MANUSCRIPT_START>>>...<<<MANUSCRIPT_END>>>` block, assembling one full document from the conversation. `manuscript_state.split_reply_and_edit()` parses this.
- **Explicit incremental add.** The primary way the manuscript actually gets built: the user reviews a chat reply, names a section in the UI, and clicks "Add last reply to manuscript" (`manuscript_events.add_last_reply_to_manuscript`). That takes the **exact, verbatim** text of the last assistant message — no re-generation, so there's no risk of the model drifting from what the user already approved — and merges it into the manuscript at that heading via `sections.replace_or_append_section()` (replacing an existing section with the same heading, or appending a new one). This is the "build it part by part" path the user asked for, instead of regenerating the whole manuscript on every change.

## Clarifying-question popup

When the model hits a real fork it can't resolve on its own (not an open-ended question — a small, concrete set of options), it can emit `<<<ASK_START>>>Question: ...\nOptions: a | b | c<<<ASK_END>>>` instead of plain text (see the prompt in `prompt_builder.py`). `src/questions.py` parses this; `chat_events._question_modal_outputs()` turns it into a popup: a `gr.Column` (`#question-modal` in `layout.py`) toggled visible, pinned over the viewport via CSS in `theme.py` (Gradio has no native Modal component in this version), with up to `MAX_ASK_OPTIONS` (4) buttons labeled from the parsed options. Clicking one (`chat_events.select_option`) fills the message box with that option's text and closes the popup, then chains via `.then()` into `chat_events.respond` as if the user had typed and sent it. `Column`/`Button` outputs don't appear in `gradio_client`'s API view (`skip_api=True` on both) — that's a client-API-testing limitation, not a bug; verify this path against the real browser, or by checking `src/questions.py`'s parsing directly and trusting Gradio's very standard visible-toggle idiom for the rest.

## Sidebar: pin, delete, attach

- **Pin/Delete act on the currently loaded project**, not on a separately-selected-but-not-open sidebar item — there's only one "current" project (`state_user_project`) at a time, which keeps the Gradio wiring simple (no per-row buttons inside a `gr.Radio`, which isn't practical). Pinned projects show in a `Pinned` section above `Chats`, ordered by pin order (not recency); the section is hidden entirely (`pinned_section` visibility) when nothing is pinned. Pin state lives in `data/Scientific-Writing-AI/<user>/pinned.json` (`storage.load_pinned()`/`save_pinned()`) — a user-level file, not inside any project folder.
- **Delete is a real two-step confirmation** (`project_events.request_delete` → `confirm_delete`/`cancel_delete`), using the same visible-toggle popup pattern as the clarifying-question modal (`#delete-modal` in `theme.py`). `storage.delete_project()` does an actual `shutil.rmtree` — there is no undo. After deleting the currently-open project, `confirm_delete()` falls back to the next most recent remaining project, or creates a fresh one if none are left. Don't make delete a single click — that was an explicit requirement, not just caution.
- **Chat-bar attach** (`attach_btn`, a `gr.UploadButton`) is deliberately scoped to papers/RAG only, not writing samples — attaching a reference mid-conversation is the natural in-chat action; writing-style samples stay a one-time setup step in the Files accordion. It calls the exact same `upload_events.process_papers()` as the Files-section upload, just from a second entry point, so the two never drift apart.

## Conventions

- Data flow for a chat turn: `chat_events.respond()` → `prompt_builder.build_messages()` (RAG context + style profile + manuscript) → `ollama_client.chat_stream()` → `manuscript_state.split_reply_and_edit()` (only non-None on an explicit full-compile ask) → `versioning.add_version()` + `persistence/manuscript_store.py`. Data flow for an incremental add: `manuscript_events.add_last_reply_to_manuscript()` → `sections.replace_or_append_section()` → same versioning/persistence calls. Trace the relevant path before changing either.
- Gradio has **no ambient session state**. Every value that must survive between event handlers is an explicit `gr.State` in `layout.py`, threaded through `inputs=`/`outputs=` on every handler. When adding a new piece of cross-call state, add it to `ui/state.py` and thread it through in `layout.py` — don't reach for globals.
- The full-compile protocol is plain text (`<<<MANUSCRIPT_START>>>` / `<<<MANUSCRIPT_END>>>`), not function-calling — quantized 7B models are unreliable at tool-calling. The model can (and does) write follow-up text after the closing marker; `manuscript_state.split_reply_and_edit()` folds that back into the visible reply rather than discarding it. Don't reintroduce that bug.
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

1. Launch the app — confirms a project auto-creates/resumes on load and `data/Scientific-Writing-AI/<LOCAL_USER>/<project>/{Manuscript,Chat,Versions}` gets created; click "+ New" to start a second one and confirm both appear in the sidebar, most recent first.
2. Upload a PDF paper, ask a question about its content — confirms parsing/chunking/embedding/retrieval.
3. Upload a writing sample, ask for a rewrite "in my style" — confirms style extraction.
4. Ask the model to write something (e.g. "write the introduction") — confirms the manuscript panel does **not** change (plain chat only).
5. Name a section and click "Add last reply to manuscript" — confirms it's inserted verbatim under that heading and a version is added.
6. Repeat with a different section name — confirms it's appended without disturbing the first section; repeat with the *same* name — confirms it replaces just that section.
7. Ask "show me the manuscript" — confirms a full document gets compiled from the conversation.
8. Make 6+ additions — confirms only the last 5 versions are kept.
9. Revert to an older version — confirms it restores correctly and is itself recorded as a new version.
10. Restart the app, reload the browser, reload the same project — confirms chat/manuscript/versions reload from disk, and papers/samples do **not** persist.
11. Click the attach icon in the chat bar and pick a PDF, then ask about its content — confirms it's usable as RAG context the same as a Files-section upload.
12. Pin a project — confirms a "Pinned" section appears above "Chats" and the button relabels to "Unpin"; unpin — confirms the section disappears again once empty.
13. Click "Delete" on the open project — confirms a confirmation popup appears and nothing is removed until you click "Delete permanently"; confirm — confirms the folder is gone from disk and another project (or a fresh one) loads automatically.

For quick non-UI checks, `gradio_client.Client` can hit the app's endpoints directly (`/startup`, `/respond`, `/toggle_pin`, `/confirm_delete`, `/add_last_reply_to_manuscript`, etc.) without a browser — see git history for example usage.

## Git

- Remote: `https://github.com/mridul0837/Scientific-Writing-AI.git`, branch `main`.
- `data/` and `.claude/` are gitignored — never commit either.
