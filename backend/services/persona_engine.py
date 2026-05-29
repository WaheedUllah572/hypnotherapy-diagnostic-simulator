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

    # ============================
    # NEW: SCENARIO DATA
    # ============================
    persona = case_histories.get(client_name, {})

    condition = persona.get("condition", "")
    goal = persona.get("goal", "")
    symptoms = persona.get("symptoms", [])

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
    # PERSONA-SPECIFIC PRESENTATION
    # ============================

    if client_name == "Claire":

        response_style += """
Primary focus:
- motorway driving
- panic while driving
- fear of losing control
- avoidance of motorways

Avoid:
- work performance concerns
- sleep difficulties
- crowd anxiety
"""

    elif client_name == "Daniel":

        response_style += """
Primary focus:
- work pressure
- performance anxiety
- fear of failure
- disappointing others
- responsibility overload

Avoid:
- motorway fears
- sleep difficulties
- crowd anxiety
"""

    elif client_name == "Sophie":

        response_style += """
Primary focus:
- crowded places
- busy environments
- noise and activity
- sensory overwhelm
- feeling trapped
- wanting to escape

Avoid:
- work performance concerns
- deadlines
- fear of failure
- sleep difficulties
"""

    elif client_name == "Mark":

        response_style += """
Primary focus:
- sleep difficulties
- night-time worry
- racing thoughts
- inability to switch off
- fatigue

Avoid:
- motorway fears
- crowd anxiety
- work performance themes
"""

    # ============================
    # SCENARIO CONSISTENCY
    # ============================

    response_style += f"""

SCENARIO CONSISTENCY RULES

Current condition:
{condition}

Core objective:
{goal}

Core symptoms:
{", ".join(symptoms)}

IMPORTANT:
Remain fully consistent with this specific scenario.

Keep responses aligned with:
- the presenting problem
- the symptom pattern
- the emotional presentation
- the client objective

Do NOT drift into symptoms, fears, goals,
or experiences that belong to other client scenarios.
"""

    return response_style

    # ============================
    # NEW: SCENARIO CONSISTENCY
    # ============================
    response_style += f"""

SCENARIO CONSISTENCY RULES

Current condition:
{condition}

Core objective:
{goal}

Core symptoms:
{", ".join(symptoms)}

IMPORTANT:
Remain fully consistent with this specific scenario.

Keep responses aligned with:
- the presenting problem
- the symptom pattern
- the emotional presentation
- the client objective

Do NOT drift into symptoms, fears, goals,
or experiences that belong to other client scenarios.
"""

    return response_style