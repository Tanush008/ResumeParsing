from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from .database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    filepath = Column(String)
    extracted_text = Column(Text)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    email = Column(String)
    phone = Column(String)

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)

    candidate_id = Column(Integer)

    skill_name = Column(String)


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)

    candidate_id = Column(Integer)

    degree = Column(String)

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True)

    candidate_id = Column(Integer)

    company = Column(String)
    role = Column(String)
    duration = Column(String)
