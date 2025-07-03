from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import update
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Profile, JobDescription as Job, Match
from app.core.matching import process_document, match_documents
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str
    department: str
    location: str
    job_type: str
    experience_level: str
    education: str
    skills: List[str]

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    department: str
    location: str
    job_type: str
    experience_level: str
    education: str
    skills: List[str]
    is_active: bool

    class Config:
        from_attributes = True
        model = Job

class MatchResponse(BaseModel):
    id: int
    profile_id: int
    job_id: int
    score: float
    analysis: dict
    status: str

    class Config:
        from_attributes = True

@router.post("/upload", response_model=Profile)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload and process a document (resume/CV)."""
    try:
        # Process document
        content, metadata = await process_document(file)
        
        # Create profile
        profile = Profile(
            user_id=current_user.id,
            filename=file.filename,
            content=content,
            profile_metadata=metadata,
            is_active=True
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return profile
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing document: {str(e)}"
        )

@router.post("/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new job description."""
    try:
        job = Job(
            user_id=current_user.id,
            title=job_data.title,
            description=job_data.description,
            requirements=job_data.requirements,
            department=job_data.department,
            location=job_data.location,
            job_type=job_data.job_type,
            experience_level=job_data.experience_level,
            education=job_data.education,
            skills=job_data.skills,
            is_active=True
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating job: {str(e)}"
        )

@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all active jobs."""
    jobs = db.query(Job).filter(
        Job.is_active == True
    ).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get job details."""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.is_active == True
    ).first()
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    return job

@router.post("/match", response_model=MatchResponse)
async def create_match(
    profile_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a match between a profile and a job."""
    try:
        # Get profile and job
        profile = db.query(Profile).filter(
            Profile.id == profile_id,
            Profile.is_active == True
        ).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.is_active == True
        ).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if match already exists
        existing_match = db.query(Match).filter(
            Match.profile_id == profile_id,
            Match.job_id == job_id
        ).first()
        if existing_match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match already exists"
            )
        
        # Create match
        score, analysis = await match_documents(
            str(profile.content),
            str(job.description)
        )
        match = Match(
            user_id=current_user.id,
            profile_id=profile_id,
            job_id=job_id,
            score=score,
            analysis=analysis,
            status="pending"
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match
    except Exception as e:
        logger.error(f"Error creating match: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating match: {str(e)}"
        )

@router.get("/matches", response_model=List[MatchResponse])
async def list_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all matches for the current user."""
    matches = db.query(Match).filter(
        Match.user_id == current_user.id
    ).all()
    return matches

@router.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get match details."""
    match = db.query(Match).filter(
        Match.id == match_id,
        Match.user_id == current_user.id
    ).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return match

@router.put("/matches/{match_id}", response_model=MatchResponse)
async def update_match_status(
    match_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update match status."""
    match = db.query(Match).filter(
        Match.id == match_id,
        Match.user_id == current_user.id
    ).first()
    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    if status not in ["pending", "accepted", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )
    
    # Update using SQLAlchemy update
    stmt = update(Match).where(Match.id == match_id).values(status=status)
    db.execute(stmt)
    db.commit()
    db.refresh(match)
    return match 