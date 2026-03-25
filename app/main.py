from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from fastapi.staticfiles import StaticFiles
from app.routes import auth, profile, solver, diagrams, chat, history, analytics
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI STEM Copilot API")

# Ensure diagrams directory exists and mount it
os.makedirs("diagrams", exist_ok=True)
app.mount("/diagram_images", StaticFiles(directory="diagrams"), name="diagram_images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://math-solverai.netlify.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(solver.router)
app.include_router(diagrams.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(analytics.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to AI STEM Copilot API"}
