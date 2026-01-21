"""Text normalization and chunking helpers."""
from __future__ import annotations


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    if not text:
        return []
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        extra = len(word) + (1 if current else 0)
        if current and current_len + extra > max_chars:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
            continue
        current.append(word)
        current_len += extra

    if current:
        chunks.append(" ".join(current))
    return chunks
