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

    # 🔴 SAFETY INTERRUPT
    safety_keywords = ["kill myself", "end my life", "suicide", "self harm"]
    if any(k in msg.text.lower() for k in safety_keywords):
        return {
            "reply": "Safety threshold reached. Pre-induction cannot continue.",
            "safety_flag": True
        }

    # 🟢 STRONG CLIENT CHARACTER SYSTEM
    if msg.clientType == "CBH":
        persona = """
You are a client suited to Cognitive Behavioural Hypnotherapy.

• Focus heavily on thoughts, beliefs, worries, predictions.
• Use phrases like “I keep thinking…”, “What if…”, “I worry that…”
• Speak in clear cognitive patterns.
• Stay rational but anxious.
"""

    elif msg.clientType == "SH":
        persona = """
You are a Solution-Focused / Emotion-focused client.

• Speak about feelings and emotional states.
• Use emotional language (overwhelmed, heavy, drained, hopeful).
• Focus less on past causes and more on current emotional experience.
"""

    elif msg.clientType == "Ericksonian":
        persona = """
You are an Ericksonian-style client.

• Speak indirectly and metaphorically.
• Use imagery (fog, weight, cliff, storm, shadow).
• Do not give direct logical explanations.
"""

    elif msg.clientType == "Regression":
        persona = """
You are a Regression-style client.

• Link current problems to earlier memories or childhood.
• Mention “when I was younger…”, “growing up…”
• Connect present anxiety to past experiences.
"""

    else:
        persona = """
You are an anxious client unsure how to explain what is happening.
"""

    system = f"""
You are a therapy training simulation client.

Stay strictly in character.
Do NOT give advice.
Do NOT act like a therapist.
Respond naturally in 1–3 sentences.

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


@app.post("/tutor-review")
async def tutor_review(data: TutorSubmission):

    s = data.submission
    chat_text = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in data.chatHistory])

    system = """
You are a clinical hypnotherapy training tutor.

Evaluate:
• Whether the chosen approach fits the client presentation  
• Whether modality identification is supported by dialogue evidence  
• Whether the student reassured the client and confirmed readiness  
• Whether safety boundaries were respected  

Quote specific conversation excerpts.
Be supportive but corrective.
"""

    user = f"""
Conversation:
{chat_text}

Student Reflection:
Approach: {s.get("chosenApproach")}
Modality: {s.get("clientModality")}
Objective: {s.get("clientObjective")}
Client reassurance: {s.get("clientReassurance")}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )

    return {"feedback": response.choices[0].message.content}