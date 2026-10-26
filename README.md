# AI Guidance Chatbot — starter scaffold

This is a skeleton, not a finished app. Every module has a docstring explaining
its job and TODOs describing what to implement — the logic is intentionally
left for you to write. Cross-reference `AI_Guidance_Chatbot_Plan.md` for the
"why" behind each phase.

## Folder layout

```
app/
  main.py                FastAPI entrypoint
  config.py               loads .env into settings
  ingestion/               Phase 1 + 2: loaders, OCR, language detect, chunking, embed+store
  retrieval/                Phase 3: retriever + confidence scoring
  chat/                      Phase 3 + 4: RAG chain, Groq fallback, LangGraph state machine
  db/                          Postgres models + session (chat history, feedback, review queue)
  api/routes/                  FastAPI endpoints (chat, feedback, admin, ingest)
  admin/dashboard.py            Streamlit admin review UI (Phase 5)
scripts/
  ingest_documents.py    CLI to bulk-load a folder of docs — good first thing to build
data/sample_docs/         put a few test PDFs/docx/images here
tests/                          write tests as you go
```

## Setup

1. `python -m venv venv && source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
2. `pip install -r requirements.txt`
3. Install Tesseract on your OS with English, Spanish, French packs, e.g. on Ubuntu:
   `sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-fra`
4. `cp .env.example .env` and fill in your `GROQ_API_KEY` (free at console.groq.com) and `DATABASE_URL`
5. Set up a free Postgres instance (Supabase is easiest) for `DATABASE_URL`. Chroma needs no separate server — it persists to `CHROMA_PERSIST_DIR` on disk.

## Where to start (maps to the 2-week day-by-day plan)

**Day 1–2 target — build these in order, and test each one standalone before moving on:**

1. `app/config.py` — load your `.env` values.
2. `app/ingestion/loaders.py` — start with just `load_pdf()`. Get one real PDF loading into LangChain `Document` objects before touching anything else.
3. `app/ingestion/ocr.py` — only needed once you hit a scanned PDF/image with no extractable text.
4. `app/ingestion/language_detect.py` — small, self-contained, easy first win.
5. `app/ingestion/chunking.py` — split the Documents from step 2 into chunks.
6. `app/ingestion/embed_store.py` — embed the chunks and get them into Chroma. **Once this works, you have a searchable knowledge base — that's your Day 1–2 milestone.**
7. `scripts/ingest_documents.py` — wire steps 2–6 into one CLI script so you can bulk-load `data/sample_docs/` with one command. This is the fastest way to test the whole ingestion pipeline without building the API yet.

**Day 3+:** move into `retrieval/`, then `chat/`, then the FastAPI routes — the docstrings in each file tell you what LangChain/LangGraph pieces to reach for.

## A note on learning this

Don't just fill in TODOs by pattern-matching — read the LangChain docs for
each class mentioned in the docstrings (`PyPDFLoader`, `RecursiveCharacterTextSplitter`,
`Chroma`, `ChatGroq`, `StateGraph`) before you write the function. That's where
the actual understanding comes from.
