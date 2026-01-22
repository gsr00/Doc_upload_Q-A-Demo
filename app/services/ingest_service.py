"""Document ingest service for RAG indexing."""
from __future__ import annotations

import uuid
from pathlib import Path

from app.services import chunker, document_parser, embedding_service, vector_store


def ingest_docx(path: Path) -> dict[str, int | str]:
    raw_text = document_parser.extract_text_from_docx(path)
    normalized = chunker.normalize_text(raw_text)
    chunks = chunker.chunk_text(normalized, max_chars=200)
    if not chunks:
        raise ValueError("No content available for indexing.")

    vectors = embedding_service.embed_texts(chunks)
    if len(vectors) != len(chunks):
        raise RuntimeError("Embedding count does not match chunk count.")

    index = vector_store.get_index()
    doc_id = uuid.uuid4().hex
    total = len(chunks)
    payload = []

    for idx, vector in enumerate(vectors):
        payload.append(
            {
                "id": f"{doc_id}-{idx}",
                "values": vector,
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "chunk_count": total,
                    "source_filename": path.name,
                },
            }
        )

    vector_store.upsert_vectors(index, payload)
    return {"doc_id": doc_id, "chunk_count": total, "vectors_upserted": total}
