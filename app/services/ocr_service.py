import os
import google.generativeai as genai
from PIL import Image

OCR_PROMPT = (
    "You are an expert OCR system for STEM education. "
    "Look at this image carefully and extract ALL text, equations, and mathematical formulas. "
    "If it is a math/physics/chemistry problem, extract the full question. "
    "Format the output as clean readable text. Use LaTeX notation for equations (e.g., $x^2 + y^2 = z^2$). "
    "Return ONLY the extracted text/question — do not solve it, do not add commentary."
)


async def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text/math from an image.
    Primary:  Groq Llama 3.2 Vision (llama-3.2-11b-vision-preview)
    Fallback: Gemini 1.5 Flash Vision
    """
    groq_error_msg = "not attempted"
    gemini_error_msg = "not attempted"

    # ── Attempt 1: Groq Llama 4 Scout Vision (Primary) ───────────────────────
    try:
        from app.services.ai_service import groq_vision_call

        result = await groq_vision_call(file_path, OCR_PROMPT)
        if result and len(result.strip()) > 3:
            print(f"Groq Vision OCR success for: {file_path}")
            return result.strip()
        raise ValueError("Groq returned empty response")

    except Exception as e:
        groq_error_msg = str(e)
        print(f"Groq Vision OCR failed: {e}. Trying Gemini Vision...")

    # ── Attempt 2: Gemini Vision (Fallback) ───────────────────────────────────
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        img = Image.open(file_path)
        response = await model.generate_content_async([OCR_PROMPT, img])
        result = response.text.strip()
        if result and len(result) > 3:
            print(f"Gemini Vision OCR success for: {file_path}")
            return result
        raise ValueError("Gemini returned empty response")

    except Exception as e:
        gemini_error_msg = str(e)
        print(f"Gemini Vision OCR also failed: {e}")

    raise RuntimeError(
        "Unable to read the image. Please try uploading a clearer image with visible text or equations. If the problem persists, try a different image or use text input instead."
    )
