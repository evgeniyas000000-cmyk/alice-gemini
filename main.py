import os
import asyncio
from fastapi import FastAPI, Request
from google import genai

app = FastAPI()

API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Инициализируем клиент
client = genai.Client(api_key=API_KEY) if API_KEY else None


def fetch_gemini_response(user_message: str) -> str:
    """Синхронный вызов Gemini API"""
    if not client:
        return "Ошибка: API ключ не задан."
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_message,
    )
    return response.text


@app.post("/")
async def handle_alice(request: Request):
    data = await request.json()

    user_message = (
        data.get("request", {}).get("command")
        or data.get("request", {}).get("original_utterance")
        or "Привет"
    )

    reply_text = "Извините, нейросеть задумалась. Попробуйте ещё раз."

    if client:
        try:
            # Запускаем вызов Gemini в отдельном потоке с лимитом времени 3.5 секунды,
            # чтобы гарантированно уложиться в 5-секундный тайм-аут Яндекса
            reply_text = await asyncio.wait_for(
                asyncio.to_thread(fetch_gemini_response, user_message),
                timeout=3.5,
            )
        except asyncio.TimeoutError:
            print("DEBUG_TIMEOUT: Запрос к Gemini превысил 3.5 секунды")
            reply_text = "Я засмотрелась на звезды и не успела ответить. Спроси еще раз!"
        except Exception as e:
            print("DEBUG_ERROR:", repr(e))
            reply_text = f"Ошибка: {str(e)}"

    return {
        "response": {
            "text": reply_text,
            "tts": reply_text,
            "end_session": False,
        },
        "version": "1.0",
    }
