from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional

from app.services.github_service import verify_github_claims
from app.services.twitter_service import verify_twitter_claims
from app.services.linkedin_service import verify_linkedin_claims
from app.models.verification import VerificationResponse, VerificationResult

router = APIRouter()

# In-memory storage for demo purposes
verification_storage = {}

from pydantic import BaseModel

class VerificationRequest(BaseModel):
    github_username: Optional[str] = None
    twitter_username: Optional[str] = None
    linkedin_username: Optional[str] = None

@router.post("/{resume_id}", response_model=VerificationResponse)
async def start_verification(resume_id: str, verification_request: VerificationRequest):
    """Start the verification process for a resume"""
    from app.api.endpoints.resume import resume_storage
    
    # Add detailed logging
    print(f"\n\n===== VERIFICATION REQUEST =====\nResume ID: {resume_id}")
    print(f"Available resume IDs in storage: {list(resume_storage.keys())}")
    print(f"Social usernames - GitHub: {verification_request.github_username}, Twitter: {verification_request.twitter_username}, LinkedIn: {verification_request.linkedin_username}")
    
    if resume_id not in resume_storage:
        error_msg = f"Resume not found with ID: {resume_id}"
        print(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    
    resume_data = resume_storage[resume_id]
    print(f"Resume data: {resume_data}")
    
    # Ensure resume_data is a dictionary
    if not isinstance(resume_data, dict):
        error_msg = f"Invalid resume data format: {type(resume_data)}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    if resume_data.get("status") != "completed":
        # If resume processing failed with a specific error, surface it directly
        if resume_data.get("status") == "error" and resume_data.get("error"):
            error_msg = str(resume_data.get("error"))
            print(f"Resume is in error state: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        error_msg = f"Resume processing not completed. Status: {resume_data.get('status')}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
        
    # Ensure skills exist and are in the correct format
    skills = resume_data.get("skills", [])
    if not skills:
        print("No skills found in resume data, adding default skills")
        resume_data["skills"] = ["Python", "Data Analysis"]
    elif not isinstance(skills, list):
        print(f"Skills is not a list, converting: {skills}")
        if isinstance(skills, str):
            resume_data["skills"] = [skills]
        else:
            resume_data["skills"] = ["Python", "Data Analysis"]
    
    # Ensure projects exist and are in the correct format
    projects = resume_data.get("projects", [])
    if not projects:
        print("No projects found in resume data; leaving empty list to avoid default placeholders")
        resume_data["projects"] = []
    elif not isinstance(projects, list):
        print(f"Projects is not a list, converting: {projects}")
        if isinstance(projects, str):
            resume_data["projects"] = [{"name": projects}]
        elif isinstance(projects, dict):
            resume_data["projects"] = [projects]
        else:
            resume_data["projects"] = []
    
    print(f"Final resume data for verification: {resume_data}")
    
    # Store initial verification status
    verification_storage[resume_id] = {
        "resume_id": resume_id,
        "status": "processing",
        "message": "Verification in progress"
    }
    
    # Process verification synchronously for better compatibility with serverless
    try:
        await process_verification(
            resume_id=resume_id,
            resume_data=resume_data,
            github_username=verification_request.github_username,
            twitter_username=verification_request.twitter_username,
            linkedin_username=verification_request.linkedin_username
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

@router.get("/{resume_id}", response_model=VerificationResult)
async def get_verification(resume_id: str):
    """Get verification results for a resume"""
    if resume_id not in verification_storage:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    verification_data = verification_storage[resume_id]
    
    # Check if processing is complete
    if verification_data.get("status") == "processing":
        return VerificationResponse(
            resume_id=resume_id,
            status="processing",
            message="Verification is still in progress"
        )
    
    return verification_data

async def process_verification(resume_id: str, resume_data: Dict[str, Any], github_username: Optional[str] = None, twitter_username: Optional[str] = None, linkedin_username: Optional[str] = None):
    """Process verification against external sources"""
    try:
        print(f"Starting verification process for resume_id: {resume_id}")
        print(f"Resume data for verification: {resume_data}")
        print(f"Social usernames passed to process_verification - GitHub: {github_username}, Twitter: {twitter_username}, LinkedIn: {linkedin_username}")
        
        # Extract skills and projects from resume data
        skills_data = resume_data.get("skills", [])
        skills = []
        
        # Handle skills which could be a list of strings or a list containing a list
        if isinstance(skills_data, list):
            for skill in skills_data:
                if isinstance(skill, str):
                    skills.append(skill)
                elif isinstance(skill, list):
                    # If skills is a list containing a list, flatten it
                    skills.extend([s for s in skill if isinstance(s, str)])
        
        print(f"Skills to verify: {skills}")
        
        # Handle projects which could be a list of dictionaries or strings
        projects_data = resume_data.get("projects", [])
        projects = []
        
        for project in projects_data:
            if isinstance(project, dict) and "name" in project:
                projects.append(project["name"])
            elif isinstance(project, str):
                projects.append(project)
            else:
                print(f"Skipping project with unexpected format: {project}")
        
        print(f"Projects to verify: {projects}")
        
        # If no projects were extracted, keep empty and do not inject defaults
        if not projects:
            print("No valid projects found in resume; skipping project verification as list is empty")
        
        # Use passed usernames if provided, otherwise fallback to resume data
        if not github_username:
            github_username = resume_data.get("github_username")
        if not twitter_username:
            twitter_username = resume_data.get("twitter_username")
        if not linkedin_username:
            linkedin_username = resume_data.get("linkedin_username")
        
        print(f"Final social usernames for verification - GitHub: {github_username}, Twitter: {twitter_username}, LinkedIn: {linkedin_username}")
        
        # Initialize verification results
        github_results = {}
        twitter_results = {}
        linkedin_results = {}
        
        print(f"About to start verification with usernames:")
        print(f"  GitHub: {github_username}")
        print(f"  Twitter: {twitter_username}")
        print(f"  LinkedIn: {linkedin_username}")
        
        # Verify with GitHub if username provided
        if github_username:
            print(f"Starting GitHub verification for username: {github_username}")
            try:
                github_results = verify_github_claims(github_username, skills, projects)
                print(f"GitHub verification completed. Results: {github_results}")
            except Exception as e:
                print(f"GitHub verification failed with error: {str(e)}")
                github_results = {"error": str(e)}
        else:
            print("No GitHub username provided, skipping GitHub verification")
        
        # Verify with Twitter if username provided
        if twitter_username:
            print(f"Starting Twitter verification for username: {twitter_username}")
            try:
                twitter_results = verify_twitter_claims(twitter_username, skills, projects)
                print(f"Twitter verification completed. Results: {twitter_results}")
            except Exception as e:
                print(f"Twitter verification failed with error: {str(e)}")
                twitter_results = {"error": str(e)}
        else:
            print("No Twitter username provided, skipping Twitter verification")
        
        # Verify with LinkedIn (mock data)
        if linkedin_username:
            print(f"Starting LinkedIn verification for username: {linkedin_username}")
            try:
                linkedin_results = verify_linkedin_claims(linkedin_username, skills, projects)
                print(f"LinkedIn verification completed. Results: {linkedin_results}")
            except Exception as e:
                print(f"LinkedIn verification failed with error: {str(e)}")
                linkedin_results = {"error": str(e)}
        else:
            print("No LinkedIn username provided, skipping LinkedIn verification")
        
        # Combine all verification results
        verification_result = {
            "resume_id": resume_id,
            "status": "completed",
            "github": github_results,
            "twitter": twitter_results,
            "linkedin": linkedin_results,
            "verified_skills": [],
            "verified_projects": [],
            "unverified_skills": [],
            "unverified_projects": []
        }
        
        # Categorize verified and unverified skills/projects
        for skill in skills:
            # Debug logging
            print(f"Checking skill: {skill}")
            print(f"GitHub verified skills: {github_results.get('verified_skills', [])}")
            print(f"Twitter verified skills: {twitter_results.get('verified_skills', [])}")
            print(f"LinkedIn verified skills: {linkedin_results.get('verified_skills', [])}")
            
            if (
                skill in github_results.get("verified_skills", []) or
                skill in twitter_results.get("verified_skills", []) or
                skill in linkedin_results.get("verified_skills", [])
            ):
                verification_result["verified_skills"].append(skill)
                print(f"Skill '{skill}' was verified")
            else:
                verification_result["unverified_skills"].append(skill)
                print(f"Skill '{skill}' was NOT verified")
        
        for project in projects:
            # Debug logging
            print(f"Checking project: {project}")
            print(f"GitHub verified projects: {github_results.get('verified_projects', [])}")
            print(f"Twitter verified projects: {twitter_results.get('verified_projects', [])}")
            print(f"LinkedIn verified projects: {linkedin_results.get('verified_projects', [])}")
            
            if (
                project in github_results.get("verified_projects", []) or
                project in twitter_results.get("verified_projects", []) or
                project in linkedin_results.get("verified_projects", [])
            ):
                verification_result["verified_projects"].append(project)
                print(f"Project '{project}' was verified")
            else:
                verification_result["unverified_projects"].append(project)
                print(f"Project '{project}' was NOT verified")
        
        # Update storage with verification results
        verification_storage[resume_id] = verification_result
        
    except Exception as e:
        # Update storage with error
        verification_storage[resume_id] = {
            "resume_id": resume_id,
            "status": "error",
            "error": str(e)
        }