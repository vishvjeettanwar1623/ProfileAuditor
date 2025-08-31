from fastapi import APIRouter

from app.api.endpoints import resume, verification, score, invite

router = APIRouter()

# Include all endpoint routers
router.include_router(resume.router, prefix="/resume", tags=["resume"])
router.include_router(verification.router, prefix="/verification", tags=["verification"])
router.include_router(score.router, prefix="/score", tags=["score"])
router.include_router(invite.router, prefix="/invite", tags=["invite"])