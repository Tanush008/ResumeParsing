from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Resume, Candidate, Skill, Education, Experience
from app.api.resume import get_db
from app.services.parsed_service import parse_resume, ResumeParsingError

router = APIRouter()


def parse_date(date_str):
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str.date()
    # Handle common date formats or return None if parsing fails
    for fmt in ('%Y-%m-%d', '%Y-%m', '%Y/%m/%d', '%Y/%m'):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    return None


@router.post("/{resume_id}")
def parse_resume_api(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        parsed = parse_resume(resume.extracted_text)
    except ResumeParsingError as e:
        # Gemini failure or malformed output -- a clean 502, not a raw 500.
        raise HTTPException(status_code=502, detail=str(e))

    # --- Persist the parsed data ---
    candidate = Candidate(
        name=parsed.get("name"),
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        raw_text=resume.extracted_text,
        source_filename=resume.filename,
    )
    db.add(candidate)
    db.flush()  # assigns candidate.id without committing yet

    # Persist Skills
    for skill_item in parsed.get("skills", []):
        if isinstance(skill_item, dict):
            db.add(Skill(
                candidate_id=candidate.id,
                skill_name=skill_item.get("skill_name") or skill_item.get("name"),
                category=skill_item.get("category"),
                confidence_score=skill_item.get("confidence_score")
            ))
        else:
            db.add(Skill(
                candidate_id=candidate.id,
                skill_name=str(skill_item)
            ))

    # Persist Education
    for edu in parsed.get("education", []):
        db.add(Education(
            candidate_id=candidate.id,
            institution=edu.get("institution") or edu.get("school"),
            degree=edu.get("degree"),
            field_of_study=edu.get("field_of_study") or edu.get("major"),
            start_date=parse_date(edu.get("start_date")),
            end_date=parse_date(edu.get("end_date")),
            confidence_score=edu.get("confidence_score")
        ))

    # Persist Experience
    for exp in parsed.get("experience", []):
        is_curr = 1 if exp.get("is_current") or exp.get("end_date") == "Present" else 0
        db.add(Experience(
            candidate_id=candidate.id,
            company=exp.get("company"),
            title=exp.get("title") or exp.get("role"),
            start_date=parse_date(exp.get("start_date")),
            end_date=parse_date(exp.get("end_date")) if not is_curr else None,
            is_current=is_curr,
            description=exp.get("description") or exp.get("summary"),
            confidence_score=exp.get("confidence_score")
        ))

    resume.candidate_id = candidate.id
    db.commit()

    return {
        "candidate_id": candidate.id,
        "resume_id": resume.id,
        **parsed,
    }