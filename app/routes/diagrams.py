from fastapi import APIRouter, Depends
from app.database import get_db
from app.models import User
from app.schemas import DiagramRequest, DiagramResponse
from app.dependencies import get_current_user
from app.services.ai_service import _fallback_call
from app.services.diagram_service import render_graphviz
import os

router = APIRouter(prefix="/diagrams", tags=["diagrams"])

@router.post("/generate", response_model=DiagramResponse)
async def generate_diagram(req: DiagramRequest, current_user: User = Depends(get_current_user)):
    system_prompt = "You are a graphviz DOT generator. Given a scenario, output ONLY valid Graphviz DOT language syntax, without markdown formatting, entirely ready to be passed to Graphviz render system."
    dot_string = await _fallback_call(system_prompt, req.description, temperature=0.3)
    if dot_string.startswith("```"):
        # Strip markdown syntax
        parts = dot_string.split("\n", 1)
        if len(parts) > 1:
            dot_string = parts[1]
        dot_string = dot_string.rsplit("```", 1)[0].strip()

    image_url = render_graphviz(dot_string)
    
    return {"image_url": image_url}
