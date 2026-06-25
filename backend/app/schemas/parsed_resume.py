"""
Strict contract for what Gemini's resume-parsing call must return.
parsed_service.py validates its JSON against this BEFORE it's stored or
returned to the frontend -- catches malformed/missing fields early instead of
letting bad data silently reach the database or the client.
"""
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None


class ExperienceItem(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None


class ParsedResume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)