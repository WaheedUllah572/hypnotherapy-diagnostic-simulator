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


# ✅ Q4 STRUCTURED EVALUATION
def evaluate_q4(student_text: str):

    text = student_text.lower()

    safety = any(x in text for x in [
        "risk", "safety", "medical", "history", "screen", "contraindication"
    ])

    reassurance = any(x in text for x in [
        "reassure", "safe", "comfortable", "support"
    ])

    readiness = any(x in text for x in [
        "ready", "proceed", "continue", "before we begin"
    ])

    return {
        "safety": safety,
        "reassurance": reassurance,
        "readiness": readiness
    }


@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    try:
        time.sleep(1)

        s = req.submission

        q1 = evaluate_response(s.get("chosenApproach", ""), "approach")
        q2 = evaluate_response(s.get("clientModality", ""), "modality")
        q3 = evaluate_response(s.get("clientObjective", ""), "objective")

        q4_data = evaluate_q4(s.get("clientReassurance", ""))
        q4 = all(q4_data.values())

        # -------- CONVERSATION CONTEXT --------
        therapist_lines = [
            m["text"]
            for m in req.chatHistory if m["role"] == "therapist"
        ]

        client_lines = [
            m["text"]
            for m in req.chatHistory if m["role"] == "client"
        ]

        last_therapist = therapist_lines[-1] if therapist_lines else ""
        last_client = client_lines[-1] if client_lines else ""

        # -------- EMPATHY CHECK --------
        empathy_issue = not any(
            x in last_therapist.lower()
            for x in ["understand", "that sounds", "i hear", "that must"]
        )

        # -------- MODALITY --------
        full_chat = " ".join(client_lines).lower()

        kinaesthetic = sum(w in full_chat for w in ["feel", "tight", "tense", "pressure", "body"])
        auditory = sum(w in full_chat for w in ["hear", "sound"])
        visual = sum(w in full_chat for w in ["see", "image"])

        modality = "Kinaesthetic"
        if auditory > kinaesthetic:
            modality = "Auditory"
        elif visual > kinaesthetic:
            modality = "Visual"

        # -------- Q4 FEEDBACK (DETAILED) --------
        if q4:
            q4_feedback = "✔ You addressed safety, reassurance, and readiness appropriately."
        else:
            q4_feedback = f"""✘ Safety & reassurance could be strengthened:

• Safety screening: {"✔ addressed" if q4_data["safety"] else "✘ not clearly addressed"}
• Reassurance: {"✔ provided" if q4_data["reassurance"] else "✘ could be clearer"}
• Readiness to proceed: {"✔ confirmed" if q4_data["readiness"] else "✘ not explicitly confirmed"}"""

        # -------- EMPATHY FEEDBACK (CONTEXTUAL) --------
        if empathy_issue:
            empathy_feedback = f'• Your response "{last_therapist[:80]}..." could include a brief acknowledgment of the client’s experience before guiding further.'
        else:
            empathy_feedback = "✔ Your interaction style was supportive and appropriately paced."

        # -------- FINAL FEEDBACK --------
        feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Appropriate model selected and linked to the client’s presentation." if q1 else "✘ Treatment approach needs clearer clinical reasoning."}

QUESTION 2 — Client Relaxation Modality
{"✔ Modality correctly identified." if q2 else f"✘ Modality unclear. Example client language: \"{last_client[:80]}...\""}

QUESTION 3 — Client Objective
{"✔ Objective clearly defined and relevant." if q3 else "✘ Objective needs to be more specific and outcome-focused."}

QUESTION 4 — Safety & Reassurance
{q4_feedback}

CLINICAL INTERACTION OBSERVATIONS
{empathy_feedback}

OVERALL CLINICAL IMPRESSION
You are developing solid clinical reasoning. Continue refining clarity, empathy, and structure for stronger client outcomes.
"""

        total = sum([q1, q2, q3, q4])

        save_session(req.clientName, total)

        return {
            "feedback": feedback.strip(),
            "score": {"total": total},
            "detected_modality": modality
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
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


def evaluate_response(student_text: str, mode: str):

    text = student_text.lower()

    if mode == "approach":
        return any(x in text for x in [
            "cognitive behavioural", "cbt", "cbh",
            "solution focused", "ericksonian", "regression"
        ])

    if mode == "modality":
        return any(x in text for x in [
            "visual", "auditory", "kinaesthetic", "feel", "see", "hear"
        ])

    if mode == "objective":
        return any(x in text for x in [
            "want", "goal", "reduce", "manage", "control", "cope"
        ])

    return False


sessions_db = []

def save_session(client, score):
    sessions_db.append({
        "client": client,
        "score": score,
    })

def get_sessions():
    return sessions_db