from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = "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"
MODEL = "google/gemini-2.0-flash-exp:free"

@app.post("/ask")
async def ask_ai(request: Request):
    body = await request.json()
    question = body.get("question", "")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a friendly AR friend who answers with clear, short, helpful responses."},
            {"role": "user", "content": question}
        ]
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        data = r.json()
        answer = data["choices"][0]["message"]["content"]
    except Exception as e:
        answer = "Sorry, I could not connect to AR AI service right now."
    return {"answer": answer}
