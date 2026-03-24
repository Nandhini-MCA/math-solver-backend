import google.generativeai as genai
import os
from PIL import Image
from app.services.ai_service import groq_vision_call

async def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text/math from image using Groq Llama 3.2 Vision (Primary)
    with Gemini Vision fallback.
    """
    prompt = (
        "You are an expert OCR system for STEM. "
        "Extract all text, equations, and mathematical formulas from this image. "
        "Format the output as clean text, maintaining the logical structure and using LaTeX for complex math."
    )

    # Attempt 1: Groq Vision
    try:
        print(f"Attempting Groq Vision OCR for: {file_path}")
        return await groq_vision_call(file_path, prompt)
    except Exception as e:
        print(f"Groq Vision OCR failed: {e}. Falling back to Gemini Vision.")
        
        # Attempt 2: Gemini Vision (Fallback)
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return "Error: Both Groq & Gemini keys missing."
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Using Image.open from PIL (loaded globally)
            img = Image.open(file_path)
            # generate_content is synchronous normally, but genai supports async too if we specify
            response = await model.generate_content_async([prompt, img])
            return response.text.strip()
        except Exception as gemini_err:
            return f"Error: All Vision services failed. ({str(gemini_err)})"
