"""Manual Pinecone round-trip test (upsert -> query -> match)."""
from __future__ import annotations

import uuid
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services import vector_store


def main() -> None:
    index = vector_store.get_index()
    vector_id = f"dummy-{uuid.uuid4().hex}"
    values = [0.0] * 1024
    values[0] = 0.1
    values[1] = 0.2
    values[2] = 0.05
    values[3] = 0.3
    values[4] = 0.12
    values[5] = 0.7
    values[6] = 0.9
    values[7] = 0.4
    metadata = {"source": "manual-test", "note": "dummy vector"}

    vector_store.upsert_vector(index, vector_id, values, metadata)
    result = vector_store.query_vector(index, values, top_k=3)

    matches = result.get("matches", [])
    if not matches:
        raise RuntimeError("No matches returned from Pinecone.")

    top = matches[0]
    top_id = top.get("id")
    top_score = top.get("score")
    top_metadata = top.get("metadata")

    if top_id != vector_id:
        raise AssertionError(f"Top match id mismatch: {top_id} != {vector_id}")

    print("top_match_id:", top_id)
    print("score:", top_score)
    print("metadata:", top_metadata)


if __name__ == "__main__":
    main()
