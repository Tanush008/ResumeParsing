from fastapi import FastAPI

from app.api.resume import router as resume_router
from app.api.parser import router as parser_router
from app.db.database import engine
from app.db.models import Base

from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Set up CORS middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)

app.include_router(
    parser_router,
    prefix="/parser",
    tags=["Parser"]
)


@app.get("/")
def home():
    return {
        "message": "ATS Backend Running"
    }
