from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.email_service import send_interview_invitation
from app.models.invite import InviteResponse

router = APIRouter()

class InviteRequest(BaseModel):
    message: Optional[str] = None
    interview_date: Optional[str] = None
    interview_location: Optional[str] = None

@router.post("/{resume_id}", response_model=InviteResponse)
async def send_invite(resume_id: str, invite_data: InviteRequest, background_tasks: BackgroundTasks):
    """Send an interview invitation to a candidate"""
    # Get resume data
    from app.api.endpoints.resume import resume_storage
    
    if resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume_data = resume_storage[resume_id]
    
    # Get score data
    from app.api.endpoints.score import score_storage
    
    if resume_id not in score_storage:
        raise HTTPException(status_code=404, detail="Score not found. Calculate score first.")
    
    score_data = score_storage[resume_id]
    
    # Check if email is available
    if "email" not in resume_data or not resume_data["email"]:
        raise HTTPException(status_code=400, detail="Candidate email not available")
    
    # Send invitation in background
    background_tasks.add_task(
        send_interview_invitation,
        email=resume_data["email"],
        name=resume_data.get("name", "Candidate"),
        score=score_data.score,
        message=invite_data.message,
        interview_date=invite_data.interview_date,
        interview_location=invite_data.interview_location
    )
    
    return InviteResponse(
        resume_id=resume_id,
        email=resume_data["email"],
        status="sent",
        message="Interview invitation sent successfully"
    )