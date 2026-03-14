from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Question, Solution
from app.dependencies import get_current_user

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/")
def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.user_id == current_user.id).order_by(Question.created_at.desc()).all()
    history_data = []
    for q in questions:
        sol = db.query(Solution).filter(Solution.question_id == q.id).first()
        history_data.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "solution_text": sol.solution_text if sol else None,
            "created_at": q.created_at
        })
        
    return {"history": history_data}
