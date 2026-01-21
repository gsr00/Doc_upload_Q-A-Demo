"""Semantic search service for RAG retrieval."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.services import chunker, document_parser, embedding_service, vector_store

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH, override=True)


def _sanitize_query(query: str) -> str:
    cleaned = " ".join(query.split())
    if len(cleaned) < 3:
        raise ValueError("Query too short; please provide a longer query.")
    if len(cleaned) > 2000:
        raise ValueError("Query too long; please keep under 2000 characters.")
    return cleaned


def _get_doc_root() -> Path:
    root = os.getenv("RAG_DOC_ROOT")
    if not root:
        raise ValueError("RAG_DOC_ROOT is required to load source excerpts.")
    return Path(root)


def _load_excerpt(doc_root: Path, filename: str, chunk_index: int, max_chars: int = 800) -> str:
    path = doc_root / filename
    if not path.exists():
        raise ValueError(f"Source document not found: {path}")
    raw_text = document_parser.extract_text_from_docx(path)
    normalized = chunker.normalize_text(raw_text)
    chunks = chunker.chunk_text(normalized, max_chars=max_chars)
    if chunk_index < 0 or chunk_index >= len(chunks):
        raise ValueError("Chunk index out of range for source document.")
    return chunks[chunk_index]


def search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    cleaned = _sanitize_query(query)
    embedding = embedding_service.embed_texts([cleaned])[0]

    index = vector_store.get_index()
    result = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    matches = result.get("matches", [])

    doc_root = _get_doc_root()
    results: list[dict[str, Any]] = []
    for match in matches:
        metadata = match.get("metadata") or {}
        filename = metadata.get("source_filename") or "unknown"
        chunk_index = int(metadata.get("chunk_index", -1))
        excerpt = _load_excerpt(doc_root, filename, chunk_index)
        results.append(
            {
                "id": match.get("id"),
                "score": match.get("score"),
                "source": filename,
                "excerpt": excerpt,
            }
        )
    return results
