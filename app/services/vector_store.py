"""Pinecone vector store helpers."""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()


def get_index():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX")
    if not api_key or not index_name:
        raise ValueError("PINECONE_API_KEY and PINECONE_INDEX are required.")
    client = Pinecone(api_key=api_key)
    host = os.getenv("PINECONE_HOST")
    if host:
        return client.Index(index_name, host=host)
    return client.Index(index_name)


def upsert_vector(index, vector_id: str, values: list[float], metadata: dict[str, Any]):
    index.upsert(vectors=[{"id": vector_id, "values": values, "metadata": metadata}])


def upsert_vectors(index, vectors: list[dict[str, Any]]):
    if not vectors:
        return
    index.upsert(vectors=vectors)


def query_vector(index, values: list[float], top_k: int = 3):
    return index.query(vector=values, top_k=top_k, include_metadata=True)
