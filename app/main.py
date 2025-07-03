from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn
from app.api import feedback
from app.routes import web, auth
from app.database import engine, Base, init_db
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RME Enterprise AI Platform",
    description="Resume Matching Engine for Enterprise",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(web.router)  # Include the web router which has the upload endpoint
app.include_router(auth.router)

# Create upload directories
UPLOAD_DIR = Path("uploads")
RESUMES_DIR = UPLOAD_DIR / "resumes"
JOBS_DIR = UPLOAD_DIR / "jobs"
MATCHES_DIR = UPLOAD_DIR / "matches"

for directory in [UPLOAD_DIR, RESUMES_DIR, JOBS_DIR, MATCHES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "RME Server is running"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True) 