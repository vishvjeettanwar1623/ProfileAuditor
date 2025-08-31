from pydantic import BaseModel
from typing import Optional

class InviteResponse(BaseModel):
    """Response model for interview invitation"""
    resume_id: str
    email: str
    status: str
    message: str