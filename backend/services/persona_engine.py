import json
import os
import random

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/case_histories.json")

with open(DATA_PATH, "r") as f:
    case_histories = json.load(f)


def get_persona_response(client_name, stage):

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
"My mind goes to..."
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

    # 🔥 FIXED: Clear modality most of the time
    if random.random() < 0.8:
        modality_instruction = f"""
Use CLEAR {dominant_modality} sensory language in your response.
Do NOT mix modalities.
"""
    else:
        modality_instruction = f"""
Use MOSTLY {dominant_modality} language but include ONE other sensory hint.
This should create slight ambiguity.
"""

    return f"""
Client background information:
{info}

Communication style:
{style}

Modality instruction:
{modality_instruction}

Respond naturally to the therapist.
Keep responses 1–3 sentences.
Do not explain too much at once.
"""