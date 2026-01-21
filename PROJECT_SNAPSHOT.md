# Project Snapshot: Doc_upload_Q-A-Demo

## Purpose
A minimal FastAPI service and UI for two legal drafting workflows:
1) Upload a DOCX, extract text, and confirm processing for later rewrite.
2) Ask a general drafting question and get a concise LLM response.

## What it does today
- Serves a single-page UI with two cards (rewrite upload + Q&A).
- Accepts DOCX uploads, validates size/type, extracts text (including tables), then reports character count.
- Sends Q&A prompts to an OpenAI-compatible chat API with a law drafting persona.

## Architecture at a glance
- Web API: FastAPI app in `app/main.py`.
- UI: Static HTML template in `app/web/templates/index.html`.
- Services:
  - `document_parser.py`: DOCX text extraction.
  - `file_store.py`: upload validation + temp file management.
  - `llm_gateway.py`: OpenAI-compatible API call wrapper.
  - `qa_service.py`: prompt assembly and response handling.

## Data flow
- Rewrite:
  1) User uploads DOCX + optional notes in the UI.
  2) `/api/rewrite` saves to temp, validates, extracts text, returns success message.
  3) Temp file is deleted in a finally block.
- Q&A:
  1) User submits a question in the UI.
  2) `/api/qa` validates the question, builds prompt, calls `llm_gateway`.
  3) Response text is returned to the UI.

## External dependencies
- Python packages: FastAPI, requests, python-docx, python-dotenv.
- Environment variables:
  - `OPENAI_API_KEY` (required for Q&A)
  - `OPENAI_MODEL` (optional, default `gpt-4o-mini`)
  - `OPENAI_API_BASE` (optional, default OpenAI endpoint)

## API surface
- `GET /` -> serves the UI
- `GET /health` -> `{"status": "ok"}`
- `POST /api/qa` -> `{ "question": "..." }` => `{ "answer": "..." }`
- `POST /api/rewrite` -> multipart form with `file` (DOCX) and optional `notes`

## Repo layout (top level)
- `app/` application code and UI
- `tests/` manual smoke tests
- `requirements.txt`, `.env.example`, `README.md`

## Known gaps / next steps
- The rewrite endpoint does not yet call the LLM or return rewritten content.
- No persistent storage or document index; all uploads are temporary.
- No authentication or audit logging.

## How to run
1) `pip install -r requirements.txt`
2) `uvicorn app.main:app --reload`
3) Open `http://localhost:8000/`
