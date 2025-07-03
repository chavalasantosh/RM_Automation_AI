from fastapi import APIRouter, Response, HTTPException, Form, UploadFile, File, Query, Request, Depends
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from pathlib import Path
import json
import csv
import io
import time
import logging
from typing import List, Optional, Any
from datetime import datetime, timedelta
import os
import shutil
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, func, and_
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from app.auth import get_current_user, get_optional_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user_from_request
from app.models import User, Match, Job, Profile
from app.database import get_db, SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")

# Create a custom OAuth2 scheme that doesn't require authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

@router.post("/api/matches/export", response_class=Response)
async def export_matches():
    try:
        matches_file = Path("data/matches.json")
        if not matches_file.exists():
            matches = []
        else:
            with open(matches_file, "r") as f:
                matches = json.load(f)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["job_title", "candidate", "match_score", "skills_match", "status", "date"])
        for m in matches:
            writer.writerow([m.get("job_title", ""), m.get("candidate", ""), m.get("match_score", ""), m.get("skills_match", ""), m.get("status", ""), m.get("date", "")])
        output.seek(0)
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=matches.csv"})
    except Exception as e:
        logger.error(f"Error exporting matches: {e}")
        raise HTTPException(status_code=500, detail="Internal server error (export)")

@router.post("/api/resumes/upload")
async def upload_resume_with_metadata(
    file: UploadFile = File(...),
    candidateName: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    notes: str = Form(None)
):
    """Upload resume with candidate metadata."""
    try:
        uploads_dir = Path("uploads")
        resumes_dir = uploads_dir / "resumes"
        resumes_dir.mkdir(exist_ok=True, parents=True)
        
        # Save resume file
        timestamp = int(time.time())
        filename = f"resume_{candidateName.replace(' ', '_')}_{timestamp}_{file.filename}"
        file_path = resumes_dir / filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # Save metadata
        metadata = {
            "candidateName": candidateName,
            "email": email,
            "phone": phone,
            "notes": notes,
            "filename": filename,
            "uploadDate": time.time(),
            "size": len(content)
        }
        
        metadata_filename = f"{filename}_metadata.json"
        metadata_path = resumes_dir / metadata_filename
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        return {
            "message": "Resume uploaded successfully",
            "filename": filename,
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Error uploading resume with metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):
    """Simple resume upload endpoint."""
    try:
        uploads_dir = Path("uploads")
        resumes_dir = uploads_dir / "resumes"
        resumes_dir.mkdir(exist_ok=True, parents=True)
        
        # Save resume file
        timestamp = int(time.time())
        filename = f"resume_{timestamp}_{file.filename}"
        file_path = resumes_dir / filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        return {
            "message": "Resume uploaded successfully",
            "filename": filename,
            "size": len(content)
        }
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/api/upload")
async def upload_files(
    jobTitle: str = Form(...),
    department: str = Form(...),
    location: str = Form(...),
    jobType: str = Form(...),
    experienceLevel: str = Form(...),
    skills: str = Form(...),
    education: str = Form(...),
    notes: str = Form(None),
    jobDescription: UploadFile = File(...),
    resumes: List[UploadFile] = File(...)
):
    try:
        uploads_dir = Path("uploads")
        jobs_dir = uploads_dir / "jobs"
        resumes_dir = uploads_dir / "resumes"
        jobs_dir.mkdir(exist_ok=True, parents=True)
        resumes_dir.mkdir(exist_ok=True, parents=True)
        
        # Save job description file
        job_desc_filename = f"{jobTitle.replace(' ', '_')}_{int(time.time())}_{jobDescription.filename}"
        job_desc_path = jobs_dir / job_desc_filename
        with open(job_desc_path, "wb") as f:
            f.write(await jobDescription.read())
            
        # Save resume files (multiple)
        profile_files = []
        for resume in resumes:
            profile_filename = f"{jobTitle.replace(' ', '_')}_{int(time.time())}_{resume.filename}"
            profile_path = resumes_dir / profile_filename
            with open(profile_path, "wb") as f:
                f.write(await resume.read())
            profile_files.append(profile_filename)
            
        return {
            "message": "Uploaded successfully",
            "job": {
                "title": jobTitle,
                "department": department,
                "location": location,
                "jobType": jobType,
                "experienceLevel": experienceLevel,
                "skills": skills,
                "education": education,
                "notes": notes,
                "jobDescription": job_desc_filename,
                "profiles": profile_files
            }
        }
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error (upload): {e}")

@router.get("/api/matches")
async def list_matches(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    score_range: Optional[str] = None,
    sort_by: Optional[str] = Query("score_desc", regex="^(score_desc|score_asc|date_desc|date_asc)$"),
    db: Session = Depends(get_db)
):
    """List matches with pagination and filtering."""
    try:
        # Temporarily disable authentication
        # Base query
        query = db.query(Match)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.join(Profile).join(Job).filter(
                or_(
                    Job.title.ilike(search_term),
                    Profile.filename.ilike(search_term),
                    Match.status.ilike(search_term)
                )
            )
        
        if job_id:
            query = query.filter(Match.job_id == job_id)
            
        if status:
            query = query.filter(Match.status == status)
            
        if score_range:
            try:
                min_score, max_score = map(float, score_range.split('-'))
                query = query.filter(Match.score >= min_score, Match.score <= max_score)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid score range format")
        
        # Apply sorting
        if sort_by == "score_desc":
            query = query.order_by(desc(Match.score))
        elif sort_by == "score_asc":
            query = query.order_by(asc(Match.score))
        elif sort_by == "date_desc":
            query = query.order_by(desc(Match.created_at))
        elif sort_by == "date_asc":
            query = query.order_by(asc(Match.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        matches = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Calculate stats
        stats = {
            "total_matches": total,
            "average_score": db.query(func.avg(Match.score)).scalar() or 0,
            "status_counts": {
                "pending": db.query(Match).filter(Match.status == "pending").count(),
                "reviewed": db.query(Match).filter(Match.status == "reviewed").count(),
                "rejected": db.query(Match).filter(Match.status == "rejected").count()
            }
        }
        
        # Format response
        matches_data = []
        for match in matches:
            profile = db.query(Profile).filter(Profile.id == match.profile_id).first()
            job = db.query(Job).filter(Job.id == match.job_id).first()
            
            if profile and job:
                matches_data.append({
                    "id": match.id,
                    "profile": {
                        "id": profile.id,
                        "filename": profile.filename,
                        "upload_date": profile.processed_at.isoformat() if profile.processed_at else None
                    },
                    "job": {
                        "id": job.id,
                        "title": job.title,
                        "department": job.department,
                        "location": job.location
                    },
                    "score": match.score,
                    "status": match.status,
                    "created_at": match.created_at.isoformat() if match.created_at else None,
                    "updated_at": match.updated_at.isoformat() if match.updated_at else None
                })
        
        return {
            "matches": matches_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error listing matches: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user)
) -> Any:
    """Home page - accessible without authentication."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": current_user}
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request
) -> Any:
    """Login page."""
    # Temporarily disable authentication check to stop redirect loop
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """Handle login form submission."""
    try:
        # Authenticate user
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Incorrect username or password"},
                status_code=401
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Create response with redirect
        response = RedirectResponse(url="/dashboard", status_code=303)
        
        # Set the token in a cookie for server-side authentication
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=False,  # Allow JavaScript access
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "An error occurred during login"},
            status_code=500
        )

@router.get("/logout")
async def logout():
    """Handle user logout."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Dashboard page."""
    # Temporarily disable authentication check
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": None,
            "profiles": [],
            "matches": []
        }
    )

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user)
) -> Any:
    """Upload page."""
    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "user": current_user}
    )

@router.get("/jobs", response_class=HTMLResponse)
async def jobs_page(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Jobs page."""
    # Temporarily disable authentication
    jobs = db.query(Job).filter(
        Job.is_active == True
    ).all()
    
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "user": None,
            "jobs": jobs
        }
    )

@router.get("/jobs/new", response_class=HTMLResponse)
async def new_job_page(
    request: Request
) -> Any:
    """New job page."""
    # Temporarily disable authentication
    return templates.TemplateResponse(
        "new_job.html",
        {"request": request, "user": None}
    )

@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_details_page(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Job details page."""
    # Temporarily disable authentication
    job = db.query(Job).filter(
        and_(
            Job.id == job_id,
            Job.is_active == True
        )
    ).first()
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Get matches for this job
    matches = db.query(Match).filter(
        Match.job_id == job_id
    ).all()
    
    return templates.TemplateResponse(
        "job_details.html",
        {
            "request": request,
            "user": None,
            "job": job,
            "matches": matches
        }
    )

@router.get("/matches", response_class=HTMLResponse)
async def matches_page(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Matches page."""
    # Temporarily disable authentication
    matches = db.query(Match).all()
    
    return templates.TemplateResponse(
        "matches.html",
        {
            "request": request,
            "user": None,
            "matches": matches
        }
    )

@router.get("/matches/{match_id}", response_class=HTMLResponse)
async def match_details_page(
    request: Request,
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Match details page."""
    match = db.query(Match).filter(
        and_(
            Match.id == match_id,
            Match.user_id == current_user.id
        )
    ).first()
    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    # Get profile and job details
    profile = db.query(Profile).filter(
        and_(
            Profile.id == match.profile_id,
            Profile.is_active == True
        )
    ).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    job = db.query(Job).filter(
        and_(
            Job.id == match.job_id,
            Job.is_active == True
        )
    ).first()
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    return templates.TemplateResponse(
        "match_details.html",
        {
            "request": request,
            "user": current_user,
            "match": match,
            "profile": profile,
            "job": job
        }
    )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Profile page."""
    # Calculate user statistics
    total_profiles = db.query(Profile).filter(
        and_(
            Profile.user_id == current_user.id,
            Profile.is_active == True
        )
    ).count()
    
    total_matches = db.query(Match).filter(
        Match.user_id == current_user.id
    ).count()
    
    active_jobs = db.query(Job).filter(
        Job.is_active == True
    ).count()
    
    # Calculate match rate (percentage of profiles that have matches)
    if total_profiles > 0:
        profiles_with_matches = db.query(Profile).filter(
            and_(
                Profile.user_id == current_user.id,
                Profile.is_active == True,
                Profile.id.in_(
                    db.query(Match.profile_id).filter(Match.user_id == current_user.id)
                )
            )
        ).count()
        match_rate = round((profiles_with_matches / total_profiles) * 100, 1)
    else:
        match_rate = 0.0
    
    stats = {
        "total_profiles": total_profiles,
        "total_matches": total_matches,
        "active_jobs": active_jobs,
        "match_rate": match_rate
    }
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request, 
            "user": current_user,
            "stats": stats
        }
    )

@router.get("/404", response_class=HTMLResponse)
async def not_found_page(
    request: Request,
    current_user: User | None = Depends(get_current_user)
) -> Any:
    """404 page."""
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "user": current_user}
    )

@router.get("/api/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    try:
        # Get basic stats
        total_jobs = db.query(Job).filter(Job.is_active == True).count()
        total_profiles = db.query(Profile).filter(Profile.is_active == True).count()
        total_matches = db.query(Match).count()
        avg_score = db.query(func.avg(Match.score)).scalar() or 0
        
        return {
            "totalJobs": total_jobs,
            "totalProfiles": total_profiles,
            "totalMatches": total_matches,
            "averageScore": round(float(avg_score), 2)
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/dashboard/activity")
async def get_dashboard_activity(
    db: Session = Depends(get_db)
):
    """Get matching activity data for charts."""
    try:
        # Get matches from last 7 days
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        matches = db.query(Match).filter(Match.created_at >= week_ago).all()
        
        # Group by date
        activity_data = {}
        for match in matches:
            date_str = match.created_at.strftime('%Y-%m-%d')
            if date_str not in activity_data:
                activity_data[date_str] = 0
            activity_data[date_str] += 1
        
        return {
            "labels": list(activity_data.keys()),
            "data": list(activity_data.values())
        }
    except Exception as e:
        logger.error(f"Error getting dashboard activity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/matches/recent")
async def get_recent_matches(
    db: Session = Depends(get_db)
):
    """Get recent matches for dashboard."""
    try:
        matches = db.query(Match).order_by(desc(Match.created_at)).limit(10).all()
        
        matches_data = []
        for match in matches:
            profile = db.query(Profile).filter(Profile.id == match.profile_id).first()
            job = db.query(Job).filter(Job.id == match.job_id).first()
            
            if profile and job:
                matches_data.append({
                    "id": match.id,
                    "profileName": profile.filename,
                    "jobTitle": job.title,
                    "score": match.score,
                    "status": match.status,
                    "date": match.created_at.isoformat() if match.created_at else None
                })
        
        return {"matches": matches_data}
    except Exception as e:
        logger.error(f"Error getting recent matches: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/skills/top")
async def get_top_skills(
    db: Session = Depends(get_db)
):
    """Get top skills for dashboard."""
    try:
        # Mock data for now - in a real app, this would query actual skills
        skills = [
            {"name": "Python", "count": 15},
            {"name": "JavaScript", "count": 12},
            {"name": "SQL", "count": 10},
            {"name": "React", "count": 8},
            {"name": "Machine Learning", "count": 6}
        ]
        
        return {"skills": skills}
    except Exception as e:
        logger.error(f"Error getting top skills: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/system/status")
async def get_system_status():
    """Get system status for dashboard."""
    try:
        status = {
            "ai": {
                "status": "operational",
                "responseTime": "2.3s",
                "lastUpdated": "2 minutes ago"
            },
            "database": {
                "status": "operational",
                "lastSync": "1 minute ago"
            },
            "api": {
                "status": "operational",
                "uptime": "99.9%"
            }
        }
        
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 