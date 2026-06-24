from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import Resume
from app.api.resume import get_db
from app.services.parsed_service import parse_resume

router = APIRouter()

@router.post("/{resume_id}")
def parse_resume_api(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    parsed = parse_resume(
        resume.extracted_text
    )

    return parsed