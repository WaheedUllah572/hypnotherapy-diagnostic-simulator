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
        "Be cautious. Answer only the therapist's question. Keep replies brief. Avoid volunteering extra information or discussing emotions unless directly invited."
    )

    elif trust_level == "medium":
     behaviour_guidance.append(
        "Answer naturally. Provide a little additional context when appropriate, but wait for invitations before giving deeper emotional detail."
    )

    else:
     behaviour_guidance.append(
        "You feel safe with the therapist. Speak warmly, volunteer one small relevant detail naturally, and reflect more openly on your thoughts and feelings."
    )

# Resistance

    if resistance_level == "high":
     behaviour_guidance.append(
        "Pause before answering. Keep replies short. Avoid unnecessary elaboration and only discuss sensitive topics if the therapist gently explores them."
    )

    elif resistance_level == "medium":
     behaviour_guidance.append(
        "Be cooperative but slightly cautious. Discuss difficult topics carefully without becoming defensive."
    )

    else:
     behaviour_guidance.append(
        "Respond openly. Expand naturally when appropriate and do not sound guarded."
    )

# Distress

    if distress_level == "high":
     behaviour_guidance.append(
        "Emotionally difficult topics should feel overwhelming. It is natural to hesitate, become emotional, or struggle to describe difficult experiences."
    )

    elif distress_level == "medium":
     behaviour_guidance.append(
        "Show emotion when discussing the presenting problem but remain calm during neutral parts of the conversation."
    )

    else:
     behaviour_guidance.append(
        "Remain emotionally calm and composed. Discuss difficult experiences without becoming overwhelmed."
    )


     # ==========================================
# COMBINED BEHAVIOUR RULES
# ==========================================

    if trust >= 80 and resistance < 30:
         behaviour_guidance.append(
            "You now trust the therapist enough to volunteer one small relevant detail naturally without being asked."
        )

    if trust < 40 and resistance >= 60:
        behaviour_guidance.append(
            "Remain polite but reserved. Answer only what was asked and avoid unnecessary elaboration."
        )

    if distress >= 80 and trust >= 70:
        behaviour_guidance.append(
            "Although discussing difficult emotions is upsetting, you feel safe enough to describe them honestly."
        )

    behaviour_guidance.append(
        personality["communication"]
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