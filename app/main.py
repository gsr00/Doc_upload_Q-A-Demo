from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.services import qa_service

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
    if not file.filename.lower().endswith((".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Please upload a .docx or .doc file.")

    placeholder = (
        f"Received '{file.filename}'. A rewritten DOCX will be available here once the "
        "rewrite service is connected. Notes received: "
        f"{notes.strip() if notes else 'none'}."
    )
    return {"message": placeholder}
