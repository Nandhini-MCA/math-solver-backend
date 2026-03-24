import urllib.parse

def render_graphviz(dot_string: str) -> str:
    """
    Renders DOT syntax using QuickChart API (Removes local Graphviz dependency).
    """
    try:
        # Clean up the dot string for URL encoding
        clean_dot = dot_string.strip()
        encoded_dot = urllib.parse.quote(clean_dot)
        
        # We return the direct QuickChart link as the image URL
        # This link works immediately in an <img> tag on the frontend
        return f"https://quickchart.io/graphviz?format=png&graph={encoded_dot}"
        
    except Exception as e:
        return f"Error formatting diagram: {str(e)}"

