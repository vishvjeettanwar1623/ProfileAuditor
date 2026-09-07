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
                    technical_skills.extend([sub.strip() for sub in s if isinstance(sub, str) and sub.strip()])
        
        soft_data = resume_data.get("soft_skills", [])
        soft_skills = []
        if isinstance(soft_data, list):
            for s in soft_data:
                if isinstance(s, str) and s.strip():
                    soft_skills.append(s.strip())
                elif isinstance(s, list):
                    soft_skills.extend([sub.strip() for sub in s if isinstance(sub, str) and sub.strip()])

        print(f"Technical skills to verify ({len(technical_skills)}): {technical_skills}")
        print(f"Self-reported soft skills ({len(soft_skills)}): {soft_skills}")
        
        # Handle projects
        projects_data = resume_data.get("projects", [])
        projects = []
        for project in projects_data:
            if isinstance(project, dict) and "name" in project:
                projects.append(project["name"])
            elif isinstance(project, str) and project.strip():
                projects.append(project.strip())
        
        # Fallback to handles in resume data if not passed in request
        if not github_username:
            github_username = resume_data.get("github_username")
        if not leetcode_username:
            leetcode_username = resume_data.get("leetcode_username")
        
        print(f"Final handles - GitHub: {github_username}, LeetCode: {leetcode_username}")
        
        github_results = {}
        leetcode_results = {}
        
        # 2. Deep GitHub Verification
        if github_username:
            print(f"Starting Deep GitHub verification for: {github_username}")
            try:
                github_results = verify_github_claims(github_username, technical_skills, projects)
            except Exception as e:
                print(f"GitHub verification failed: {e}")
                github_results = {"error": str(e)}
        else:
            print("No GitHub handle provided")

        # 3. LeetCode GraphQL Verification (with language skill cross-referencing)
        if leetcode_username:
            print(f"Starting LeetCode verification for: {leetcode_username}")
            try:
                leetcode_results = verify_leetcode_claims(leetcode_username, claimed_skills=technical_skills)
            except Exception as e:
                print(f"LeetCode verification failed: {e}")
                leetcode_results = {"error": str(e)}
        else:
            print("No LeetCode handle provided")

        # 4. Compile verification results
        verification_result = {
            "resume_id": resume_id,
            "status": "completed",
            "github": github_results,
            "leetcode": leetcode_results,
            "verified_skills": [],
            "unverified_skills": [],
            "soft_skills": soft_skills,
            "verified_projects": [],
            "unverified_projects": []
        }
        
        # Categorize verified and unverified technical skills against GitHub AND LeetCode proof
        gh_verified_skills = set(github_results.get("verified_skills", []))
        lc_verified_skills = set(leetcode_results.get("verified_skills", []))
        all_verified_skills = gh_verified_skills.union(lc_verified_skills)

        for skill in technical_skills:
            if skill in all_verified_skills:
                verification_result["verified_skills"].append(skill)
                sources = []
                if skill in gh_verified_skills:
                    sources.append("GitHub")
                if skill in lc_verified_skills:
                    sources.append("LeetCode")
                print(f"Technical skill '{skill}' verified via {', '.join(sources)}")
            else:
                verification_result["unverified_skills"].append(skill)
                print(f"Technical skill '{skill}' NOT verified on GitHub or LeetCode")
        
        # Categorize verified and unverified projects against GitHub proof
        gh_verified_projects = github_results.get("verified_projects", [])
        for project in projects:
            if project in gh_verified_projects:
                verification_result["verified_projects"].append(project)
                print(f"Project '{project}' verified on GitHub")
            else:
                verification_result["unverified_projects"].append(project)
                print(f"Project '{project}' NOT verified on GitHub")
        
        verification_storage[resume_id] = verification_result
        
    except Exception as e:
        verification_storage[resume_id] = {
            "resume_id": resume_id,
            "status": "error",
            "error": str(e)
        }