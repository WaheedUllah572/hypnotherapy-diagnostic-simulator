from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import random
from dotenv import load_dotenv

load_dotenv()

from services.session_tracker import save_session, get_sessions
from services.progress_engine import calculate_progress
from services.persona_engine import get_persona_response
from services.conversation_engine import get_stage, advance_stage, detect_stage_from_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

risk_sessions = {}


class Message(BaseModel):
    text: str
    clientType: str
    history: list = []


@app.post("/chat")
async def chat(msg: Message):

    # ✅ TEST MODE
    text = msg.text.strip().lower()

    if "test safety" in text:
        return {
            "reply": "I've been feeling really overwhelmed lately… sometimes I feel like I just want everything to stop.",
            "safety_flag": False
        }

    if "test end" in text:
        return {
            "reply": "Safety threshold reached. Pre-induction cannot continue. Please refer this client to appropriate support services.",
            "safety_flag": True
        }

    # Student safety keywords
    safety_keywords = [
        "kill myself", "end my life", "suicide", "self harm",
        "i want to die", "i don't want to live"
    ]

    if any(k in text for k in safety_keywords):
        return {
            "reply": "Safety threshold reached. Pre-induction cannot continue. Please refer this client to appropriate support services.",
            "safety_flag": True
        }

    session_id = msg.clientType + "_session"

    if session_id not in risk_sessions:
        risk_sessions[session_id] = (random.randint(1, 15) == 3)

    risk_mode = risk_sessions[session_id]

    detected_stage = detect_stage_from_question(msg.text)

    if detected_stage:
        stage = detected_stage
    else:
        stage = get_stage(session_id)

    persona_reply = get_persona_response(msg.clientType, stage, risk_mode)

    system = f"""
You are role-playing as a therapy client in a pre-hypnosis assessment session.

IMPORTANT RULES:
• Respond naturally to the therapist.
• Keep answers 1–3 sentences.
• Reveal information gradually.

Current session stage: {stage}

Client information:
{persona_reply}
"""

    messages = [{"role": "system", "content": system}]

    for m in msg.history:
        if m["role"] == "therapist":
            messages.append({"role": "user", "content": m["text"]})
        elif m["role"] == "client":
            messages.append({"role": "assistant", "content": m["text"]})

    messages.append({"role": "user", "content": msg.text})

    # ✅ Safe OpenAI call
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
    except Exception as e:
        print("❌ OPENAI ERROR:", e)
        return {
            "reply": "System temporarily unavailable.",
            "safety_flag": False
        }

    reply_content = response.choices[0].message.content
    reply_text = reply_content.lower()

    # ✅ FINAL RISK DETECTION (KEYWORDS ONLY)
    risk_words = [
        "hurt myself", "kill myself", "end my life", "suicide",
        "want to die", "don't want to live", "giving up",
        "can't go on", "no point", "feel trapped", "want to escape",
        "escape from everything", "wish i could disappear",
        "everything to stop", "too much to handle",
        "i can't cope", "i can't handle this anymore",
        "i want to get away", "i want to disappear"
    ]

    if any(word in reply_text for word in risk_words):
        return {
            "reply": reply_content,
            "safety_flag": True
        }

    if detected_stage:
        advance_stage(session_id)

    return {
        "reply": reply_content,
        "safety_flag": False,
        "stage": stage
    }