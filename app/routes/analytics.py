from fastapi import APIRouter, Depends
from app.models import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/report")
async def get_analytics_report(current_user: User = Depends(get_current_user)):
    # Return dummy analytics for the frontend dashboard
    return {
        "level": 5,
        "total_xp": 1250,
        "streak_count": 7,
        "subject_mastery": {
            "Mathematics": 85,
            "Physics": 72,
            "Chemistry": 64,
            "Biology": 91
        },
        "weak_topics": ["Quantum Mechanics", "Organic Chemistry", "Calculus III"],
        "weekly_progress": [40, 60, 30, 80, 50, 90, 70]
    }
