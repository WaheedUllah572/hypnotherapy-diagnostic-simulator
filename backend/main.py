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


@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    try:
        time.sleep(1)

        s = req.submission

        q1 = evaluate_response(s.get("chosenApproach", ""), "approach")
        q2 = evaluate_response(s.get("clientModality", ""), "modality")
        q3 = evaluate_response(s.get("clientObjective", ""), "objective")
        q4 = evaluate_response(s.get("clientReassurance", ""), "safety")

        # ✅ DEFINE empathy_issue (FIXED)
        therapist_lines = [
            m["text"].lower()
            for m in req.chatHistory if m["role"] == "therapist"
        ]

        empathy_issue = any(
            x in line for line in therapist_lines
            for x in ["just relax", "calm down", "you can relax"]
        )

        # -------- MODALITY FROM CHAT --------
        full_chat = " ".join([
            m["text"].lower()
            for m in req.chatHistory if m["role"] == "client"
        ])

        kinaesthetic = sum(w in full_chat for w in ["feel", "tight", "tense", "pressure", "body"])
        auditory = sum(w in full_chat for w in ["hear", "sound"])
        visual = sum(w in full_chat for w in ["see", "image"])

        modality = "Kinaesthetic"
        if auditory > kinaesthetic:
            modality = "Auditory"
        elif visual > kinaesthetic:
            modality = "Visual"

        # -------- FIXED FEEDBACK --------
        feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ You identified an appropriate therapeutic model and linked it well to the client’s presentation. This shows good clinical reasoning and understanding of how the client’s difficulties are maintained." 
if q1 
else 
"✘ The treatment approach needs to be more clearly defined. Try explicitly linking the client’s symptoms and thinking patterns to a recognised therapeutic model such as CBH, Solution-Focused, or Ericksonian approaches."}

QUESTION 2 — Client Relaxation Modality
{"✔ You correctly identified the client’s primary modality based on their language. This demonstrates good attention to how the client experiences their internal world." 
if q2 
else 
"✘ The client’s modality was not clearly identified. Focus more closely on sensory language to determine whether they are visual, auditory, or kinaesthetic."}

QUESTION 3 — Client Objective
{"✔ The client’s objective is clearly defined and relevant to their presenting issue." 
if q3 
else 
"✘ The client’s objective needs to be clearer. Try summarising what the client wants to change or achieve."}

QUESTION 4 — Safety & Reassurance
{"✔ You demonstrated appropriate awareness of safety and reassurance." 
if q4 
else 
"✘ Safety and suitability were not sufficiently addressed. You should explore health history and reassure the client."}

CLINICAL INTERACTION OBSERVATIONS
{"⚠ Some responses were slightly directive. Focus more on empathy and validation." 
if empathy_issue 
else 
"✔ Your interaction style was supportive and appropriate."}

OVERALL CLINICAL IMPRESSION
You are developing solid clinical reasoning. Continue refining structure, empathy, and clarity.
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

    if mode == "safety":
        return any(x in text for x in [
            "risk", "safety", "medical", "history", "screen", "suitability"
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