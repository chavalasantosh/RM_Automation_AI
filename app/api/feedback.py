from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter()

class FeedbackBase(BaseModel):
    type: str
    content: str
    email: Optional[EmailStr] = None
    page: str
    timestamp: datetime

class HelpFeedback(BaseModel):
    section: str
    helpful: bool
    timestamp: datetime

# Ensure feedback directory exists
FEEDBACK_DIR = Path("data/feedback")
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackBase):
    try:
        # Create feedback file with timestamp
        timestamp = feedback.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_{timestamp}.json"
        filepath = FEEDBACK_DIR / filename
        
        # Save feedback to file
        with open(filepath, "w") as f:
            json.dump(feedback.dict(), f, indent=2, default=str)
        
        return {"status": "success", "message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/help-feedback")
async def submit_help_feedback(feedback: HelpFeedback):
    try:
        # Create help feedback file
        timestamp = feedback.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"help_feedback_{timestamp}.json"
        filepath = FEEDBACK_DIR / filename
        
        # Save feedback to file
        with open(filepath, "w") as f:
            json.dump(feedback.dict(), f, indent=2, default=str)
        
        return {"status": "success", "message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/stats")
async def get_feedback_stats():
    try:
        feedback_files = list(FEEDBACK_DIR.glob("feedback_*.json"))
        help_feedback_files = list(FEEDBACK_DIR.glob("help_feedback_*.json"))
        
        stats = {
            "total_feedback": len(feedback_files),
            "total_help_feedback": len(help_feedback_files),
            "feedback_types": {},
            "help_feedback": {
                "helpful": 0,
                "not_helpful": 0
            }
        }
        
        # Process general feedback
        for file in feedback_files:
            with open(file, "r") as f:
                data = json.load(f)
                feedback_type = data.get("type", "unknown")
                stats["feedback_types"][feedback_type] = stats["feedback_types"].get(feedback_type, 0) + 1
        
        # Process help feedback
        for file in help_feedback_files:
            with open(file, "r") as f:
                data = json.load(f)
                if data.get("helpful"):
                    stats["help_feedback"]["helpful"] += 1
                else:
                    stats["help_feedback"]["not_helpful"] += 1
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 