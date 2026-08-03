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

    personality = get_personality(
    client_name
)

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

    return {

        "personality": personality,
        
        "variation": variation,

        "self_disclosure": self_disclosure,

        "defensiveness": defensiveness,

        "emotional_access": emotional_access,

        "cooperation": cooperation,

        "risk_sensitivity": risk_sensitivity
    }