from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, profile, solver, diagrams, chat, history

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI STEM Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://math-solverai.netlify.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
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

@app.get("/")
def read_root():
    return {"message": "Welcome to AI STEM Copilot API"}
