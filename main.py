
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
    
    # Detect commands
    lower_q = question.lower()
    command = None
    emotion = "neutral"
    
    # Check for special commands
    if any(word in lower_q for word in ["dance", "dancing"]):
        command = "dance"
    elif any(word in lower_q for word in ["sing", "singing", "song"]):
        command = "sing"
    elif any(word in lower_q for word in ["sit", "sitting", "sit down"]):
        command = "sit"
    elif any(word in lower_q for word in ["stand", "standing", "stand up"]):
        command = "stand"
    else:
        # Check if question is too complex or not supported
        complex_keywords = ["create", "make", "build", "code", "program", "develop", "design", "complex"]
        if any(word in lower_q for word in complex_keywords):
            command = "not_supported"
    
    # Detect emotions from question context
    if any(word in lower_q for word in ["angry", "mad", "upset", "frustrated", "annoyed"]):
        emotion = "angry"
    elif any(word in lower_q for word in ["very happy", "extremely happy", "ecstatic", "thrilled", "excited"]):
        emotion = "very_happy"
    elif any(word in lower_q for word in ["happy", "glad", "pleased", "joyful"]):
        emotion = "happy"
    elif any(word in lower_q for word in ["sad", "unhappy", "depressed", "down"]):
        emotion = "sad"
    
    # If command detected, return early
    if command and command != "not_supported":
        return {"answer": "Command executed", "command": command, "emotion": emotion}
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    system_prompt = """You are a friendly AR friend. Always give short, sweet, and concise answers. Keep responses under 2-3 sentences maximum.
    Detect the user's emotion and respond accordingly. If the request is too complex or not supported, indicate that."""
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
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
        
        # Detect emotion from AI response
        answer_lower = answer.lower()
        if any(word in answer_lower for word in ["angry", "mad", "upset"]):
            emotion = "angry"
        elif any(word in answer_lower for word in ["very happy", "extremely happy", "ecstatic", "thrilled"]):
            emotion = "very_happy"
        elif any(word in answer_lower for word in ["happy", "glad", "pleased"]):
            emotion = "happy"
        elif any(word in answer_lower for word in ["sad", "unhappy", "sorry"]):
            emotion = "sad"
        
        # Check if answer indicates not supported
        if "not available" in answer_lower or "will be available soon" in answer_lower or "not supported" in answer_lower:
            command = "not_supported"
            
    except Exception as e:
        answer = "Sorry, I could not connect to AR AI service right now."
    
    return {"answer": answer, "emotion": emotion, "command": command}

