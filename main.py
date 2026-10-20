import os
import asyncio
import httpx
from fastapi import FastAPI, Request

app = FastAPI()

API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

@app.post("/")
async def handle_alice(request: Request):
    data = await request.json()

    user_message = (
        data.get("request", {}).get("command")
        or data.get("request", {}).get("original_utterance")
        or "Привет"
    )

    reply_text = "Извините, нейросеть задумалась. Попробуйте ещё раз."

    if API_KEY:
        try:
            # Делаем быстрый прямой HTTP-запрос к API Gemini (без тяжелого SDK, который тормозит на Render)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": user_message}]}]
            }
            
            async with httpx.AsyncClient() as client:
                # Ограничиваем сетевой запрос строгими 3 секундами
                response = await asyncio.wait_for(
                    client.post(url, json=payload, timeout=3.0),
                    timeout=3.5
                )
                
                if response.status_code == 200:
                    res_data = response.json()
                    reply_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    print(f"API Error [{response.status_code}]: {response.text}")
                    reply_text = f"Ошибка API: {response.status_code}"
                    
        except asyncio.TimeoutError:
            print("DEBUG_TIMEOUT: Прямой HTTP-запрос превысил 3.5 секунды")
            reply_text = "Я здесь, но сервер ответил слишком медленно!"
        except Exception as e:
            print("DEBUG_ERROR:", repr(e))
            reply_text = "Что-то пошло не так при обращении к сети."

    return {
        "response": {
            "text": reply_text,
            "tts": reply_text,
            "end_session": False,
        },
        "version": "1.0",
    }
