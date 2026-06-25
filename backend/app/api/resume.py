import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Resume
from app.services.pdf_service import extract_text_from_pdf

router = APIRouter()

# Resolve path from this file's location to stay independent of working directory
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Only PDF is supported.")

    # Unique prefix to prevent file overwrites
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = UPLOAD_DIR / unique_name

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(str(filepath))
    except Exception as e:
        filepath.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not extract text from PDF: {e}")

    if not extracted_text.strip():
        filepath.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="No extractable text found in PDF (may be a scanned image).")

    resume = Resume(
        filename=file.filename,
        filepath=str(filepath),
        extracted_text=extracted_text
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Uploaded Successfully",
        "resume_id": resume.id,
        "text_length": len(extracted_text)
    }


@router.get("/")
def get_all_resumes(db: Session = Depends(get_db)):
    return db.query(Resume).all()


@router.get("/{resume_id}")
def get_resume_by_id(resume_id: int, db: Session = Depends(get_db)):
    if not (resume := db.get(Resume, resume_id)):
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume