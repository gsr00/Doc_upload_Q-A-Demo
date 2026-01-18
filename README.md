# legal-rewrite-qa

Minimal FastAPI service scaffold with a health check.

## Getting started
1. Create and activate a virtual environment.
2. pip install -r requirements.txt
3. uvicorn app.main:app --reload

## Endpoints
- GET /health -> {"status": "ok"}
- GET / -> simple service identifier

## Smoke test
Run `python tests/manual_smoke.py` while the server is running to hit the root and health endpoints.
