from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.github_service import verify_github_claims
from app.services.leetcode_service import verify_leetcode_claims
from app.models.verification import VerificationResponse, VerificationResult

router = APIRouter()

# In-memory storage for demo purposes
verification_storage = {}


class VerificationRequest(BaseModel):
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None


@router.post("/{resume_id}", response_model=VerificationResponse)
async def start_verification(resume_id: str, verification_request: VerificationRequest):
    """Start the verification process for a resume"""
    from app.api.endpoints.resume import resume_storage
    
    print(f"\n\n===== VERIFICATION REQUEST =====\nResume ID: {resume_id}")
    print(f"Available resume IDs in storage: {list(resume_storage.keys())}")
    print(f"Handles - GitHub: {verification_request.github_username}, LeetCode: {verification_request.leetcode_username}")
    
    if resume_id not in resume_storage:
        error_msg = f"Resume not found with ID: {resume_id}"
        print(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    
    resume_data = resume_storage[resume_id]
    
    if not isinstance(resume_data, dict):
        error_msg = f"Invalid resume data format: {type(resume_data)}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    if resume_data.get("status") != "completed":
        if resume_data.get("status") == "error" and resume_data.get("error"):
            error_msg = str(resume_data.get("error"))
            print(f"Resume is in error state: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        error_msg = f"Resume processing not completed. Status: {resume_data.get('status')}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
        
    # Store initial verification status
    verification_storage[resume_id] = {
        "resume_id": resume_id,
        "status": "processing",
        "message": "Verification in progress"
    }
    
    try:
        await process_verification(
            resume_id=resume_id,
            resume_data=resume_data,
            github_username=verification_request.github_username,
            leetcode_username=verification_request.leetcode_username
        )
        print(f"Verification process completed for resume ID: {resume_id}")
        
        return VerificationResponse(
            resume_id=resume_id,
            status="completed",
            message="Verification completed"
        )
    except Exception as e:
        error_msg = f"Error during verification process: {str(e)}"
        print(error_msg)
        verification_storage[resume_id] = {
            "resume_id": resume_id,
            "status": "error",
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/{resume_id}")
async def get_verification(resume_id: str):
    """Get verification results for a resume"""
    if resume_id not in verification_storage:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return verification_storage[resume_id]


async def process_verification(
    resume_id: str,
    resume_data: Dict[str, Any],
    github_username: Optional[str] = None,
    leetcode_username: Optional[str] = None
):
    """Process verification against GitHub and LeetCode"""
    try:
        print(f"Starting verification process for resume_id: {resume_id}")
        
        # 1. Extract technical skills, soft skills, and projects
        tech_data = resume_data.get("technical_skills") or resume_data.get("skills", [])
        technical_skills = []
        if isinstance(tech_data, list):
            for s in tech_data:
                if isinstance(s, str) and s.strip():
                    technical_skills.append(s.strip())
                elif isinstance(s, list):
