import json
import os
from pathlib import Path

import google.generativeai as genai
from pydantic import ValidationError

from dotenv import load_dotenv
from app.schemas.parsed_resume import ParsedResume

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# Loaded once at import time, not re-read on every call.
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "resume_parser.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()


class ResumeParsingError(Exception):
    """Raised when Gemini's output can't be parsed/validated as a resume."""
    pass


def parse_resume(resume_text: str) -> dict:
    """
    Calls Gemini to extract structured fields from raw resume text, validates
    the result against ParsedResume, and returns a plain dict ready for
    storage or API response.

    Raises ResumeParsingError if Gemini fails, returns malformed JSON, or the
    JSON doesn't match the expected schema -- callers should catch this and
    return a clean 502/422 instead of letting it bubble up as a raw 500.
    """
    prompt = f"{_PROMPT_TEMPLATE}\n\nResume:\n\n{resume_text}"

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        raise ResumeParsingError(f"Gemini API call failed: {e}") from e

    text = (response.text or "").strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ResumeParsingError(f"Gemini did not return valid JSON: {e}") from e

    try:
        validated = ParsedResume.model_validate(data)
    except ValidationError as e:
        raise ResumeParsingError(f"Gemini output did not match expected schema: {e}") from e

    return validated.model_dump()