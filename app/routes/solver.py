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
    from app.services.ai_service import detect_language
    
    # Resolve language
    final_lang = req.language
    if not final_lang or final_lang == "Auto-Detect (Smart)":
        final_lang = await detect_language(req.text)
    else:
        lang_map = {"en": "English", "ta": "Tamil", "hi": "Hindi"}
        final_lang = lang_map.get(final_lang, final_lang)
        
    solution_text = await generate_solution(req.text, req.explanation_mode, final_lang)
    
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
        "solution_text": solution.solution_text,
        "detected_language": final_lang
    }

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    try:
        extracted_text = await extract_text_from_image(file_location)
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=f"Could not read image: {str(e)}")
    
    if not extracted_text or len(extracted_text.strip()) < 5:
        raise HTTPException(status_code=422, detail="No readable text or math found in the image. Please upload a clearer image.")
    
    return {"extracted_text": extracted_text, "filename": file.filename}

