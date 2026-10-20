import os
from fastapi import FastAPI, Request
from google import genai

app = FastAPI()

# Инициализируем новый клиент с вашим ключом AQ...
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

@app.post("/")
async def handle_alice(request: Request):
    data = await request.json()
    
    user_message = (
        data.get("request", {}).get("command")
        or data.get("request", {}).get("original_utterance")
        or "Привет"
    )
    
    reply_text = "Ой, что-то пошло не так, не могу связаться с нейросетью."
    
    if API_KEY:
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
            )
            reply_text = response.text
        except Exception as e:
            print("DEBUG_ERROR:", repr(e))
            # Если gemini-2.5-flash еще не доступен в регионе, пробуем gemini-2.0-flash
            try:
                client = genai.Client(api_key=API_KEY)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_message,
                )
                reply_text = response.text
            except Exception as e2:
                print("DEBUG_ERROR_2:", repr(e2))
                reply_text = f"Ошибка Gemini: {str(e2)}"

    return {
        "response": {
            "text": reply_text,
            "tts": reply_text,
            "end_session": False
        },
        "version": "1.0"
    }
