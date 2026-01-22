# Legal Rewrite & Document Q&A Application

This repository contains a small but complete FastAPI application designed to demonstrate
how AI can add value and increase productivity in real wprld applications.
Applying AI technicques like Retrieval-Augmented Generation (RAG) and using Large Language Models.
Overall the AI system is explainable from retrieving data from documents to LLM augmentation.

The AI system Integrates three distinct core use cases embeded into one UI:

1. Rewriting uploaded legal documents for clarity and tone.

2. Answering general legal drafting questions.

3. Searching across multiple uploaded documents to find relevant clauses or passages, with sources.

## Getting started
### Prerequisites:

Python 3.10+
A Pinecone account (free tier is sufficient)
An OpenAI-compatible API key

### Setup
1. Create and activate a virtual environment.
2. Install dependencies:
- pip install -r requirements.txt
3. Create a .env file with:
- OPENAI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=...

4. Run the app
uvicorn app.main:app --reload

5. Open a browser at http://127.0.0.1:8000

## How to run with Docker
docker compose up --build
open http://127.0.0.1:8000

## Endpoints
- GET /health -> {"status": "ok"}
- GET / -> simple service identifier

## Smoke test
Run `python tests/manual_smoke.py` while the server is running to hit the root and health endpoints.
