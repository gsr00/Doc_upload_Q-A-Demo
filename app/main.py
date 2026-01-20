from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.services import document_parser, file_store, qa_service

app = FastAPI(title="legal-rewrite-qa")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the static UI page."""
    ui_path = Path(__file__).parent / "web" / "templates" / "index.html"
    return HTMLResponse(ui_path.read_text(encoding="utf-8"))


@app.get("/health")
async def health():
    return {"status": "ok"}


class QARequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)


@app.post("/api/qa")
async def ask_question(payload: QARequest):
    # Validate and forward to the QA service (LLM stubbed in llm_gateway for now).
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = qa_service.answer_question(payload.question.strip())
    return {"answer": answer}


@app.post("/api/rewrite")
async def rewrite_document(file: UploadFile = File(...), notes: str | None = None):
    # Accept only DOCX, with size/type validation and temp cleanup.
    tmp_path: Path | None = None
    try:
        tmp_path = file_store.save_upload_to_temp(file)
        extracted_text = document_parser.extract_text_from_docx(tmp_path)
        # Do not log or return raw text; just confirm processing succeeded.
        message = (
            "Document processed successfully. Rewrite service will use this text when connected. "
            f"Characters extracted: {len(extracted_text)}."
        )
        return {"message": message}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
