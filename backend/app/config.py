"""
Centralized settings, loaded once at import time.

Why this exists: previously, GEMINI_API_KEY and DATABASE_URL were read via
scattered os.getenv() calls in database.py and parsed_service.py. If either
was missing or misspelled, you wouldn't find out until the first real
request hit that code path (e.g. the first resume parse), and the error
would be a confusing one from deep inside SQLAlchemy or the Gemini SDK.

This module reads and validates everything at import time, so a missing
env var fails immediately and loudly when the app starts, with a clear
message pointing at exactly which variable is missing.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill in a real value."
        )
    return value


class Settings:
    database_url: str = _require("DATABASE_URL")
    gemini_api_key: str = _require("GEMINI_API_KEY")

    # Optional, with a sensible default -- not every deploy needs to override this.
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
