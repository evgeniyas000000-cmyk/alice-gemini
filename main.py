import os 
from fastapi import FastAPI, Request 
import google.generativeai as genai
app = FastAPI()
# Получаем ключ из переменных окружения
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
# Настраиваем клиент библиотеки
if API_KEY: genai.configure(api_key=API_KEY)
@app.post("/") async def handle_alice(request: Request): data = await request.json()
# Извлекаем текст от пользователя
user_message = (
    data.get("request", {}).get("command")
    or data.get("request", {}).get("original_utterance")
    or "Привет"
)

try:
    # Используем проверенный вызов GenerativeModel
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(user_message)
    reply_text = response.text
except Exception as e:
    print("DEBUG_ERROR:", repr(e))
    reply_text = "Ой, что-то пошло не так, не могу связаться с нейросетью."
    
return {
    "response": {
        "text": reply_text,
        "tts": reply_text,
        "end_session": False
    },
    "version": "1.0"
}
