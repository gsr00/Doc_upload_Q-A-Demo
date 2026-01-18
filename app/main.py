from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="legal-rewrite-qa")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the static UI page."""
    ui_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(ui_path.read_text(encoding="utf-8"))


@app.get("/health")
async def health():
    return {"status": "ok"}


class QARequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)


@app.post("/api/qa")
async def ask_question(payload: QARequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    placeholder_answer = (
        "Thanks for your question. This is a placeholder response while the drafting "
        "assistant is being connected. We will return specific guidance here soon."
    )
    return {"answer": placeholder_answer}


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

