import json
import os
import random

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/case_histories.json")

with open(DATA_PATH, "r") as f:
    case_histories = json.load(f)


def get_persona_response(client_name, stage, state):

    trust = state["trust"]
    distress = state["distress"]
    resistance = state["resistance"]
    risk = state["risk_flag"]

    behaviour_explored = state.get("behaviour_explored", False)

    tone = "neutral"

    if trust > 70:
        tone = "open"
    elif resistance > 60:
        tone = "resistant"
    elif distress > 60:
        tone = "distressed"

    response_style = f"""
Client emotional state:
- Trust: {trust}
- Distress: {distress}
- Resistance: {resistance}

Behaviour rules:
- If trust is high → open up more
- If resistance is high → give short hesitant replies
- If distress is high → show emotional difficulty
"""

    # ✅ MODALITY RULE ENFORCEMENT
    if not behaviour_explored:
        response_style += """
IMPORTANT:
Do NOT reveal how you relax or hobbies unless specifically asked.
Do NOT provide behaviour-based answers yet.
"""
    else:
        response_style += """
Now you may describe what you do to relax or hobbies naturally.
Use this to reveal modality through behaviour.
"""

    # ✅ FIXED: "I USED TO" (NOT RANDOM — TRIGGERED CONDITION)
    if distress > 35 and stage in ["timeline", "feelings", "body"]:
        response_style += """
Include a natural sentence like:
"I used to enjoy doing things like that, but I don't seem to anymore."
"""

    if risk != "none":
        response_style += """
Include subtle expressions of overwhelm or wanting to escape.
"""

    return response_style