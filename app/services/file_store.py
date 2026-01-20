"""Utilities for saving uploads to temporary files with validation."""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import UploadFile

# Accept only DOCX uploads for now.
ALLOWED_EXTENSIONS: set[str] = {".docx"}
ALLOWED_CONTENT_TYPES: set[str] = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Some browsers send generic octet-stream; we'll rely on extension check too.
    "application/octet-stream",
}
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
READ_CHUNK_BYTES = 1024 * 1024


def _validate_extension(filename: str | None) -> str:
    if not filename:
        raise ValueError("Filename missing; please upload a .docx file.")
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type; please upload a .docx file.")
    return ext


def _validate_content_type(content_type: str | None) -> None:
    if content_type is None:
        return
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported content type; please upload a DOCX file.")


def save_upload_to_temp(upload: UploadFile, max_bytes: int = DEFAULT_MAX_BYTES) -> Path:
    """Persist an UploadFile to a temporary file with basic validation.

    Raises ValueError on validation or size failures; ensures temp files are
    removed if anything goes wrong during the write.
    """
    ext = _validate_extension(upload.filename)
    _validate_content_type(upload.content_type)

    # Start from the beginning in case the upload stream was read earlier.
    try:
        upload.file.seek(0)
    except Exception:
        pass

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    total = 0
    try:
        while True:
            chunk = upload.file.read(READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("File too large; max allowed is 5 MB.")
            temp.write(chunk)
        temp.flush()
    except Exception:
        temp.close()
        Path(temp.name).unlink(missing_ok=True)
        raise
    else:
        temp.close()
        return Path(temp.name)