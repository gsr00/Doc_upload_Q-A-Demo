"""Minimal smoke checks for local FastAPI server."""
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    r.raise_for_status()
    data = r.json()
    assert data.get("status") == "ok", data
    print("/health", data)


def test_root():
    r = requests.get(BASE_URL)
    r.raise_for_status()
    print("/", r.json())


if __name__ == "__main__":
    test_health()
    test_root()
