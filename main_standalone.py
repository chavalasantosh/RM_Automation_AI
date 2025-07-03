from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import logging
from datetime import datetime
import re
import logging.config
import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, field_validator
import uvicorn
from src.document_processor import DocumentProcessor
from src.matching_engine import MatchingEngine
from src.skill_categories import SkillRegistry, Skill, SkillCategory, SkillLevel
import yaml
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Inches, Pt
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import sys
import socket
import aiofiles
import asyncio
import mimetypes
import tempfile
import shutil
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes.web import router as web_router

# Load configuration
def load_config():
    """Load configuration from config.yaml."""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise

config = load_config()

# Get CORS settings from config
cors_config = config.get('security', {}).get('cors', {
    'allowed_origins': ['http://localhost:8001', 'http://127.0.0.1:8001'],
    'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allowed_headers': ['*'],
    'allow_credentials': True,
    'max_age': 3600
})

# Configure logging
logging_config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': config['app']['log_file'],
            'formatter': 'standard',
            'level': 'INFO'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': config['app']['log_level'],
            'propagate': True
        }
    }
}

# Create necessary directories
os.makedirs('logs', exist_ok=True)
os.makedirs(config['app']['temp_dir'], exist_ok=True)
os.makedirs('output', exist_ok=True)

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RME Enterprise AI Platform",
    description="Resume Matching Engine with AI-powered analysis and matching",
    version="1.0.0"
)

# Configure CORS with settings from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config['allowed_origins'],
    allow_credentials=cors_config['allow_credentials'],
    allow_methods=cors_config['allowed_methods'],
    allow_headers=cors_config['allowed_headers'],
    max_age=cors_config['max_age']
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
document_processor = DocumentProcessor()
matching_engine = MatchingEngine(config=config)

# File validation
async def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file."""
    try:
        # Check file size
        file_size = 0
        chunk_size = 8192
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            if file_size > config['security']['file_validation']['max_size']:
                raise HTTPException(
                    status_code=413,
                    detail="File too large"
                )
        await file.seek(0)
        
        # Check file type using mimetypes
        content_type, _ = mimetypes.guess_type(str(file.filename))
        if content_type not in config['security']['file_validation']['allowed_types']:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {content_type}"
            )
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error validating file"
        )

class MatchRequest(BaseModel):
    """Request model for matching."""
    job_description: str
    threshold: float = 0.7
    
    @field_validator('threshold')
    @classmethod
    def validate_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Threshold must be between 0 and 1')
        return v

@app.post("/match")
async def match_resumes(
    job_description: str,
    files: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """Match resumes against job description."""
    try:
        if not job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty"
            )
            
        if not files:
            raise HTTPException(
                status_code=400,
                detail="At least one resume file is required"
            )
            
        results = []
        temp_files = []
        
        try:
            for file in files:
                # Validate file
                await validate_file(file)
                
                # Save to temporary file
                temp_file = Path(tempfile.gettempdir()) / f"rme_temp_{file.filename}"
                temp_files.append(temp_file)
                
                async with aiofiles.open(temp_file, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                    
                # Process resume
                doc_result = document_processor.process_document(str(temp_file))
                if not doc_result or 'content' not in doc_result:
                    logger.warning(f"Could not process file {file.filename}")
                    continue
                    
                # Match against job description
                match_result = matching_engine.match(
                    job_description,
                    doc_result['content']
                )
                
                # Add model information
                result = {
                    "filename": file.filename,
                    "match_score": match_result['score'],
                    "matching_skills": match_result['matching_skills'],
                    "missing_skills": match_result['missing_skills'],
                    "section_scores": match_result['section_scores']
                }
                
                results.append(result)
                
            # Sort results by match score
            results.sort(key=lambda x: x["match_score"], reverse=True)
            
            return {
                "matches": results,
                "job_description": job_description,
                "processed_at": datetime.now().isoformat(),
                "model_info": {
                    "name": "Base Matching Engine",
                    "version": "1.0.0",
                    "enhanced": False
                }
            }
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Error cleaning up temporary file {temp_file}: {str(e)}")
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in match_resumes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    """Serve the GUI (index.html) from the templates directory."""
    return templates.TemplateResponse("index.html", {"request": request})

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

# Include web routes
app.include_router(web_router)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "message": "The page you're looking for doesn't exist."},
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(
        "500.html",
        {"request": request, "message": "Something went wrong on our end."},
        status_code=500
    )

if __name__ == "__main__":
    print("Starting RME Server...")
    print(f"Access the application at: http://{config['app']['host']}:{config['app']['port']}")
    print("Press Ctrl+C to stop the server")
    uvicorn.run(app, host=config['app']['host'], port=config['app']['port']) 