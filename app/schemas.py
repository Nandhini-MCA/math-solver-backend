from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: Optional[str] = None
    google_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionRequest(BaseModel):
    text: str
    explanation_mode: Optional[str] = "standard"
    language: Optional[str] = None

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    solution_text: str
    detected_language: Optional[str] = None

    class Config:
        from_attributes = True

class DiagramRequest(BaseModel):
    description: str

class DiagramResponse(BaseModel):
    image_url: str

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    role: str
    message: str
    timestamp: datetime
    detected_language: Optional[str] = None

    class Config:
        from_attributes = True
