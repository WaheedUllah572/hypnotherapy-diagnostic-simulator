import json
import os
import random

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data/case_histories.json"
)

with open(DATA_PATH, "r") as f:
    case_histories = json.load(f)


def get_persona_response(client_name, stage, state):

    trust = state["trust"]
    distress = state["distress"]
    resistance = state["resistance"]
    risk = state["risk_flag"]

    behaviour_explored = state.get(
        "behaviour_explored",
        False
    )

    tone = "neutral"

    # ============================
    # CLIENT STATE LOGIC
    # ============================
    if trust > 70:
        tone = "open"

    elif resistance > 60:
        tone = "resistant"

    elif distress > 60:
        tone = "distressed"

    # ============================
    # BASE RESPONSE STYLE
    # ============================
    response_style = f"""
Client emotional state:
- Trust: {trust}
- Distress: {distress}
- Resistance: {resistance}

Current tone:
- {tone}

Behaviour rules:
- If trust is high → open up more naturally
- If resistance is high → give shorter hesitant replies
- If distress is high → show emotional difficulty and overwhelm
- Remain realistic and conversational
"""

    # ============================
    # MODALITY RULE ENFORCEMENT
    # ============================
    if not behaviour_explored:

        response_style += """
IMPORTANT:
Do NOT reveal hobbies, relaxation methods,
or behavioural coping strategies unless
specifically asked.

You may describe emotions and stress,
but NOT modality-revealing behaviour yet.
"""

    else:

        response_style += """
Now you may naturally describe:
- hobbies
- relaxation behaviour
- downtime activities
- coping habits

Use real-world behaviour to reveal modality.
"""

        # ============================
        # STRESS INDICATOR RULE
        # ============================
        response_style += """
IMPORTANT:
If discussing previous enjoyable activities,
naturally include a stress-related reduction
in engagement such as:

- "I used to enjoy..."
- "I don't really do that anymore"
- "I haven't done that in a while"

This should feel natural and emotionally realistic,
not forced into every response.
"""

    # ============================
    # RISK / OVERWHELM LOGIC
    # ============================
    if risk != "none":

        response_style += """
Include subtle signs of emotional overwhelm,
exhaustion, or wanting to escape pressure.

Do NOT become extreme or crisis-focused unless prompted.
"""

    # ============================
    # ANXIETY PRESENTATION SUPPORT
    # ============================
    response_style += """
Where appropriate, show:
- worry
- overthinking
- emotional fatigue
- difficulty switching off
- tension about responsibilities
"""

    return response_style