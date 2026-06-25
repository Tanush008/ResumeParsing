"""
Strict contract for what Gemini's resume-parsing call must return.
parsed_service.py validates its JSON against this BEFORE it's stored or
returned to the frontend -- catches malformed/missing fields early instead of
letting bad data silently reach the database or the client.
"""
from pydantic import BaseModel, Field


class SkillItem(BaseModel):
    skill_name: str | None = None
    category: str | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class EducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None  # kept as str here; app/api/parser.py parses to date
    end_date: str | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class ExperienceItem(BaseModel):
    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class ParsedResume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[SkillItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
