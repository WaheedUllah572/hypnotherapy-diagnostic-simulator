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
from services.conversation_engine import get_stage, advance_stage, detect_stage_from_question
from services.scoring_engine import evaluate_response

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


class TutorRequest(BaseModel):
    submission: dict
    chatHistory: list
    clientName: str


@app.post("/chat")
async def chat(msg: Message):

    text = msg.text.strip().lower()

    if "test safety" in text:
        return {
            "reply": "I've been feeling really overwhelmed lately… sometimes I feel like I just want everything to stop.",
            "safety_flag": False
        }

    if "test end" in text:
        return {
            "reply": "Safety threshold reached. Pre-induction cannot continue.",
            "safety_flag": True
        }

    session_id = msg.clientType + "_session"

    if session_id not in risk_sessions:
        risk_sessions[session_id] = (random.randint(1, 15) == 3)

    risk_mode = risk_sessions[session_id]

    stage = detect_stage_from_question(msg.text) or get_stage(session_id)

    persona_reply = get_persona_response(msg.clientType, stage, risk_mode)

    system = f"""
You are role-playing as a therapy client.

Keep answers short (1–3 sentences).
Be natural and realistic.

Stage: {stage}

{persona_reply}
"""

    messages = [{"role": "system", "content": system}]

    for m in msg.history:
        if m["role"] == "therapist":
            messages.append({"role": "user", "content": m["text"]})
        elif m["role"] == "client":
            messages.append({"role": "assistant", "content": m["text"]})

    messages.append({"role": "user", "content": msg.text})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
    except Exception as e:
        print("ERROR:", e)
        return {"reply": "System error", "safety_flag": False}

    return {
        "reply": response.choices[0].message.content,
        "safety_flag": False,
        "stage": stage
    }


# ✅ FIXED TUTOR REVIEW (PER QUESTION EVALUATION)
@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    try:
        time.sleep(1.5)

        s = req.submission

        # ✅ Evaluate EACH QUESTION separately
        q1 = evaluate_response(s.get("chosenApproach", ""))
        q2 = evaluate_response(s.get("clientModality", ""))
        q3 = evaluate_response(s.get("clientObjective", ""))
        q4 = evaluate_response(s.get("clientReassurance", ""))

        # ✅ Build structured feedback
        feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Good alignment with a therapeutic model." if q1["scores"]["treatment_approach"] else "✘ Needs clearer link to a recognised therapeutic approach (e.g. CBH, Solution-Focused)."}

QUESTION 2 — Client Relaxation Modality
{"✔ Correctly identified client modality." if q2["scores"]["modality"] else "✘ Modality identification needs improvement. Look for visual, auditory, kinaesthetic cues."}

QUESTION 3 — Client Objective
{"✔ Clear understanding of client goal." if q3["scores"]["objective"] else "✘ Client objective not clearly defined. Summarise what the client wants."}

QUESTION 4 — Safety & Reassurance
{"✔ Demonstrates awareness of safety and reassurance." if q4["scores"]["safety"] else "✘ Safety and reassurance not clearly addressed. Must assess suitability and reassure client."}

OVERALL COMMENTS
You are developing good clinical reasoning. Focus on clarity, structure, and linking responses directly to clinical models.
"""

        total = (
            q1["total"] +
            q2["total"] +
            q3["total"] +
            q4["total"]
        ) // 4  # keep score out of 4

        save_session(req.clientName, total)

        return {
            "feedback": feedback.strip(),
            "score": {"total": total},
            "detected_modality": q2["modality_label"]
        }

    except Exception as e:
        print("TUTOR ERROR:", e)
        return {
            "feedback": "Tutor feedback unavailable.",
            "score": {"total": 0},
            "detected_modality": None
        }


@app.get("/progress")
async def get_progress():

    try:
        sessions = get_sessions()
        return calculate_progress(sessions)

    except Exception as e:
        print("PROGRESS ERROR:", e)
        return {
            "sessionsCompleted": 0,
            "averageScore": 0,
            "personasCompleted": []
        }