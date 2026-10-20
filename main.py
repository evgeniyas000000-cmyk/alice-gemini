import os
import json
import urllib.request
import urllib.error
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

@app.post("/")
async def handle_alice(request: Request):
    data = await request.json()
    
    user_message = (
        data.get("request", {}).get("command")
        or data.get("request", {}).get("original_utterance")
        or "Привет"
    )
    
    reply_text = "Ой, что-то пошло не так, не могу связаться с нейросетью."
    
    if TOKEN:
        payload = {
            "contents": [{
                "parts": [{"text": user_message}]
            }]
        }
        req_data = json.dumps(payload).encode("utf-8")
        
        # Вариант 1: Запрос с авторизацией Bearer (для токенов AQ...)
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            req = urllib.request.Request(
                url, 
                data=req_data, 
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {TOKEN}"
                }, 
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                reply_text = res_body["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e1:
            print("DEBUG_BEARER_ERROR:", repr(e1))
            
            # Вариант 2: Передача токена через URL-параметр ?key=
            try:
                url_key = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={TOKEN}"
                req_key = urllib.request.Request(
                    url_key, 
                    data=req_data, 
                    headers={"Content-Type": "application/json"}, 
                    method="POST"
                )
                with urllib.request.urlopen(req_key) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    reply_text = res_body["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e2:
                print("DEBUG_KEY_ERROR:", repr(e2))
                reply_text = f"Ошибка Gemini: {str(e2)}"

    return {
        "response": {
            "text": reply_text,
            "tts": reply_text,
            "end_session": False
        },
        "version": "1.0"
    }
