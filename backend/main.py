from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

from services.session_tracker import save_session, get_sessions
from services.progress_engine import calculate_progress

# ✅ UPDATED IMPORTS (Phase 2A)
from services.conversation_engine import (
    get_stage,
    detect_stage_from_question,
    update_state,
    get_state
)
from services.persona_engine import get_persona_response
from services.prompt_builder import build_prompt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Message(BaseModel):
    text: str
    clientType: str
    history: list = []
    sessionId: str | None = None


class TutorRequest(BaseModel):
    submission: dict
    chatHistory: list
    clientName: str


# ============================
# ✅ CHAT ENDPOINT (UNCHANGED)
# ============================
@app.post("/chat")
async def chat(msg: Message):

    client_type = msg.clientType or "Daniel"
    session_id = msg.sessionId or (client_type + "_session")

    stage = detect_stage_from_question(msg.text) or get_stage(session_id)

    try:
        state = update_state(session_id, msg.text)
    except Exception:
        state = get_state(session_id)

    persona = get_persona_response(client_type, stage, state)
    system_prompt = build_prompt(stage, persona)

    messages = [{"role": "system", "content": system_prompt}]

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

    return {
        "reply": reply,
        "stage": stage,
        "state": state
    }


# ============================
# ✅ TUTOR EVALUATION (FIXED ONLY WHERE NEEDED)
# ============================
def evaluate_q4(text):
    t = text.lower()

    # ✅ FIX: slightly expanded keywords (minimal but necessary)
    safety = any(x in t for x in [
        "risk", "medical", "history", "screen", "contraindication"
    ])

    reassurance = any(x in t for x in [
        "reassure", "safe", "comfortable", "support", "ease", "okay", "you're safe"
    ])

    readiness = any(x in t for x in [
        "ready", "proceed", "continue", "begin", "move forward", "we can start"
    ])

    return {
        "safety": safety,
        "reassurance": reassurance,
        "readiness": readiness
    }


@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    s = req.submission
    chat = req.chatHistory

    q1_text = s.get("chosenApproach", "").lower()
    q2_text = s.get("clientModality", "").lower()
    q3_text = s.get("clientObjective", "").lower()
    q4_text = s.get("clientReassurance", "").lower()

    q1 = "cbt" in q1_text or "cognitive" in q1_text

    # ✅ behavioural detection (UNCHANGED)
    asked_behaviour = any(
        any(x in m["text"].lower() for x in [
            "relax",
            "hobbies",
            "fun",
            "downtime",
            "what do you enjoy",
            "what do you like to do",
            "how do you switch off",
            "what helps you relax"
        ])
        for m in chat if m["role"] == "therapist"
    )

    q2 = asked_behaviour and any(x in q2_text for x in [
        "visual", "auditory", "kinaesthetic"
    ])

    q3 = any(x in q3_text for x in ["goal", "reduce", "manage", "control"])

    # ✅ stress detection (UNCHANGED)
    stress_present = any(
        any(x in m["text"].lower() for x in [
            "i used to",
            "used to enjoy",
            "don't do that anymore",
            "haven't done that in a long time"
        ])
        for m in chat if m["role"] == "client"
    )

    # ✅ FIX: more flexible + realistic clinical phrasing detection
    handled_stress = (
        any(x in q4_text for x in [
            "used to",
            "not doing",
            "stopped",
            "no longer"
        ]) and
        any(x in q4_text for x in [
            "stress",
            "overwhelm",
            "sign",
            "affect",
            "impact",
            "difficult"
        ]) and
        any(x in q4_text for x in [
            "will",
            "again",
            "you'll",
            "you will",
            "begin",
            "return",
            "able",
            "start"
        ])
    )

    stress_score = True if (not stress_present or handled_stress) else False

    q4_data = evaluate_q4(q4_text)
    q4 = all(q4_data.values()) and stress_score

    stress_feedback = ""
    if stress_present:
        if handled_stress:
            stress_feedback = "✔ You correctly identified the reduction in pleasurable activity as a stress indicator."
        else:
            stress_feedback = "✘ You missed the client's ‘I used to…’ stress indicator."

    feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Appropriate model selected." if q1 else "✘ Approach unclear."}

QUESTION 2 — Client Modality
{"✔ Correct (behaviour explored)." if q2 else "✘ Modality must be based on behavioural questioning."}

QUESTION 3 — Client Objective
{"✔ Objective clear." if q3 else "✘ Objective unclear."}

QUESTION 4 — Safety & Reassurance
{"✔ Appropriate." if q4 else "✘ Needs improvement."}

STRESS INDICATOR
{stress_feedback}
"""

    total = sum([q1, q2, q3, q4])
    save_session(req.clientName, total)

    return {
        "feedback": feedback.strip(),
        "score": {"total": total},
        "detected_modality": "Kinaesthetic"
    }


# ============================
# ✅ PROGRESS (UNCHANGED)
# ============================
@app.get("/progress")
def progress():

    sessions = get_sessions()

    if not sessions:
        return {
            "sessionsCompleted": 0,
            "averageScore": 0,
            "personasCompleted": []
        }

    total_sessions = len(sessions)
    avg_score = sum(s["score"] for s in sessions) / total_sessions
    personas = list(set(s["client"] for s in sessions))

    return {
        "sessionsCompleted": total_sessions,
        "averageScore": round(avg_score, 2),
        "personasCompleted": personas
    }