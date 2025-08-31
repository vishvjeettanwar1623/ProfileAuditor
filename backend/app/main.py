from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.api.routes import router as api_router

app = FastAPI(title="ProfileAuditor Backend", version="0.1.0")

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "ProfileAuditor Backend API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.options("/{path:path}")
def options_handler(path: str):
    return {"message": "OK"}
