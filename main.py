import os
from fastapi import FastAPI, Request
from google import genai

app = FastAPI()

API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Инициализируем клиент при старте
client = genai.Client(api_key=API_KEY) if API_KEY else None

@app.post("/")
async def handle_alice(request: Request):
    data = await request.json()
    
    user_message = (
        data.get("request", {}).get("command")
        or data.get("request", {}).get("original_utterance")
        or "Привет"
    )
    
    reply_text = "Ой, не удалось получить ответ от нейросети."
    
    if client:
        try:
            # Запрашиваем именно актуальную модель gemini-3.8-flash
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_message,
            )
            reply_text = response.text
        except Exception as e:
            print("DEBUG_ERROR:", repr(e))
            reply_text = f"Ошибка Gemini: {str(e)}"

    return {
        "response": {
            "text": reply_text,
            "tts": reply_text,
            "end_session": False
        },
        "version": "1.0"
    }
