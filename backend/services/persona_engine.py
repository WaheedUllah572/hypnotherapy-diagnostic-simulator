import json
import os
import random

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/case_histories.json")

with open(DATA_PATH, "r") as f:
    case_histories = json.load(f)


def get_persona_response(client_name, stage, risk_mode=False):

    case = case_histories.get(client_name)

    if not case:
        return "The client seems unsure and is trying to explain their problem."

    info = case.get(stage, "")
    persona_type = case.get("type", "")

    # Communication style per persona
    if persona_type == "CBH":
        style = """
You are a Cognitive Behavioural client.
Speak using thought-based language like:
"I keep thinking..."
"I worry that..."
"I keep imagining..."
"""
        dominant_modality = "Visual"

    elif persona_type == "SH":
        style = """
You are an emotional / solution-focused client.
Speak using feeling and emotional language like:
"I feel overwhelmed..."
"I feel under pressure..."
"""
        dominant_modality = "Auditory"

    elif persona_type == "Ericksonian":
        style = """
You are an Ericksonian-style client.
Speak using metaphor and imagery like:
"It's like..."
"I feel like I'm..."
"""
        dominant_modality = "Kinaesthetic"

    elif persona_type == "Regression":
        style = """
You are a regression-style client.
Link present problems to past experiences.
"""
        dominant_modality = "Kinaesthetic"

    else:
        style = "Speak naturally."
        dominant_modality = "Kinaesthetic"

    # 🔴 IMPORTANT: Risk behaviour instruction (UNCHANGED)
    risk_instruction = ""
    if risk_mode:
        risk_instruction = """
IMPORTANT SAFETY BEHAVIOUR:
You are an emotionally vulnerable client.

When the therapist asks about:
- feelings
- stress
- coping
- sleep
- feeling overwhelmed
- wanting to escape
- feeling trapped
- giving up

You MUST include at least one of the following ideas in your response:
- feeling trapped
- wanting to escape
- wanting everything to stop
- feeling like giving up
- feeling like you can't go on
- wishing you could disappear

Keep it natural and realistic, not dramatic.
Use 1–2 sentences only.
"""

    # ✅ FIXED MODALITY LOGIC (CLIENT REQUIREMENT)
    if random.randint(1, 15) == 1:
        modality_instruction = f"""
Use MOSTLY {dominant_modality} language but include ONE other sensory hint.
"""
    else:
        modality_instruction = f"""
Use CLEAR {dominant_modality} sensory language.
Do NOT mix modalities.
"""

    return f"""
Client background information:
{info}

Communication style:
{style}

{risk_instruction}

Modality instruction:
{modality_instruction}

Respond naturally to the therapist.
Keep responses to 1–3 sentences.
Do not explain everything at once.
"""