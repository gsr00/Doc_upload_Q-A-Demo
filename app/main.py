from pathlib import Path

import re
import tempfile

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from app.services import document_parser, doc_qa_service, docx_writer, file_store, qa_service, rewrite_service

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


@app.post("/api/doc_qa")
async def doc_qa(payload: QARequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        result = doc_qa_service.answer_question(payload.question.strip())
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Doc Q&A failed: {exc}")


@app.post("/api/rewrite")
async def rewrite_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    notes: str | None = Form(None),
    goals: str | None = Form(None),
):
    # Accept only DOCX, with size/type validation and temp cleanup.
    tmp_path: Path | None = None
    try:
        tmp_path = file_store.save_upload_to_temp(file)
        extracted_text = document_parser.extract_text_from_docx(tmp_path)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text found in the document.")
        parsed_goals = [part for part in re.split(r"[,\n]", goals or "") if part.strip()]
        rewritten_text = rewrite_service.rewrite_document(
            extracted_text,
            goals=parsed_goals,
            notes=notes,
        )
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        output_path = Path(output_file.name)
        output_file.close()
        docx_writer.write_docx(rewritten_text, output_path)
        background_tasks.add_task(output_path.unlink, missing_ok=True)
        return FileResponse(
            output_path,
            media_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            filename="rewritten.docx",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        # Always delete temp file, regardless of success or failure.
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
