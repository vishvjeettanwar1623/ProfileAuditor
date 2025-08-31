from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.scoring_service import calculate_reality_score
from app.models.score import ScoreResponse

router = APIRouter()

# In-memory storage for demo purposes
score_storage = {}

@router.get("/{resume_id}", response_model=ScoreResponse)
async def get_score(resume_id: str):
    """Get the reality score for a resume"""
    # Check if score already calculated
    if resume_id in score_storage:
        return score_storage[resume_id]
    
    # Get verification results
    from app.api.endpoints.verification import verification_storage
    
    if resume_id not in verification_storage:
        raise HTTPException(status_code=404, detail="Verification not found. Please start verification first.")
    
    verification_data = verification_storage[resume_id]
    
    # Check verification status
    verification_status = verification_data.get("status")
    if verification_status == "processing":
        raise HTTPException(
            status_code=202, 
            detail="Verification is still in progress. Please wait and try again."
        )
    elif verification_status == "error":
        raise HTTPException(
            status_code=400, 
            detail=f"Verification failed: {verification_data.get('error', 'Unknown error')}"
        )
    elif verification_status != "completed":
        raise HTTPException(
            status_code=400, 
            detail="Verification not completed. Cannot calculate score."
        )
    
    # Calculate score
    score_result = calculate_score(resume_id, verification_data)
    
    # Store score
    score_storage[resume_id] = score_result
    
    return score_result

def calculate_score(resume_id: str, verification_data: Dict[str, Any]) -> ScoreResponse:
    """Calculate reality score based on verification results"""
    # Get verification data
    github_results = verification_data.get("github", {})
    twitter_results = verification_data.get("twitter", {})
    linkedin_results = verification_data.get("linkedin", {})
    
    # Calculate score using scoring service
    score, breakdown = calculate_reality_score(
        github_results=github_results,
        twitter_results=twitter_results,
        linkedin_results=linkedin_results,
        verified_skills=verification_data.get("verified_skills", []),
        unverified_skills=verification_data.get("unverified_skills", []),
        verified_projects=verification_data.get("verified_projects", []),
        unverified_projects=verification_data.get("unverified_projects", [])
    )
    
    return ScoreResponse(
        resume_id=resume_id,
        score=score,
        breakdown=breakdown,
        verified_skills=verification_data.get("verified_skills", []),
        unverified_skills=verification_data.get("unverified_skills", []),
        verified_projects=verification_data.get("verified_projects", []),
        unverified_projects=verification_data.get("unverified_projects", [])
    )