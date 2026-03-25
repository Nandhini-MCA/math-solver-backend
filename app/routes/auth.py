from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
import os
import httpx

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

class GoogleLogin(BaseModel):
    token: str

class GoogleCodeRequest(BaseModel):
    code: str
    redirect_uri: str

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password) if user.password else None
    
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        google_id=user.google_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not db_user.password_hash or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google-login", response_model=Token)
def google_login(data: GoogleLogin, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(data.token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo.get("email")
        name = idinfo.get("name")
        google_id = idinfo.get("sub")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        new_user = User(
            name=name,
            email=email,
            password_hash=None,
            google_id=google_id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db_user = new_user
    elif not db_user.google_id:
        db_user.google_id = google_id
        db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/google-callback", response_model=Token)
async def google_callback(data: GoogleCodeRequest, db: Session = Depends(get_db)):
    """
    Receives an authorization code from the frontend after a Google OAuth redirect.
    Exchanges it for tokens server-side using the Client Secret, then logs in or
    creates the user. This bypasses the origin-restricted GIS JavaScript SDK.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured on server")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": data.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": data.redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(status_code=401, detail=f"Google token exchange failed: {token_response.text}")
        token_json = token_response.json()

    # Fetch user profile from Google
    access_token_google = token_json.get("access_token")
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token_google}"}
        )
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Could not fetch user info from Google")
        userinfo = userinfo_response.json()

    email = userinfo.get("email")
    name = userinfo.get("name", email)
    google_id = userinfo.get("id")

    if not email:
        raise HTTPException(status_code=401, detail="No email returned from Google")

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        new_user = User(name=name, email=email, password_hash=None, google_id=google_id)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db_user = new_user
    elif not db_user.google_id:
        db_user.google_id = google_id
        db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": jwt_token, "token_type": "bearer"}
