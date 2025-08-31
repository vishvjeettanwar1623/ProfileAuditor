from pydantic import BaseModel
from typing import List, Dict, Any

class ScoreBreakdown(BaseModel):
    """Model for score breakdown"""
    github_score: float
    twitter_score: float
    linkedin_score: float
    skills_score: float
    projects_score: float

class ScoreResponse(BaseModel):
    """Response model for reality score"""
    resume_id: str
    score: float
    breakdown: ScoreBreakdown
    verified_skills: List[str] = []
    unverified_skills: List[str] = []
    verified_projects: List[str] = []
    unverified_projects: List[str] = []