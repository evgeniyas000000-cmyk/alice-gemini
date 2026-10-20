import os
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/")
async def handle_alice(request: Request):
    data = await request.json()

    user_message = (
        data.get("request", {}).get("command")
        or data.get("request", {}).get("original_utterance")
        or "Привет"
    )

    # Тестовый ответ для проверки связи с Яндексом
    reply_text = f"Я услышала тебя: «{user_message}». Связь с сервером есть!"

    return {
        "response": {
            "text": reply_text,
            "tts": reply_text,
            "end_session": False,
        },
        "version": "1.0",
    }
