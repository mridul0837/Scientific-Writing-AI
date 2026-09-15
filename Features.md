Here is the current finalized V0.1 scope based on all decisions so far.

V0.1 — Finalized Features
1. Core experience
One ChatGPT-like chatbot
Natural-language interaction — no forced task modes
User can ask it to:
Research
Write
Rewrite
Explain
Summarize
Review
Edit
Find evidence
Format
AI automatically determines what the user wants.
2. File uploads

Research papers

Upload 1–10 papers
Session-only
Used for:
RAG/knowledge
Research context
Terminology
Academic writing conventions

Writing samples

Upload 1–10 samples
Session-only
AI automatically learns the user's writing style.

User can simply say:

"Rewrite this in my style."

3. Context & memory

Automatic management of:

Current conversation
Manuscript
Research context
Uploaded papers
Writing style
Relevant user/project context

Long conversations → automatically summarize older context.

The user shouldn't have to manage context manually.

4. Scientific writing

AI can:

Generate sections/content
Rewrite existing text
Improve academic style
Make text concise
Maintain user's writing style
Modify the manuscript directly

No predefined manuscript structure.

5. Scientific review

Two levels:

Language

Grammar
Clarity
Academic style
Conciseness

Scientific

Logic
Unsupported claims
Contradictions
Methodological issues
Weak reasoning
Missing justification

Review should report problems + suggest fixes, rather than silently modifying the manuscript.

6. Web research

Three user-selectable settings:

Off
Automatic
Always

The user can change this anytime.

7. Citations

APA 7 only for V0.1.

AI:

Identifies a claim requiring evidence.
Finds relevant literature.
Shows:
Claim
Supporting evidence
Full APA 7 citation
User chooses Insert or Ignore.

No automatic citation insertion.

8. Manuscript versions
AI edits update the manuscript directly.
Keep last 5 versions.
User can recover previous versions.
9. Export

One-click:

[Download Word] [Download LaTeX] [Download PDF]

Also support natural-language requests such as:

"Export this as LaTeX."

10. Persistence

Automatically save:

Chat after every message
Manuscript after every AI edit
Version history

To user's personal Google Drive:

Scientific-Writing-AI/
└── User_Name/
    └── Project_Name/
        ├── Manuscript/
        ├── Chat/
        └── Versions/

Uploaded papers/writing samples are not persisted.

11. UI / technology

Frontend: Streamlit

The goal is to make Streamlit feel as close as practical to a premium ChatGPT experience:

Clean chat
Streaming responses
Drag/drop uploads
File visibility
Manuscript interaction
Simple export buttons
12. Local AI

Initial deployment:

Ollama
Open-weight LLM
Local RTX 3060 Laptop GPU
Quantized ~7–8B-class model initially

No fine-tuning for V0.1.

13. RAG

Likely:

PDF
 ↓
Parser
 ↓
Chunks
 ↓
Embedding model
 ↓
Vector DB
 ↓
Relevant passages
 ↓
LLM

Likely Chroma or FAISS initially.

Explicitly NOT V0.1

Don't build these yet:

❌ Multi-agent system
❌ Fine-tuning
❌ Figures/tables handling
❌ Multiple citation styles
❌ Complex project-management UI
❌ Multiple-user account system
❌ Advanced memory controls
❌ Cloud GPU infrastructure
❌ Real-time collaboration
❌ React/Next.js