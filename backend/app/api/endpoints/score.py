from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.services.scoring_service import calculate_reality_score
from app.services.job_matching_service import evaluate_role_fit
from app.services.ats_service import evaluate_ats_health
from app.models.score import ScoreResponse

router = APIRouter()

# In-memory storage for demo purposes
score_storage = {}


class LiveAtsRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None


@router.post("/live-ats")
async def evaluate_live_ats(request: LiveAtsRequest):
    """Evaluate ATS score and suggestions in real-time for live editor"""
    from app.services.resume_parser import extract_github_username, extract_leetcode_username
    
    text = request.resume_text or ""
    gh_handle = extract_github_username(text)
    lc_handle = extract_leetcode_username(text)
    
    parsed_stub = {
        "github_username": gh_handle,
        "leetcode_username": lc_handle,
    }
    
    ats_analysis = evaluate_ats_health(raw_text=text, parsed_resume=parsed_stub)
    
    role_analysis = None
    if request.job_description and request.job_description.strip():
        # Fast rule-based matching of mentioned skills
        from app.services.job_matching_service import extract_jd_requirements, _skill_matches
        requirements = extract_jd_requirements(request.job_description)
        req_skills = requirements.get("required_skills", [])
        
        found_in_text = []
        missing_in_text = []
        for s in req_skills:
            if re_match := s.lower() in text.lower():
                found_in_text.append(s)
            else:
                missing_in_text.append(s)
                
        total_req = len(req_skills)
        fit_score = round((len(found_in_text) / total_req * 100), 1) if total_req > 0 else 100.0
        
        role_analysis = {
            "role_title": requirements.get("role_title", "Target Role"),
            "role_fit_score": fit_score,
            "verified_requirements": found_in_text,
            "missing_requirements": missing_in_text,
            "total_required_count": total_req
        }
        
    return {
        "ats_score": ats_analysis.get("ats_score", 0),
        "ats_analysis": ats_analysis,
        "role_analysis": role_analysis,
        "detected_handles": {
            "github": gh_handle,
            "leetcode": lc_handle
        }
    }


@router.get("/{resume_id}", response_model=ScoreResponse)
async def get_score(resume_id: str):
    """Get the reality score, target role fit, and ATS health for a resume"""
    # Check if score already calculated
    if resume_id in score_storage:
        return score_storage[resume_id]
    
    # Get verification results
    from app.api.endpoints.verification import verification_storage
    from app.api.endpoints.resume import resume_storage
    
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
