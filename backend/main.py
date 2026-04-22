from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import random
import time
from dotenv import load_dotenv

load_dotenv()

from services.session_tracker import save_session, get_sessions
from services.progress_engine import calculate_progress
from services.persona_engine import get_persona_response
from services.conversation_engine import get_stage, detect_stage_from_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

risk_sessions = {}


class Message(BaseModel):
    text: str
    clientType: str
    history: list = []


class TutorRequest(BaseModel):
    submission: dict
    chatHistory: list
    clientName: str


@app.post("/chat")
async def chat(msg: Message):

    session_id = msg.clientType + "_session"

    if session_id not in risk_sessions:
        risk_sessions[session_id] = (random.randint(1, 15) == 3)

    stage = detect_stage_from_question(msg.text) or get_stage(session_id)
    persona_reply = get_persona_response(msg.clientType, stage, risk_sessions[session_id])

    messages = [{"role": "system", "content": f"Stage: {stage}\n{persona_reply}"}]

    for m in msg.history:
        if m["role"] == "therapist":
            messages.append({"role": "user", "content": m["text"]})
        elif m["role"] == "client":
            messages.append({"role": "assistant", "content": m["text"]})

    messages.append({"role": "user", "content": msg.text})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            timeout=10
        )
        reply = response.choices[0].message.content
    except Exception:
        reply = "I'm not sure how to explain that… could you ask me in a different way?"

    return {"reply": reply, "safety_flag": False, "stage": stage}


# ✅ Q4 STRUCTURED CHECK
def evaluate_q4(text):
    t = text.lower()
    return {
        "safety": any(x in t for x in ["risk", "medical", "history", "screen"]),
        "reassurance": any(x in t for x in ["reassure", "safe", "comfortable"]),
        "readiness": any(x in t for x in ["ready", "proceed", "continue"])
    }


@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    s = req.submission

    q1 = "cbt" in s.get("chosenApproach", "").lower()
    q2 = any(x in s.get("clientModality", "").lower() for x in ["visual", "auditory", "kinaesthetic"])
    q3 = "goal" in s.get("clientObjective", "").lower()

    q4_data = evaluate_q4(s.get("clientReassurance", ""))
    q4 = all(q4_data.values())

    # ✅ FINAL STRUCTURED FEEDBACK
    feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Appropriate model selected." if q1 else "✘ The correct approach would be a Cognitive Behavioural approach based on the client’s thought patterns."}

QUESTION 2 — Client Modality
{"✔ Modality correctly identified." if q2 else "✘ The client’s language suggests a kinaesthetic modality (focus on feelings and body sensations)."}

QUESTION 3 — Client Objective
{"✔ Objective clearly defined." if q3 else "✘ The objective should clearly state what the client wants to change or achieve."}

QUESTION 4 — Safety & Reassurance
{"✔ All components addressed." if q4 else f"""
• Safety: {"✔" if q4_data["safety"] else "✘"}
• Reassurance: {"✔" if q4_data["reassurance"] else "✘"}
• Readiness: {"✔" if q4_data["readiness"] else "✘"}
"""}
"""

    total = sum([q1, q2, q3, q4])
    save_session(req.clientName, total)

    return {
        "feedback": feedback.strip(),
        "score": {"total": total},
        "detected_modality": "Kinaesthetic"
    }