"""Embedding helper for RAG ingestion."""
from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


def _get_target_dim() -> int | None:
    raw = os.getenv("EMBEDDING_DIM")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _adjust_dim(vector: list[float], target_dim: int | None) -> list[float]:
    if target_dim is None:
        return vector
    if len(vector) > target_dim:
        return vector[:target_dim]
    if len(vector) < target_dim:
        return vector + [0.0] * (target_dim - len(vector))
    return vector


def embed_texts(texts: list[str]) -> list[list[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for embeddings.")

    endpoint = os.getenv("OPENAI_EMBED_API_BASE", "https://api.openai.com/v1/embeddings")
    model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    payload = {"model": model, "input": texts}

    resp = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()

    target_dim = _get_target_dim()
    return [_adjust_dim(item["embedding"], target_dim) for item in data.get("data", [])]
