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
            detail="Verification not completed. Cannot calculate score."
        )
    
    # Check if job description or raw text was stored
    resume_info = resume_storage.get(resume_id, {})
    job_description = resume_info.get("job_description")
    raw_text = resume_info.get("raw_text", "")
    
    # Calculate score
    score_result = calculate_score(
        resume_id=resume_id,
        verification_data=verification_data,
        job_description=job_description,
        raw_text=raw_text,
        parsed_resume=resume_info
    )
    
    # Store score
    score_storage[resume_id] = score_result
    
    return score_result


def calculate_score(
    resume_id: str,
    verification_data: Dict[str, Any],
    job_description: Optional[str] = None,
    raw_text: str = "",
    parsed_resume: Optional[Dict[str, Any]] = None
) -> ScoreResponse:
    """Calculate reality score, role fit, and ATS health based on verification results"""
    github_results = verification_data.get("github", {})
    leetcode_results = verification_data.get("leetcode", {})
    verified_skills = verification_data.get("verified_skills", [])
    unverified_skills = verification_data.get("unverified_skills", [])
    verified_projects = verification_data.get("verified_projects", [])
    unverified_projects = verification_data.get("unverified_projects", [])
    
    # 1. Calculate reality score using scoring service
    score, breakdown = calculate_reality_score(
        github_results=github_results,
        leetcode_results=leetcode_results,
        verified_skills=verified_skills,
        unverified_skills=unverified_skills,
        verified_projects=verified_projects,
        unverified_projects=unverified_projects
    )
    
    # 2. Evaluate role fit if target job description was provided
    role_analysis = None
    job_fit_score = None
    if job_description:
        role_analysis = evaluate_role_fit(
            job_description=job_description,
            verified_skills=verified_skills,
            unverified_skills=unverified_skills,
            verified_projects=verified_projects,
            github_results=github_results,
            leetcode_results=leetcode_results
        )
        if role_analysis:
            job_fit_score = role_analysis.get("role_fit_score")
            
    # 3. Evaluate ATS & Resume Health
    ats_analysis = None
    ats_score = None
    if parsed_resume or raw_text:
        ats_analysis = evaluate_ats_health(
            raw_text=raw_text,
            parsed_resume=parsed_resume or {}
        )
        if ats_analysis:
            ats_score = ats_analysis.get("ats_score")
    
    return ScoreResponse(
        resume_id=resume_id,
        score=score,
        breakdown=breakdown,
        verified_skills=verified_skills,
        unverified_skills=unverified_skills,
        soft_skills=verification_data.get("soft_skills", []),
        verified_projects=verified_projects,
        unverified_projects=unverified_projects,
        job_fit_score=job_fit_score,
        role_analysis=role_analysis,
        ats_score=ats_score,
        ats_analysis=ats_analysis
    )