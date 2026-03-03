from __future__ import annotations

import unittest
from io import BytesIO
from unittest.mock import patch

from docx import Document
from fastapi.testclient import TestClient

from app.main import app
from app.services import rewrite_service
from app.services.services import lock_service

ALLOWED_DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _build_docx_bytes() -> bytes:
    buffer = BytesIO()
    doc = Document()
    doc.add_paragraph("Rewrite this document.")
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


class RewriteConcurrencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def tearDown(self):
        lock_service.release("rewrite:demo-doc-1")
        lock_service.release("rewrite:doc-456")

    @patch("app.services.rewrite_service.generate_text")
    def test_route_returns_409_when_rewrite_is_already_running(
        self,
        mock_generate,
    ):
        self.assertTrue(lock_service.acquire("rewrite:demo-doc-1", ttl_seconds=60))

        response = self.client.post(
            "/api/rewrite",
            files={
                "file": (
                    "sample.docx",
                    BytesIO(_build_docx_bytes()),
                    ALLOWED_DOCX_TYPE,
                )
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["detail"],
            rewrite_service.REWRITE_IN_PROGRESS_MESSAGE,
        )
        mock_generate.assert_not_called()

    @patch("app.services.rewrite_service.generate_text", side_effect=RuntimeError("boom"))
    def test_service_releases_lock_when_llm_call_fails(self, _mock_generate):
        with self.assertRaises(RuntimeError):
            rewrite_service.rewrite_document(
                document_id="doc-456",
                text="Rewrite this text.",
            )

        self.assertTrue(lock_service.acquire("rewrite:doc-456", ttl_seconds=60))
