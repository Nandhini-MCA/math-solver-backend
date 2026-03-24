import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Question, Solution
from app.schemas import QuestionRequest, QuestionResponse
from app.dependencies import get_current_user
from app.services.ai_service import generate_solution
from app.services.ocr_service import extract_text_from_image

router = APIRouter(prefix="/solver", tags=["solver"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/solve", response_model=QuestionResponse)
async def solve_question(req: QuestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    solution_text = await generate_solution(req.text)
    
    # Save to db
    question = Question(user_id=current_user.id, question_text=req.text)
    db.add(question)
    db.commit()
    db.refresh(question)
    
    solution = Solution(question_id=question.id, solution_text=solution_text)
    db.add(solution)
    db.commit()
    db.refresh(solution)
    
    return {
        "id": question.id,
        "question_text": question.question_text,
        "solution_text": solution.solution_text
    }

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    extracted_text = await extract_text_from_image(file_location)
    return {"extracted_text": extracted_text, "filename": file.filename}

