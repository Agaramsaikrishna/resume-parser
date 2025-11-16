from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class JobEntry(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: Optional[List[str]] = Field(default_factory=list)

class EducationEntry(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None

class ResumeData(BaseModel):
    document_id: str
    contact: Optional[ContactInfo] = None
    summary: Optional[str] = None
    experience: Optional[List[JobEntry]] = Field(default_factory=list)
    education: Optional[List[EducationEntry]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    raw_text: Optional[str] = None



class UploadResponse(BaseModel):
    document_id: str