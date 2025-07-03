from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import asyncio
import aiofiles
import tempfile
import shutil
from src.document_processor import DocumentProcessor
from src.matching_engine import MatchingEngine
from src.enhanced_document_processor import EnhancedDocumentProcessor
import yaml
import mimetypes

# Load configuration
def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Initialize processors
document_processor = EnhancedDocumentProcessor()
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
                raise HTTPException(status_code=413, detail="File too large")
        await file.seek(0)
        
        # Check file type
        content_type, _ = mimetypes.guess_type(str(file.filename))
        if content_type not in config['security']['file_validation']['allowed_types']:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {content_type}")
        return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating file: {str(e)}")

# Dashboard
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Resume Management
@router.get("/resumes", response_class=HTMLResponse)
async def resumes(request: Request):
    return templates.TemplateResponse("resumes.html", {"request": request})

@router.post("/api/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str = Form(...),
    email: str = Form(...)
):
    try:
        # Validate file
        await validate_file(file)
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/resumes")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{candidate_name}_{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
            
        # Process resume
        doc_result = document_processor.process_document(str(file_path))
        if not doc_result:
            raise HTTPException(status_code=400, detail="Could not process resume")
            
        # Extract additional information
        skills = document_processor.extract_skills(doc_result['content'])
        experience = document_processor.extract_experience(doc_result['content'])
        education = document_processor.extract_education(doc_result['content'])
        
        # Save metadata
        metadata = {
            "candidate_name": candidate_name,
            "email": email,
            "filename": file.filename,
            "skills": skills,
            "years_experience": experience,
            "education": education,
            "uploaded_at": datetime.now().isoformat(),
            "processed_at": doc_result['metadata']['processed_at']
        }
        
        metadata_path = upload_dir / f"{file_path.stem}_metadata.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
            
        return {
            "message": "Resume uploaded and processed successfully",
            "filename": file.filename,
            "metadata": metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Job Management
@router.get("/jobs", response_class=HTMLResponse)
async def jobs(request: Request):
    return templates.TemplateResponse("jobs.html", {"request": request})

@router.post("/api/jobs")
async def create_job(
    job_title: str = Form(...),
    department: str = Form(...),
    description: str = Form(...),
    skills: str = Form(...)
):
    try:
        # Create jobs directory if it doesn't exist
        jobs_dir = Path("uploads/jobs")
        jobs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create job metadata
        job_id = int(datetime.now().timestamp())
        job_data = {
            "id": job_id,
            "title": job_title,
            "department": department,
            "description": description,
            "skills": [s.strip() for s in skills.split(',')],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Save job data
        job_path = jobs_dir / f"job_{job_id}.json"
        async with aiofiles.open(job_path, 'w') as f:
            await f.write(json.dumps(job_data, indent=2))
            
        return {
            "message": "Job created successfully",
            "job_id": job_id,
            "job_data": job_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Matching
@router.get("/matches", response_class=HTMLResponse)
async def matches(request: Request):
    return templates.TemplateResponse("matches.html", {"request": request})

@router.get("/matches/{match_id}", response_class=HTMLResponse)
async def match_details(request: Request, match_id: int):
    return templates.TemplateResponse("match_details.html", {
        "request": request,
        "match_id": match_id
    })

# Analytics
@router.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

# API Endpoints for Dashboard
@router.get("/api/dashboard/stats")
async def dashboard_stats():
    try:
        # Count resumes
        resume_dir = Path("uploads/resumes")
        total_resumes = len(list(resume_dir.glob("*.pdf"))) + len(list(resume_dir.glob("*.docx")))
        
        # Count active jobs
        jobs_dir = Path("uploads/jobs")
        active_jobs = len([f for f in jobs_dir.glob("*.json") if json.loads(f.read_text())["status"] == "active"])
        
        # Count matches
        matches_dir = Path("uploads/matches")
        matches_dir.mkdir(exist_ok=True)
        total_matches = len(list(matches_dir.glob("*.json")))
        
        # Calculate success rate
        successful_matches = len([f for f in matches_dir.glob("*.json") 
                                if json.loads(f.read_text())["score"] >= 0.7])
        success_rate = (successful_matches / total_matches * 100) if total_matches > 0 else 0
        
        return {
            "totalResumes": total_resumes,
            "activeJobs": active_jobs,
            "totalMatches": total_matches,
            "successRate": round(success_rate, 1)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/matches/recent")
async def recent_matches():
    try:
        matches_dir = Path("uploads/matches")
        matches_dir.mkdir(exist_ok=True)
        
        # Get all match files and sort by date
        match_files = sorted(
            matches_dir.glob("*.json"),
            key=lambda x: json.loads(x.read_text())["date"],
            reverse=True
        )[:10]  # Get 10 most recent
        
        matches = []
        for match_file in match_files:
            match_data = json.loads(match_file.read_text())
            matches.append({
                "id": match_data["id"],
                "resumeName": match_data["resume_name"],
                "jobTitle": match_data["job_title"],
                "score": round(match_data["score"] * 100),
                "date": match_data["date"],
                "status": match_data["status"]
            })
            
        return matches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/skills/top")
async def top_skills():
    try:
        # Get all resume metadata files
        resume_dir = Path("uploads/resumes")
        skill_counts = {}
        
        for metadata_file in resume_dir.glob("*_metadata.json"):
            metadata = json.loads(metadata_file.read_text())
            for skill in metadata.get("skills", []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
                
        # Sort skills by count
        top_skills = sorted(
            [{"name": skill, "count": count} for skill, count in skill_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]  # Get top 10 skills
        
        return top_skills
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch Processing
async def process_batch_file(file: UploadFile, job_id: int, matches_dir: Path):
    """Process a single file in batch mode."""
    try:
        # Validate and save file
        await validate_file(file)
        temp_file = Path(tempfile.gettempdir()) / f"rme_temp_{file.filename}"
        
        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)
            
        # Process resume
        doc_result = document_processor.process_document(str(temp_file))
        if not doc_result:
            return None
            
        # Get job description
        job_file = Path("uploads/jobs") / f"job_{job_id}.json"
        if not job_file.exists():
            return None
            
        job_data = json.loads(job_file.read_text())
        
        # Match resume against job
        match_result = matching_engine.match(
            job_data["description"],
            doc_result['content']
        )
        
        # Create match record
        match_id = int(datetime.now().timestamp())
        match_data = {
            "id": match_id,
            "job_id": job_id,
            "resume_name": file.filename,
            "job_title": job_data["title"],
            "score": match_result["score"],
            "matching_skills": match_result["matching_skills"],
            "missing_skills": match_result["missing_skills"],
            "date": datetime.now().isoformat(),
            "status": "Matched" if match_result["score"] >= 0.7 else "Pending"
        }
        
        # Save match data
        match_file = matches_dir / f"match_{match_id}.json"
        async with aiofiles.open(match_file, 'w') as f:
            await f.write(json.dumps(match_data, indent=2))
            
        return match_data
        
    except Exception as e:
        print(f"Error processing {file.filename}: {str(e)}")
        return None
        
    finally:
        if temp_file.exists():
            temp_file.unlink()

@router.post("/api/batch/process")
async def batch_process(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    job_id: int = Form(...)
):
    try:
        # Create matches directory
        matches_dir = Path("uploads/matches")
        matches_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify job exists
        job_file = Path("uploads/jobs") / f"job_{job_id}.json"
        if not job_file.exists():
            raise HTTPException(status_code=404, detail="Job not found")
            
        # Process files in background
        async def process_files():
            tasks = [process_batch_file(file, job_id, matches_dir) for file in files]
            results = await asyncio.gather(*tasks)
            return [r for r in results if r is not None]
            
        background_tasks.add_task(process_files)
        
        return {
            "message": "Batch processing started",
            "file_count": len(files),
            "job_id": job_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# User Profile
@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# Settings
@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request}) 