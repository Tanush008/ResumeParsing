"""
ORM models.

Design notes:
- candidates: 1 row per uploaded resume.
- experience / education / skills: 1-to-many off candidates, each with its own
  confidence_score so the eval harness can correlate low confidence with errors.
- job_descriptions: stored JDs, either pasted manually or fetched from a URL.
- rankings: output of the ranking agent — one row per (candidate, job) pair scored.
"""
from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    filename = Column(String(512))
    filepath = Column(String(512))
    extracted_text = Column(Text)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)

    candidate = relationship("Candidate", back_populates="resumes")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    links = Column(JSON)  # list of URLs (LinkedIn, GitHub, portfolio) extracted from the resume
    raw_text = Column(Text)  # full extracted text, kept for re-parsing / debugging
    source_filename = Column(String(512))
    overall_confidence = Column(Float)  # aggregate confidence from the parser agent
    created_at = Column(DateTime, default=datetime.utcnow)

    experience = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    rankings = relationship("Ranking", back_populates="candidate", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="candidate")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    company = Column(String(255))
    title = Column(String(255))
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # null + is_current=True means "Present"
    is_current = Column(Integer, default=0)  # 0/1 boolean (portable across PG versions)
    description = Column(Text)
    confidence_score = Column(Float)

    candidate = relationship("Candidate", back_populates="experience")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    institution = Column(String(255))
    degree = Column(String(255))
    field_of_study = Column(String(255))
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    confidence_score = Column(Float)

    candidate = relationship("Candidate", back_populates="education")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    skill_name = Column(String(255))
    category = Column(String(100))  # e.g. "programming_language", "tool", "soft_skill"
    confidence_score = Column(Float)

    candidate = relationship("Candidate", back_populates="skills")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    raw_text = Column(Text)
    source_url = Column(String(1024), nullable=True)  # null if pasted manually
    required_skills = Column(JSON)  # list[str], extracted by the agent
    created_at = Column(DateTime, default=datetime.utcnow)

    rankings = relationship("Ranking", back_populates="job", cascade="all, delete-orphan")


class Ranking(Base):
    __tablename__ = "rankings"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    score = Column(Float)  # 0-100
    rationale = Column(Text)  # the agent's reasoning for the score
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    ranked_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="rankings")
    job = relationship("JobDescription", back_populates="rankings") 