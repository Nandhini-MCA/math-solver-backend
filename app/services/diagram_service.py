import graphviz
import uuid
import os

DIAGRAMS_DIR = "diagrams"
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

def render_graphviz(dot_string: str) -> str:
    # Safely renders a DOT string into a PNG image and returns the local path
    filename = str(uuid.uuid4())
    filepath = os.path.join(DIAGRAMS_DIR, filename)
    
    try:
        src = graphviz.Source(dot_string)
        src.render(filepath, format='png', cleanup=True)
        return f"/diagrams/{filename}.png"
    except graphviz.ExecutableNotFound:
        return "Error: Graphviz executable not found on host."
    except Exception as e:
        return f"Error generating diagram: {str(e)}"
