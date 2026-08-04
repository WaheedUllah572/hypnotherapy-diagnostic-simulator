"""
Dynamic Behaviour Controller

This engine converts the current conversation state into
a dynamic behavioural profile.

It does NOT generate responses.

It determines HOW the client should behave based on:

- trust
- distress
- resistance
- risk
- treatment approach

The Persona Engine consumes this profile.
"""

from services.response_variation_engine import (
    get_response_variation
)

from services.personality_engine import (
    get_personality
)


def get_dynamic_behaviour(
    client_name: str,
    trust: int,
    distress: int,
    resistance: int,
    risk: str,
    treatment_approach: str
):

    variation = get_response_variation(
        trust=trust,
        distress=distress,
        resistance=resistance,
        treatment_approach=treatment_approach
    )

# ==========================================
# TRUST LEVEL
# ==========================================

    if trust >= 80:
     trust_level = "high"

    elif trust >= 60:
     trust_level = "medium"

    else:
     trust_level = "low"


     # ==========================================
# DISTRESS LEVEL
# ==========================================

    if distress >= 80:
     distress_level = "high"

    elif distress >= 55:
     distress_level = "medium"

    else:
     distress_level = "low"

     # ==========================================
# RESISTANCE LEVEL
# ==========================================

    if resistance >= 70:
     resistance_level = "high"

    elif resistance >= 45:
     resistance_level = "medium"

    else:
     resistance_level = "low"

    personality = get_personality(client_name)

    # ==========================================
    # SELF DISCLOSURE
    # ==========================================

    if trust >= 80:
        self_disclosure = "high"

    elif trust >= 60:
        self_disclosure = "moderate"

    else:
        self_disclosure = "low"

    # ==========================================
    # DEFENSIVENESS
    # ==========================================

    if resistance >= 70:
        defensiveness = "high"

    elif resistance >= 45:
        defensiveness = "moderate"

    else:
        defensiveness = "low"

    # ==========================================
    # EMOTIONAL ACCESS
    # ==========================================

    if distress >= 80:
        emotional_access = "deep"

    elif distress >= 55:
        emotional_access = "moderate"

    else:
        emotional_access = "light"

    # ==========================================
    # COOPERATION
    # ==========================================

    if trust >= 75 and resistance < 40:
        cooperation = "high"

    elif resistance >= 70:
        cooperation = "low"

    else:
        cooperation = "moderate"

    # ==========================================
    # RISK SENSITIVITY
    # ==========================================

    if risk != "none":
        risk_sensitivity = "high"
    else:
        risk_sensitivity = "normal"

    # ==========================================
    # RETURN PROFILE
    # ==========================================

    # ==========================================
    # DYNAMIC BEHAVIOUR GUIDANCE
    # ==========================================

    behaviour_guidance = []

# Trust

    if trust_level == "low":
     behaviour_guidance.append(
        "Be cautious. Give shorter answers. Do not volunteer extra information."
    )

    elif trust_level == "medium":
     behaviour_guidance.append(
        "Answer comfortably but only elaborate when invited."
    )

    else:
     behaviour_guidance.append(
        "You feel comfortable with the therapist. You may naturally provide a little more reflection and emotional openness."
    )

# Resistance

    if resistance_level == "high":
     behaviour_guidance.append(
        "Be hesitant and slightly guarded. Avoid long explanations."
    )

    elif resistance_level == "medium":
     behaviour_guidance.append(
        "Be cooperative but slightly cautious when discussing difficult topics."
    )

    else:
     behaviour_guidance.append(
        "Answer questions openly without sounding overly defensive."
    )

# Distress

    if distress_level == "high":
     behaviour_guidance.append(
        "Emotionally difficult topics should feel noticeably overwhelming."
    )

    elif distress_level == "medium":
     behaviour_guidance.append(
        "Show emotion when discussing the presenting problem, but remain composed during neutral topics."
    )

    else:
     behaviour_guidance.append(
        "Remain emotionally calm unless discussing distressing experiences."
    )

    return {

    "personality": personality,

    "variation": variation,

    "trust_level": trust_level,

    "distress_level": distress_level,

    "resistance_level": resistance_level,

    "behaviour_guidance": behaviour_guidance,

    "self_disclosure": self_disclosure,

    "defensiveness": defensiveness,

    "emotional_access": emotional_access,

    "cooperation": cooperation,

    "risk_sensitivity": risk_sensitivity
}