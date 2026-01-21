"""Manual semantic search test for RAG retrieval."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services import search_service


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python tests/manual_rag_search.py \"your query\"")

    query = sys.argv[1]
    results = search_service.search(query, top_k=5)

    for idx, item in enumerate(results, start=1):
        print(f"match_{idx}_source:", item["source"])
        print(f"match_{idx}_score:", item["score"])
        print(f"match_{idx}_excerpt:", item["excerpt"])


if __name__ == "__main__":
    main()
