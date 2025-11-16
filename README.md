# Resume Parser API

A **Resume Parsing API** built with FastAPI that extracts structured data from PDF and DOCX resumes using LLMs (Groq / LangChain) and validates the output with **Pydantic models**.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Installation](#installation)  
5. [Environment Variables](#environment-variables)  
6. [Usage](#usage)  
7. [API Endpoints](#api-endpoints)  
8. [Project Structure](#project-structure)  
9. [Project Flow Diagram](#project-flow-diagram)  
10. [Error Handling](#error-handling)  
11. [Improvements & Future Work](#improvements--future-work)  
12. [Contributing](#contributing)  
13. [License](#license)  
---

## Overview

This project provides an automated way to extract structured resume information such as:

- **Contact Information**  
- **Summary**  
- **Skills**  
- **Education**  
- **Experience**  
- **Certifications**

The extracted information is validated with **Pydantic models** to ensure correctness and consistency.

---

## Features

- Upload PDF or DOCX resumes and parse them automatically.  
- Extracts structured information using a large language model (Groq / LangChain).  
- Validates the parsed output using **Pydantic**.  
- Stores parsed resumes with unique `document_id` in a JSON metadata file.  
- Provides endpoints to fetch previously uploaded resumes.  
- Logging using `utils.logger` for easy debugging.  
- CORS enabled for frontend integration.  

---

## Tech Stack

- **FastAPI** – High-performance Python API framework.  
- **Pydantic** – For request/response validation and structured data.  
- **PyMuPDF (fitz)** – Extract text from PDF files.  
- **python-docx** – Extract text from DOCX files.  
- **LangChain / ChatGroq** – LLM for parsing resume text into structured JSON.  
- **Logging** – Advanced logging.  
- **UUID** – For unique document identifiers.  
- **JSON** – data storage.  

---

## Installation

```bash
# Clone repository
git clone https://github.com/Agaramsaikrishna/resume-parser.git
cd resume-parser-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables
Create a .env file with the following:
```
UPLOAD_DIR=./data/uploads
METADATA_FILE=./data/data.json
LLM_PROVIDER=groq
GROQ_API_KEY=<your_groq_api_key>
GROQ_MODEL=openai/gpt-oss-20b
LOG_LEVEL=INFO
```

## Usage
### Start the API:
``` 
uvicorn app.main:app --reload
``` 
- Upload resume: POST /api/upload

- Fetch resume: GET /api/resume/{document_id}

### Use a tool like Postman or cURL to test the endpoints.

API Endpoints
| Endpoint                    | Method | Request            | Response         | Description                           |
| --------------------------- | ------ | ------------------ | ---------------- | ------------------------------------- |
| `/api/upload`               | POST   | `file: UploadFile` | `UploadResponse` | Upload a PDF/DOCX resume and parse it |
| `/api/resume/{document_id}` | GET    | `document_id`      | `ResumeData`     | Fetch parsed resume by ID             |


Request example for upload (cURL):
```
curl -X POST "http://localhost:8000/api/upload" 
\-F "file=@/path/to/resume.pdf"
```
## Project Structure
```
resume-parser/
│
├── app/
│   ├── main.py                  # FastAPI app with routes
│   ├── models.py                # Pydantic models  (ResumeData, UploadResponse)
│   ├── services/
│   │   ├── parser.py            # File processing, text extraction
│   │   └── llm_service.py       # LLM integration, JSON extraction
│   └── utils/
│       └── logger.py            # Logger setup (Loguru)
│
├── data/                        # Uploaded files and metadata
│
├── requirements.txt             # Python dependencies
└── README.md                     # Project documentation
```
## Project Flow Diagram'
```
Resume File --> Upload Endpoint --> Text Extraction --> LLM Parsing --> Validation --> Save data --> Fetch Endpoint
```
## Error Handling

- 400 Bad Request – Unsupported file type or invalid resume content.

- 404 Not Found – Resume not found for the given document_id.

- 500 Internal Server Error – File save or processing failure.



## Improvements & Future Work

1. Database Integration

    - Replace JSON metadata file with PostgreSQL or MongoDB for scalability.

2. Authentication / Authorization

    - Add JWT or OAuth2 to secure the API endpoints.

3. Frontend Dashboard

    - Show uploaded resumes, parsed fields, and allow search/filtering.


4. Unit & Integration Testing

    - Add pytest tests for routes, services, and LLM parsing.

5. Error Handling & Monitoring

     - Add Prometheus for logging and monitoring production errors.

6. Support More File Types

    - Add TXT, RTF, or HTML resume parsing support.

## License
    MIT License © 2025