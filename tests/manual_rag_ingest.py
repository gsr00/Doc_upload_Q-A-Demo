"""Manual DOCX ingest test for RAG indexing."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services import ingest_service


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python tests/manual_rag_ingest.py <path-to-docx>")

    path = Path(sys.argv[1])
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    result = ingest_service.ingest_docx(path)
    print("document_id:", result["doc_id"])
    print("chunk_count:", result["chunk_count"])
    print("vectors_upserted:", result["vectors_upserted"])


if __name__ == "__main__":
    main()
