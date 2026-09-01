from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ScoreBreakdown(BaseModel):
    """Model for score breakdown"""
    github_score: float
    leetcode_score: float
    skills_score: float
    projects_score: float

class ScoreResponse(BaseModel):
    """Response model for reality score"""
    resume_id: str
    score: float
    breakdown: ScoreBreakdown
    verified_skills: List[str] = []
    unverified_skills: List[str] = []
    soft_skills: List[str] = []
    verified_projects: List[str] = []
    unverified_projects: List[str] = []
    job_fit_score: Optional[float] = None
    role_analysis: Optional[Dict[str, Any]] = None
    ats_score: Optional[float] = None
    ats_analysis: Optional[Dict[str, Any]] = None