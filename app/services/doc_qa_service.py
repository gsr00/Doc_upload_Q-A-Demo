"""Grounded document Q&A service with citations."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app import prompts
from app.services import chunker, document_parser, embedding_service, vector_store
from app.services.llm_gateway import generate_text

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH, override=True)


def _sanitize_question(question: str) -> str:
    cleaned = " ".join(question.split())
    if len(cleaned) < 5:
        raise ValueError("Question too short; need at least 5 characters.")
    if len(cleaned) > 2000:
        raise ValueError("Question too long; keep under 2000 characters.")
    return cleaned


def _get_doc_root() -> Path:
    root = os.getenv("RAG_DOC_ROOT")
    if not root:
        raise ValueError("RAG_DOC_ROOT is required to load source excerpts.")
    return Path(root)


def _load_excerpt(doc_root: Path, filename: str, chunk_index: int, max_chars: int = 200) -> str:
    path = doc_root / filename
    if not path.exists():
        raise ValueError(f"Source document not found: {path}")
    raw_text = document_parser.extract_text_from_docx(path)
    normalized = chunker.normalize_text(raw_text)
    chunks = chunker.chunk_text(normalized, max_chars=max_chars)
    if chunk_index < 0 or chunk_index >= len(chunks):
        raise ValueError("Chunk index out of range for source document.")
    return chunks[chunk_index]


def _build_sources(matches: list[dict[str, Any]], doc_root: Path) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for match in matches:
        metadata = match.get("metadata") or {}
        filename = metadata.get("source_filename") or "unknown"
        chunk_index = int(metadata.get("chunk_index", -1))
        excerpt = _load_excerpt(doc_root, filename, chunk_index)
        score = match.get("score")
        sources.append(
            {
                "id": str(match.get("id")),
                "score": float(score) if score is not None else 0.0,
                "source": filename,
                "chunk_index": int(chunk_index),
                "excerpt": excerpt,
            }
        )
    return sources


def _format_sources(sources: list[dict[str, Any]]) -> str:
    blocks = []
    for idx, source in enumerate(sources, start=1):
        blocks.append(
            f"SOURCE {idx}\n"
            f"Document: {source['source']}\n"
            f"Chunk: {source['chunk_index']}\n"
            f"Excerpt: {source['excerpt']}\n"
        )
    return "\n".join(blocks)


def answer_question(question: str, top_k: int = 5) -> dict[str, Any]:
    cleaned = _sanitize_question(question)
    embedding = embedding_service.embed_texts([cleaned])[0]

    index = vector_store.get_index()
    result = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    matches = result.get("matches", [])
    if not matches:
        return {"answer": "No strong match found in the documents.", "sources": []}

    min_score = float(os.getenv("MIN_RELEVANCE_SCORE", "0.35"))
    top_score = matches[0].get("score") or 0.0
    if top_score < min_score:
        return {"answer": "No strong match found in the documents.", "sources": []}

    doc_root = _get_doc_root()
    sources = _build_sources(matches, doc_root)
    sources_block = _format_sources(sources)
    user_prompt = (
        f"Question: {cleaned}\n\n"
        f"SOURCES:\n{sources_block}\n\n"
        "Answer the question using only the SOURCES and cite them."
    )

    llm_response = generate_text(user_prompt, system=prompts.LEGAL_DOC_QA_SYSTEM_PROMPT)
    return {"answer": llm_response.content, "sources": sources}
