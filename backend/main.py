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
    persona_reply = get_persona_response(
        msg.clientType, stage, risk_sessions[session_id]
    )

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


# ✅ STRONGER Q4 DETECTION (FINAL)
def evaluate_q4(text):
    t = text.lower()

    safety = any(x in t for x in [
        "risk", "medical", "history", "screen", "contraindication"
    ])

    reassurance = any(x in t for x in [
        "reassure", "safe", "comfortable", "support", "ease"
    ])

    readiness = any(x in t for x in [
        "ready",
        "ready to proceed",
        "confirmed ready",
        "confirmed readiness",
        "they are ready",
        "they were ready",
        "we agreed to proceed",
        "happy to proceed",
        "okay to continue",
        "we can begin",
        "before we begin",
        "proceed",
        "continue",
        "move forward"
    ])

    return {
        "safety": safety,
        "reassurance": reassurance,
        "readiness": readiness
    }


@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    s = req.submission

    q1_text = s.get("chosenApproach", "").lower()
    q2_text = s.get("clientModality", "").lower()
    q3_text = s.get("clientObjective", "").lower()

    q1 = "cbt" in q1_text or "cognitive" in q1_text
    q2 = any(x in q2_text for x in ["visual", "auditory", "kinaesthetic"])
    q3 = any(x in q3_text for x in ["goal", "reduce", "manage", "control"])

    q4_data = evaluate_q4(s.get("clientReassurance", ""))
    q4 = all(q4_data.values())

    # ✅ FIXED Q4 FEEDBACK BLOCK (STABLE)
    if q4:
        q4_feedback = "✔ You addressed safety, reassurance, and readiness appropriately."
    else:
        q4_feedback = f"""✘ Safety & reassurance could be strengthened:

• Safety screening: {"✔ addressed" if q4_data["safety"] else "✘ not clearly addressed"}
• Reassurance: {"✔ provided" if q4_data["reassurance"] else "✘ could be clearer"}
• Readiness to proceed: {"✔ confirmed" if q4_data["readiness"] else "✘ not explicitly confirmed"}
"""

    # ✅ FINAL STRUCTURED FEEDBACK
    feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Appropriate model selected. Cognitive Behavioural Therapy (CBT) is suitable based on the client’s presentation of anxiety and thought patterns." if q1 else "✘ The selected approach is unclear. A Cognitive Behavioural Therapy (CBT) approach would be more appropriate based on the client’s anxiety presentation and thinking patterns."}

QUESTION 2 — Client Modality
{"✔ Modality correctly identified." if q2 else "✘ The client’s language suggests a kinaesthetic modality (focus on feelings, tension, and bodily sensations)."}

QUESTION 3 — Client Objective
{"✔ Objective clearly defined and relevant." if q3 else "✘ The objective should clearly state what the client wants to change or achieve (e.g., reducing anxiety or improving coping)."}

QUESTION 4 — Safety & Reassurance
{q4_feedback}
"""

    total = sum([q1, q2, q3, q4])
    save_session(req.clientName, total)

    return {
        "feedback": feedback.strip(),
        "score": {"total": total},
        "detected_modality": "Kinaesthetic"
    }