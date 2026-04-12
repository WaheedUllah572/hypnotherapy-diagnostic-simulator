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


# ✅ FINAL FIXED TUTOR REVIEW
@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    try:
        time.sleep(1.5)

        s = req.submission

        q1 = evaluate_response(s.get("chosenApproach", ""))
        q2 = evaluate_response(s.get("clientModality", ""))
        q3 = evaluate_response(s.get("clientObjective", ""))
        q4 = evaluate_response(s.get("clientReassurance", ""))

        # -------- FIXED MODALITY (COUNT-BASED FROM CHAT) --------
        full_chat_text = " ".join([m["text"].lower() for m in req.chatHistory if m["role"] == "client"])

        visual_score = sum(word in full_chat_text for word in ["see", "image", "visual", "picture"])
        auditory_score = sum(word in full_chat_text for word in ["hear", "sound", "auditory", "listen"])
        kinaesthetic_score = sum(word in full_chat_text for word in [
            "feel", "felt", "feeling",
            "tight", "tension", "pressure",
            "chest", "stomach", "body",
            "heavy", "relax", "tense",
            "heart", "breath"
        ])

        modality_label = "Unknown"

        max_score = max(visual_score, auditory_score, kinaesthetic_score)

        if max_score > 0:
            if max_score == kinaesthetic_score:
                modality_label = "Kinaesthetic"
            elif max_score == auditory_score:
                modality_label = "Auditory"
            else:
                modality_label = "Visual"

        # -------- CHAT ANALYSIS --------
        therapist_lines = [
            m["text"].lower()
            for m in req.chatHistory
            if m["role"] == "therapist"
        ]

        empathy_issue = False

        for line in therapist_lines:
            if "just relax" in line or "calm down" in line or "you can relax" in line:
                empathy_issue = True

        # -------- FEEDBACK --------
        feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Clear and appropriate therapeutic model identified." if q1["scores"]["treatment_approach"] else "✘ You need to clearly link the client’s presentation to a recognised therapeutic model (e.g. CBH, Solution-Focused)."}

QUESTION 2 — Client Relaxation Modality
{"✔ Correct identification of modality based on client language." if q2["scores"]["modality"] else "✘ Modality identification needs improvement. Focus on sensory language (visual, auditory, kinaesthetic)."}

QUESTION 3 — Client Objective
{"✔ Client objective clearly defined." if q3["scores"]["objective"] else "✘ The client’s objective is not clearly defined. Summarise what they want to achieve."}

QUESTION 4 — Safety & Reassurance
{"✔ Good awareness of safety, suitability, and reassurance." if q4["scores"]["safety"] else "✘ Safety and suitability are not clearly demonstrated. You must assess risk, screen appropriately, and reassure the client before proceeding."}

CLINICAL INTERACTION OBSERVATIONS
{"⚠ Some responses lacked empathy or were too directive. Focus on validation and open-ended exploration." if empathy_issue else "✔ Your interaction style was appropriate and supportive."}

OVERALL
You are developing strong clinical reasoning. Continue improving structure, empathy, and clarity in your responses.
"""

        # ✅ FIXED SCORING (CORRECT OUT OF 4)
        total = sum([
            1 if q1["scores"]["treatment_approach"] else 0,
            1 if q2["scores"]["modality"] else 0,
            1 if q3["scores"]["objective"] else 0,
            1 if q4["scores"]["safety"] else 0
        ])

        save_session(req.clientName, total)

        return {
            "feedback": feedback.strip(),
            "score": {"total": total},
            "detected_modality": modality_label  # ✅ FIXED
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