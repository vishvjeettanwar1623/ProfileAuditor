from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ResumeResponse(BaseModel):
    """Response model for resume upload"""
    resume_id: str
    message: str
    status: str

class ResumeData(BaseModel):
    """Model for parsed resume data"""
    resume_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    job_description: Optional[str] = None
    raw_text: Optional[str] = None
    status: str