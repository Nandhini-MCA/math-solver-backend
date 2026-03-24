import os
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not found in .env")
        return
        
    client = AsyncGroq(api_key=api_key)
    try:
        print("Testing Groq...")
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Explain 1+1 briefly",
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        print("Response:", chat_completion.choices[0].message.content)
    except Exception as e:
        print("Groq Error:", e)

if __name__ == "__main__":
    asyncio.run(test_groq())
