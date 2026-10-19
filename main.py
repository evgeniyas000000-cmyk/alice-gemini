import os
from fastapi import FastAPI, Request
from google import genai
from google.genai import types

app = FastAPI()

# Получаем ключ Gemini из переменных окружения
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)


@app.post("/")
async def handle_alice(request: Request):
  data = await request.json()

  # Достаем текст, который сказала Алиса/пользователь
  user_message = (
      data.get("request", {}).get("command")
      or data.get("request", {}).get("original_utterance")
      or "Привет"
  )

  # Формируем запрос к Gemini (используем быструю и бесплатную модель gemini-2.5-flash)
  try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Ты — голосовой помощник Алиса. Отвечай кратко, вежливо и"
                " естественно, чтобы ответ было удобно слушать вслух."
            )
        ),
    )
    reply_text = response.text
  except Exception as e:
    reply_text = "Ой, что-то пошло не так, не могу связаться с нейросетью."

  # Возвращаем ответ в специальном формате, который понимает Яндекс Алиса
  return {
      "response": {
          "text": reply_text,
          "tts": reply_text,
          "end_session": False,
      },
      "version": "1.0",
  }
