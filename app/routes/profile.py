from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import UserResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/", response_model=UserResponse)
def read_profile(current_user: User = Depends(get_current_user)):
    return current_user
