from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

from services.session_tracker import save_session, get_sessions
from services.progress_engine import calculate_progress

# NEW IMPORTS
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


class Message(BaseModel):
    text: str
    clientType: str
    history: list = []


@app.post("/chat")
async def chat(msg: Message):

    safety_keywords = ["kill myself", "end my life", "suicide", "self harm"]
    if any(k in msg.text.lower() for k in safety_keywords):
        return {
            "reply": "Safety threshold reached. Pre-induction cannot continue.",
            "safety_flag": True
        }

    session_id = msg.clientType

    detected_stage = detect_stage_from_question(msg.text)
    if detected_stage:
        stage = detected_stage
    else:
        stage = get_stage(session_id)

    persona_reply = get_persona_response(msg.clientType, stage)

    system = f"""
You are role-playing as a therapy client in a pre-hypnosis assessment session.

IMPORTANT:
• Respond directly to the therapist’s question.
• Keep answers to 1–3 sentences.
• Speak naturally like a real client.
• Do not repeat previous answers.
• Reveal information gradually.

Current session stage: {stage}

Client information to use in your answer:
{persona_reply}
"""

    messages = [{"role": "system", "content": system}]

    for m in msg.history:
        if m["role"] == "therapist":
            messages.append({"role": "user", "content": m["text"]})
        elif m["role"] == "client":
            messages.append({"role": "assistant", "content": m["text"]})

    messages.append({"role": "user", "content": msg.text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    advance_stage(session_id)

    return {
        "reply": response.choices[0].message.content,
        "safety_flag": False
    }


class TutorSubmission(BaseModel):
    submission: dict
    chatHistory: list
    clientName: str


def evaluate_submission(submission):

    score = {
        "approach": 0,
        "modality": 0,
        "objective": 0,
        "safety": 0
    }

    if submission.get("chosenApproach"):
        score["approach"] = 1
    if submission.get("clientModality"):
        score["modality"] = 1
    if submission.get("clientObjective"):
        score["objective"] = 1
    if submission.get("clientReassurance"):
        score["safety"] = 1

    total = sum(score.values())

    return {
        "breakdown": score,
        "total": total
    }


@app.post("/tutor-review")
async def tutor_review(data: TutorSubmission):

    s = data.submission
    score = evaluate_submission(s)

    save_session(data.clientName, score["total"])

    chat_text = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in data.chatHistory])

    system = """
You are a clinical hypnotherapy training tutor.

Structure your feedback clearly with headings:

Approach Fit
Modality Identification
Client Objective
Safety & Reassurance
Overall Comments
"""

    user = f"""
Conversation:
{chat_text}

Student Reflection:
Approach: {s.get("chosenApproach")}
Modality: {s.get("clientModality")}
Objective: {s.get("clientObjective")}
Safety/Reassurance: {s.get("clientReassurance")}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )

    return {
        "feedback": response.choices[0].message.content,
        "score": score
    }


@app.get("/progress")
async def get_progress():
    sessions = get_sessions()
    return calculate_progress(sessions)