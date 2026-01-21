"""Manual grounded Q&A test with citations."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services import doc_qa_service


def _run(query: str) -> None:
    result = doc_qa_service.answer_question(query, top_k=5)
    print("query:", query)
    print("answer:", result.get("answer"))
    print("sources:", len(result.get("sources", [])))


def main() -> None:
    _run("What is the clause for holiday pay?")
    _run("Explain the quantum entanglement clause in this document.")


if __name__ == "__main__":
    main()
