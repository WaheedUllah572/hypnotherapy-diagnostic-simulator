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


# ✅ TUTOR REVIEW (FIXED + IMPROVED)
# ✅ TUTOR REVIEW (ENHANCED — CONTEXT AWARE, SAFE)
@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    try:
        time.sleep(1.5)  # simulate thinking

        combined_text = " ".join(req.submission.values())
        result = evaluate_response(combined_text)

        # ✅ NEW: ANALYSE CHAT HISTORY FOR CLINICAL QUALITY
        therapist_lines = [
            m["text"].lower()
            for m in req.chatHistory
            if m["role"] == "therapist"
        ]

        empathy_issues = []
        risk_missed = False

        for line in therapist_lines:
            if "just relax" in line or "calm down" in line:
                empathy_issues.append(
                    "At one point you used a phrase such as 'just relax', which may feel dismissive to the client’s experience."
                )

            if "escape" in line or "disappear" in line:
                risk_missed = True

        # ✅ BUILD HUMAN-LIKE FEEDBACK
        feedback_parts = []

        feedback_parts.append(
            "You demonstrated a thoughtful attempt at analysing the client’s presentation."
        )

        # Treatment
        if result["scores"]["treatment_approach"]:
            feedback_parts.append(
                "You clearly linked the client's issues to an appropriate therapeutic model."
            )
        else:
            feedback_parts.append(
                "Your treatment approach could be strengthened by explicitly aligning your observations with a recognised model such as CBT or Solution-Focused Therapy."
            )

        # Modality
        if result["scores"]["modality"]:
            feedback_parts.append(
                "You showed good awareness of how the client experiences their problem, correctly identifying their modality."
            )
        else:
            feedback_parts.append(
                "Try to pay closer attention to the client’s language to identify whether their experience is visual, auditory, or kinaesthetic."
            )

        # Safety
        if result["scores"]["safety"]:
            feedback_parts.append(
                "You demonstrated awareness of safety and suitability, which is important in early assessment."
            )
        else:
            feedback_parts.append(
                "Safety considerations were not clearly addressed. It is important to assess risk and suitability during early stages."
            )

        # Objective
        if result["scores"]["objective"]:
            feedback_parts.append(
                "You identified the client’s core objective clearly, which supports effective treatment planning."
            )
        else:
            feedback_parts.append(
                "The client’s core objective could be clarified further by summarising what they want to achieve."
            )

        # ✅ NEW: ADD CLINICAL OBSERVATION FROM SESSION
        if empathy_issues:
            feedback_parts.extend(empathy_issues)

        # Overall
        feedback_parts.append(
            f"\nOverall, you scored {result['total']} out of 4."
        )

        feedback_parts.append(
            "This was a solid clinical attempt with clear strengths. With further refinement, your responses will become more structured, empathetic, and clinically precise."
        )

        feedback = "\n\n".join(feedback_parts)

        # SAVE SESSION
        save_session(req.clientName, result["total"])

        return {
            "feedback": feedback,
            "score": {"total": result["total"]},
            "detected_modality": result["modality_label"]
        }

    except Exception as e:
        print("TUTOR ERROR:", e)
        return {
            "feedback": "Tutor feedback unavailable.",
            "score": {"total": 0},
            "detected_modality": None
        }


# ✅ PROGRESS ENDPOINT (FIXES 404)
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