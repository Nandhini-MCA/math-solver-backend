import os
from groq import AsyncGroq
import google.generativeai as genai

# Setup Groq Client
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = AsyncGroq(api_key=groq_api_key) if groq_api_key else None
GROQ_MODEL = "llama-3.3-70b-versatile"

# Setup Gemini Client
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

async def _fallback_call(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    # Attempt 1: Groq
    try:
        if not groq_client:
            raise ValueError("Groq API key is missing.")
            
        print("Attempting Groq generation...")
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as groq_err:
        print(f"Groq API failed: {groq_err}. Falling back to Gemini.")
        
        # Attempt 2: Gemini Fallback
        try:
            if not gemini_api_key:
                return f"Placeholder response. Both Groq & Gemini keys missing. (Groq Error: {str(groq_err)})"
                
            model = genai.GenerativeModel("gemini-1.5-pro")
            full_prompt = f"System Instructions: {system_prompt}\n\nUser Question: {user_prompt}"
            
            # genai currently defaults to sync generate_content, but we can utilize async methods if supported
            response = await model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            return response.text
        except Exception as gemini_err:
            return f"Error: Both AI services failed. Groq error: {str(groq_err)} | Gemini error: {str(gemini_err)}"

async def chat_fallback_call(system_prompt: str, messages: list, temperature: float = 0.7) -> str:
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
            model=GROQ_MODEL,
            messages=payload,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as groq_err:
        print(f"Groq Chat failed: {groq_err}. Falling back to Gemini.")
        
        # Attempt 2: Gemini Fallback (Translate history to Gemini format)
        try:
            if not gemini_api_key:
                return f"Placeholder response. Both keys missing. (Groq Error: {str(groq_err)})"
            
            model = genai.GenerativeModel(
                "gemini-1.5-pro",
                system_instruction=system_prompt
            )
            
            gemini_history = []
            for msg in messages[:-1]: # Send everything but the last message as history
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
                
            chat = model.start_chat(history=gemini_history)
            last_message = messages[-1]["content"] if messages else ""
            
            response = await chat.send_message_async(
                last_message,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            return response.text
        except Exception as gemini_err:
            return f"Error: Chat services failed. Groq error: {str(groq_err)} | Gemini error: {str(gemini_err)}"

async def generate_solution(question_text: str) -> str:
    system_prompt = "You are an expert AI STEM Copilot tutor. Provide a step-by-step solution to the user's question, ending with a clear final answer."
    return await _fallback_call(system_prompt, question_text, temperature=0.4)

async def chat_with_tutor(messages: list) -> str:
    system_prompt = "You are a friendly, encouraging STEM AI tutor interacting via a chat interface. Provide concise and helpful explanations."
    return await chat_fallback_call(system_prompt, messages, temperature=0.7)
