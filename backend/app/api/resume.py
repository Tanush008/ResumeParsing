import os
import shutil

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

UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


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

    filepath = f"{UPLOAD_DIR}/{file.filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(filepath)

    resume = Resume(
        filename=file.filename,
        filepath=filepath,
        extracted_text=extracted_text
    )

    db.add(resume)
    db.commit()

    return {
        "message": "Uploaded Successfully",
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