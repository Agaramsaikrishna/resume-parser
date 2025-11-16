from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import os

from app.utils.logger import setup_logger
from app.services import parser as resume_parser
from app.models import ResumeData, UploadResponse

# Initialize logger
logger = setup_logger(os.getenv("LOG_LEVEL", "INFO"))

# Initialize FastAPI
app = FastAPI(title="Resume Parser API", version="1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX), parse it, and return the document ID.
    """
    logger.info("Received file upload: %s", file.filename)
    ext = file.filename.lower().split(".")[-1]

    if ext not in ("pdf", "docx", "doc"):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported.")

    try:
        contents = await file.read()
        file_path = resume_parser.save_uploaded_file(contents, file.filename)
    except ValueError as exc:
        logger.error("Failed to save uploaded file: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        parsed = resume_parser.process_file(file_path, file.filename)
        return JSONResponse(content={"document_id": parsed["document_id"]})
    except ValueError as ve:
        logger.warning("Processing error for file %s: %s", file.filename, ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.exception("Unexpected error processing file %s: %s", file.filename, exc)
        raise HTTPException(status_code=500, detail="Failed to process resume.")


@app.get("/api/resume/{document_id}", response_model=ResumeData)
def get_resume(document_id: str):
    """
    Retrieve a parsed resume by its document ID.
    """
    logger.info("Fetching resume with document_id: %s", document_id)
    data = resume_parser.load_metadata(document_id)

    if not data:
        logger.warning("Resume not found: %s", document_id)
        raise HTTPException(status_code=404, detail="Resume not found")

    return JSONResponse(content=data)
