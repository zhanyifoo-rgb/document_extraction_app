# app/main.py

from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
import tempfile

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document
from app.ocr_service import extract_text
from app.document_parser import parse_invoice,extract_document
import logging


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
MAX_FILE_SIZE = 4 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Invoice and Receipt Automation API",
    lifespan=lifespan,
)

logger = logging.getLogger(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = Path(file.filename or "upload").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, WEBP and PDF files are supported.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="The file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 4 MB.",
        )

    # Use the original extension so PaddleOCR can identify the input type.
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / f"document{extension}"
        temp_path.write_bytes(content)

        try:
            ocr_result = extract_text(str(temp_path))
            parsed = await extract_document(ocr_result["text"])
        except Exception as exc:
            logger.exception("Document processing failed")

            raise HTTPException(
                status_code=422,
                detail="Unable to process this document. Check its format and quality.",
            ) from exc

    document = Document(
        filename=filename,
        document_type=(
            "receipt"
            if "receipt" in ocr_result["text"].lower()
            else "invoice"
        ),
        status="needs_review",
        extracted_data={
            "document_number": parsed["document_number"],
            "document_date": parsed["document_date"],
            "subtotal": (
                str(parsed["subtotal"])
                if parsed["subtotal"] is not None
                else None
            ),
            "tax_total": (
                str(parsed["tax_total"])
                if parsed["tax_total"] is not None
                else None
            ),
            "total": (
                str(parsed["total"])
                if parsed["total"] is not None
                else None
            ),
            "currency": parsed["currency"],
            "ocr_text": ocr_result["text"],
            "ocr_lines": ocr_result["lines"],
        },
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": str(document.id),
        "filename": document.filename,
        "document_type": document.document_type,
        "status": document.status,
        "extracted_data": document.extracted_data,
        "created_at": document.created_at.isoformat(),
    }