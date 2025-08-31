from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class VerificationResponse(BaseModel):
    """Response model for verification status"""
    resume_id: str
    status: str
    message: Optional[str] = None

class VerificationResult(BaseModel):
    """Model for verification results"""
    resume_id: str
    status: str
    github: Dict[str, Any] = {}
    twitter: Dict[str, Any] = {}
    linkedin: Dict[str, Any] = {}
    verified_skills: List[str] = []
    unverified_skills: List[str] = []
    verified_projects: List[str] = []
    unverified_projects: List[str] = []
    error: Optional[str] = None