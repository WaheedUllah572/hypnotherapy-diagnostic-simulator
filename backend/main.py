from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

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


@app.post("/chat")
async def chat(msg: Message):

    safety_keywords = ["kill myself", "end my life", "suicide", "self harm"]
    if any(k in msg.text.lower() for k in safety_keywords):
        return {
            "reply": "Safety threshold reached. Pre-induction cannot continue.",
            "safety_flag": True
        }

    if msg.clientType == "CBH":
        persona = """
You are a client suited to Cognitive Behavioural Hypnotherapy.
Focus on thoughts, beliefs and worries.
Use phrases like “I keep thinking…”, “What if…”
Progress conversation gradually.
Avoid repeating identical emotional phrases.
"""

    elif msg.clientType == "SH":
        persona = """
You are a Solution-Focused client.
Speak about emotional states.
Progress emotional narrative gradually.
Avoid repeating the same wording unless adding new detail.
"""

    elif msg.clientType == "Ericksonian":
        persona = """
You are an indirect, metaphorical client.
Use imagery.
Allow narrative to evolve naturally.
Avoid repetition.
"""

    elif msg.clientType == "Regression":
        persona = """
You link present anxiety to earlier life memories.
Develop narrative progressively.
Do not repeat the same explanation twice.
"""

    else:
        persona = "You are an anxious client unsure how to explain what is happening."

    system = f"""
You are a therapy training simulation client.

Stay strictly in character.
Do NOT give advice.
Do NOT act like a therapist.
Respond naturally in 1–3 sentences.
Avoid repetition of previously stated emotional phrases.
Progress the narrative gradually.

Client behaviour style:
{persona}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": msg.text}
        ]
    )

    return {
        "reply": response.choices[0].message.content,
        "safety_flag": False
    }


class TutorSubmission(BaseModel):
    submission: dict
    chatHistory: list


# ---------------- PHASE 3 SCORING ENGINE ----------------

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
    chat_text = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in data.chatHistory])

    system = """
You are a clinical hypnotherapy training tutor.

Structure your feedback clearly with headings:

Approach Fit
Modality Identification
Client Objective
Safety & Reassurance
Overall Comments

Quote specific dialogue excerpts.
Be supportive but corrective.
Use clean spacing and short paragraphs.
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

    score = evaluate_submission(s)

    return {
        "feedback": response.choices[0].message.content,
        "score": score
    }