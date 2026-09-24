"""
Dynamic Behaviour Controller

This engine converts the current conversation state into a
dynamic behavioural profile.

It does NOT generate responses.

It determines HOW the client should communicate based on:

- trust
- distress
- resistance
- risk
- treatment approach

IMPORTANT:

Dynamic behaviour may change communication style, openness,
hesitation and emotional expression.

It must NEVER change:

- the authoritative client case
- established clinical facts
- personality
- symptoms
- timeline
- goals
- healthcare information
- safety information
"""

from typing import Any, Dict

from services.response_variation_engine import (
    get_response_variation,
)

from services.personality_engine import (
    get_personality,
)


# ============================================================
# HELPERS
# ============================================================

def _clamp(
    value: Any,
    minimum: int = 0,
    maximum: int = 100,
) -> int:
    """
    Safely convert a state value to an integer between 0 and 100.
    """

    try:
        value = int(value)
    except (TypeError, ValueError):
        value = minimum

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _normalise_risk(
    risk: Any,
) -> str:
    """
    Normalise the risk state.

    Missing/empty risk is treated as 'none'.

    This function does NOT determine whether risk exists.
    That decision belongs to the safety/evidence layer.
    """

    if risk is None:
        return "none"

    value = str(
        risk
    ).strip().lower()

    return value or "none"


def _level_from_thresholds(
    value: int,
    high_threshold: int,
    medium_threshold: int,
) -> str:
    """
    Convert a 0-100 state value into a simple level.
    """

    if value >= high_threshold:
        return "high"

    if value >= medium_threshold:
        return "medium"

    return "low"


# ============================================================
# MAIN CONTROLLER
# ============================================================

def get_dynamic_behaviour(
    client_name: str,
    trust: int,
    distress: int,
    resistance: int,
    risk: str,
    treatment_approach: str,
) -> Dict[str, Any]:
    """
    Build the current dynamic behavioural profile.

    The returned profile is consumed by the persona/prompt layers.

    Dynamic state affects communication only.
    It must never override authoritative case information.
    """

    # --------------------------------------------------------
    # NORMALISE STATE
    # --------------------------------------------------------

    trust = _clamp(
        trust
    )

    distress = _clamp(
        distress
    )

    resistance = _clamp(
        resistance
    )

    risk = _normalise_risk(
        risk
    )

    # --------------------------------------------------------
    # RESPONSE VARIATION
    # --------------------------------------------------------

    variation = get_response_variation(
        trust=trust,
        distress=distress,
        resistance=resistance,
        treatment_approach=treatment_approach,
    )

    if not isinstance(
        variation,
        dict,
    ):
        variation = {}

    # --------------------------------------------------------
    # PERSONALITY
    # --------------------------------------------------------

    personality = get_personality(
        client_name
    )

    if not isinstance(
        personality,
        dict,
    ):
        personality = {}

    # --------------------------------------------------------
    # TRUST LEVEL
    # --------------------------------------------------------

    trust_level = _level_from_thresholds(
        value=trust,
        high_threshold=80,
        medium_threshold=60,
    )

    # --------------------------------------------------------
    # DISTRESS LEVEL
    # --------------------------------------------------------

    distress_level = _level_from_thresholds(
        value=distress,
        high_threshold=80,
        medium_threshold=55,
    )

    # --------------------------------------------------------
    # RESISTANCE LEVEL
    # --------------------------------------------------------

    resistance_level = _level_from_thresholds(
        value=resistance,
        high_threshold=70,
        medium_threshold=45,
    )

    # --------------------------------------------------------
    # SELF DISCLOSURE
    # --------------------------------------------------------

    if trust >= 80:
        self_disclosure = "high"

    elif trust >= 60:
        self_disclosure = "moderate"

    else:
        self_disclosure = "low"

    # --------------------------------------------------------
    # DEFENSIVENESS
    # --------------------------------------------------------

    if resistance >= 70:
        defensiveness = "high"

    elif resistance >= 45:
        defensiveness = "moderate"

    else:
        defensiveness = "low"

    # --------------------------------------------------------
    # EMOTIONAL ACCESS
    # --------------------------------------------------------

    if distress >= 80:
        emotional_access = "deep"

    elif distress >= 55:
        emotional_access = "moderate"

    else:
        emotional_access = "light"

    # --------------------------------------------------------
    # COOPERATION
    # --------------------------------------------------------

    if trust >= 75 and resistance < 40:
        cooperation = "high"

    elif resistance >= 70:
        cooperation = "low"

    else:
        cooperation = "moderate"

    # --------------------------------------------------------
    # RISK SENSITIVITY
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Risk sensitivity does not mean the client has risk.
    #
    # It only tells the response layer to avoid casual,
    # exaggerated or invented responses around safety topics.
    #

    if risk != "none":
        risk_sensitivity = "high"

    else:
        risk_sensitivity = "normal"

    # ========================================================
    # BEHAVIOUR GUIDANCE
    # ========================================================

    behaviour_guidance = []

    # --------------------------------------------------------
    # TRUST GUIDANCE
    # --------------------------------------------------------

    if trust_level == "low":

        behaviour_guidance.append(
            "Be cautious and reserved. Answer the therapist's "
            "question directly and avoid volunteering unnecessary "
            "information."
        )

    elif trust_level == "medium":

        behaviour_guidance.append(
            "Answer naturally and provide a little additional "
            "context when appropriate, but do not automatically "
            "volunteer deeply personal information."
        )

    else:

        behaviour_guidance.append(
            "You feel relatively safe with the therapist. Speak "
            "more warmly and openly, and allow one small relevant "
            "detail to emerge naturally when appropriate."
        )

    # --------------------------------------------------------
    # RESISTANCE GUIDANCE
    # --------------------------------------------------------

    if resistance_level == "high":

        behaviour_guidance.append(
            "Be somewhat hesitant and concise. Sensitive topics "
            "may require gentle exploration before you elaborate."
        )

    elif resistance_level == "medium":

        behaviour_guidance.append(
            "Remain cooperative but slightly cautious when "
            "discussing difficult or personal topics."
        )

    else:

        behaviour_guidance.append(
            "Respond openly and cooperatively. Expand naturally "
            "when the therapist's question invites elaboration."
        )

    # --------------------------------------------------------
    # DISTRESS GUIDANCE
    # --------------------------------------------------------

    if distress_level == "high":

        behaviour_guidance.append(
            "Difficult emotional topics may be harder to discuss. "
            "Mild hesitation or emotional expression is appropriate, "
            "but do not exaggerate the distress."
        )

    elif distress_level == "medium":

        behaviour_guidance.append(
            "Show some emotional response when discussing the "
            "presenting problem while remaining reasonably composed "
            "during neutral conversation."
        )

    else:

        behaviour_guidance.append(
            "Remain relatively calm and composed while discussing "
            "the presenting problem."
        )

    # ========================================================
    # COMBINED STATE GUIDANCE
    # ========================================================

    if trust >= 80 and resistance < 30:

        behaviour_guidance.append(
            "Because trust is high and resistance is low, you may "
            "volunteer one small relevant detail naturally without "
            "waiting for a direct follow-up question."
        )

    if trust < 40 and resistance >= 60:

        behaviour_guidance.append(
            "Remain polite but reserved. Answer what was asked "
            "without unnecessary elaboration."
        )

    if distress >= 80 and trust >= 70:

        behaviour_guidance.append(
            "Although difficult emotions may feel upsetting, you "
            "feel sufficiently safe to describe them honestly."
        )

    # ========================================================
    # PERSONALITY COMMUNICATION
    # ========================================================

    personality_communication = personality.get(
        "communication"
    )

    if personality_communication:

        behaviour_guidance.append(
            str(
                personality_communication
            )
        )

    # ========================================================
    # NON-NEGOTIABLE INVARIANT
    # ========================================================

    behaviour_guidance.append(
        "Dynamic state changes how openly and comfortably you "
        "communicate, but it must never change the client's "
        "established personality or clinical facts."
    )

    # ========================================================
    # RETURN PROFILE
    # ========================================================

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

        "risk_sensitivity": risk_sensitivity,

    }