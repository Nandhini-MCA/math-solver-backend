import os
from groq import AsyncGroq
import google.generativeai as genai
import base64

# Setup Groq Client
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = AsyncGroq(api_key=groq_api_key) if groq_api_key else None
GROQ_MODEL = "llama-3.3-70b-versatile"

# Setup Gemini Client
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

async def groq_vision_call(image_path: str, prompt: str) -> str:
    """
    Uses Llama 3.2-Vision on Groq for OCR and solving from images.
    """
    try:
        if not groq_client:
            raise ValueError("Groq API key missing.")

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = await groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq Vision failed: {e}. Reverting to Gemini.")
        raise e

async def _fallback_call(
    system_prompt: str, user_prompt: str, temperature: float = 0.4
) -> str:
    # Attempt 1: Groq
    try:
        if not groq_client:
            raise ValueError("Groq API key is missing.")

        print("Attempting Groq Text generation...")
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as groq_err:
        print(f"Groq API failed: {groq_err}. Falling back to Gemini.")

        # Attempt 2: Gemini Fallback
        try:
            if not gemini_api_key:
                return f"Placeholder response. Both Groq & Gemini keys missing. (Groq Error: {str(groq_err)})"

            model = genai.GenerativeModel("gemini-1.5-pro")
            full_prompt = (
                f"System Instructions: {system_prompt}\n\nUser Question: {user_prompt}"
            )

            response = await model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature),
            )
            return response.text
        except Exception as gemini_err:
            return f"Error: Both AI services failed. Groq error: {str(groq_err)} | Gemini error: {str(gemini_err)}"

async def chat_fallback_call(
    system_prompt: str, messages: list, temperature: float = 0.7
) -> str:
    # Attempt 1: Groq
    try:
        if not groq_client:
            raise ValueError("Groq API key is missing.")

        # Map roles for Groq compatibility (map 'ai' to 'assistant')
        chat_messages = []
        for msg in messages:
            role = "assistant" if msg["role"] == "ai" else msg["role"]
            chat_messages.append({"role": role, "content": msg["content"]})

        payload = [{"role": "system", "content": system_prompt}] + chat_messages
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL, messages=payload, temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as groq_err:
        print(f"Groq Chat failed: {groq_err}. Falling back to Gemini.")

        # Attempt 2: Gemini Fallback (Translate history to Gemini format)
        try:
            if not gemini_api_key:
                return f"Placeholder response. Both keys missing. (Groq Error: {str(groq_err)})"

            model = genai.GenerativeModel(
                "gemini-1.5-pro", system_instruction=system_prompt
            )

            gemini_history = []
            for msg in messages[:-1]:  # Send everything but the last message as history
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=gemini_history)
            last_message = messages[-1]["content"] if messages else ""

            response = await chat.send_message_async(
                last_message,
                generation_config=genai.types.GenerationConfig(temperature=temperature),
            )
            return response.text
        except Exception as gemini_err:
            return f"Error: Chat services failed. Groq error: {str(groq_err)} | Gemini error: {str(gemini_err)}"

async def generate_solution(
    question_text: str, explanation_mode: str = "standard", language: str = "English"
) -> str:
    base_prompt = "You are an Elite AI STEM Copilot Tutor. Your goal is to solve complex physics, chemistry, and math problems with absolute precision and pedagogical brilliance."

mode_instructions = {
        "standard": """FORMAT: Academic Standard
Use headers like "##  Academic Standard"
Show Given: [equation]
Then show each step on a new line with the operation performed
Final answer: [value] with units if any""",

        "eli5": """FORMAT: Explain Like I'm 10
Use headers like "##  Explain Like I'm 10"
Use everyday analogies (like comparing variables to boxes of chocolates)
Use simple words: 'add', 'take away', 'divide up'
Use '👉' arrow emojis for steps
Use '✅' for final answer
Make it fun and easy for a 10 year old to understand""",

        "shortcut": """FORMAT: Shortcuts & Methods
Use headers like "##  Shortcuts & Methods"
Show the direct formula/substitution in one line
Keep it extremely short and simple
Perfect for competitive exams""",

        "concept_first": """FORMAT: Concept-First Deep-Dive
Use headers like "##  Concept-First Deep-Dive"
Start with 'This is a [type of equation]'
Explain what operations mean (* means multiplied, + means added)
Explain inverse operations principle
Then solve step by step""",

        "derivation": """FORMAT: Formula Derivations
Use headers like "##  Formula Derivations"
First derive the general formula for this type of problem
Show each step of derivation
Then apply to this specific problem
End with formula summary"""
    }

    mode_key = explanation_mode
    if mode_key not in mode_instructions:
        mode_key = "standard"
    
    mode_text = mode_instructions[mode_key]

    language_instruction = f"\nCRITICAL LANGUAGE RULE: You MUST write your ENTIRE explanation strictly in {language}. Do not use English unless the user's language is English."

    system_prompt = f"""{base_prompt}

CRITICAL FORMATTING RULES:
1. {mode_text}
2. NEVER use $ symbols for math - use brackets like [x = 5] instead of $x = 5$
3. Use brackets [ ] for all mathematical expressions and equations
4. Use clear section headers starting with ##
5. Write step-by-step clearly
6. Include final answer marked with ✅ or "Final Answer:"{language_instruction}

Solve this STEM question:"""
    return await _fallback_call(system_prompt, question_text, temperature=0.5)

async def detect_language(text: str) -> str:
    """
    Silently detect the user's language, dialect, or transliterated style from any input.
    Returns a short label such as 'English', 'Tanglish', 'Hinglish', 'Tamil', 'Hindi',
    'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Arabic', 'French', 'Spanish', etc.
    Works on even minimal inputs like 'hi' or 'hi nanba'.
    """
    detection_prompt = (
        "Analyze the language or language style of the following text. "
        "The text may be in any language including formal scripts (Tamil, Hindi Devanagari, Arabic, etc.) "
        "or transliterated/romanized versions (Tanglish = Tamil in Roman letters, Hinglish = Hindi in Roman letters, etc.). "
        "Recognize slang, regional words, and informal greetings as strong language markers. "
        "Examples: 'hi nanba' → Tanglish, 'bhai kya hal hai' → Hinglish, 'bonjour' → French. "
        "Return ONLY a single short label (e.g., 'English', 'Tanglish', 'Hinglish', 'Tamil', 'Hindi', "
        "'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Arabic', 'French', 'Spanish'). "
        "If you are not sure, return 'English'. Do not explain anything.\n\n"
        f"Text: {text}"
    )
    try:
        result = await _fallback_call(
            "You are a language detection assistant. Output only the language label, nothing else.",
            detection_prompt,
            temperature=0.0,
        )
        return result.strip().strip(".")
    except Exception:
        return "English"

def _build_multilingual_system_prompt(detected_language: str) -> str:
    """
    Build a multilingual-aware STEM tutor system prompt based on detected language.
    """
    base_rules = (
        "You are a friendly, encouraging STEM AI tutor. "
        "Provide concise, helpful, and accurate explanations in physics, math, and chemistry."
    )

    language_instruction = (
        f"IMPORTANT — LANGUAGE RULE: The user is communicating in '{detected_language}'. "
        "You MUST reply ENTIRELY in that same language and style. "
        "Mirror the user's exact tone, register, and script: "
        "  - If Tanglish (Tamil in Roman letters): reply fully in Tanglish, e.g. 'Seri da, ithu intha mathiri irukku...'. "
        "  - If Hinglish (Hindi in Roman letters): reply in Hinglish, e.g. 'Haan bhai, yeh toh simple hai...'. "
        "  - If formal Tamil/Hindi/Arabic/French/etc. script: reply in that exact script. "
        "  - If English: reply in natural English. "
        "  - If the user is casual, be casual. If formal, be formal. "
        "NEVER respond in English if the detected language is something else. "
        "NEVER mention or explain language detection to the user. Just respond naturally."
    )

    return f"{base_rules}\n\n{language_instruction}"

async def chat_with_tutor(messages: list, detected_language: str = "English") -> str:
    """
    Chat with the AI tutor. If detected_language is provided, the tutor
    will respond entirely in that language/style.
    """
    system_prompt = _build_multilingual_system_prompt(detected_language)
    return await chat_fallback_call(system_prompt, messages, temperature=0.7)
