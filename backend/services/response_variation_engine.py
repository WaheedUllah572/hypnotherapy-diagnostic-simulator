"""
Response Variation Engine

This engine determines HOW the client should communicate.

It never changes clinical facts.

It only adjusts behavioural communication based on:

- trust
- distress
- resistance
- treatment approach

The returned profile is consumed by the Dynamic Behaviour
Controller and Prompt Builder.
"""

from typing import Any, Dict


# ============================================================
# HELPERS
# ============================================================

def _clamp(
    value: Any,
    minimum: int = 0,
    maximum: int = 100,
) -> int:
    """
    Safely convert a value to an integer between 0 and 100.
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


def _normalise_treatment(
    treatment_approach: Any,
) -> str:
    """
    Normalize the treatment approach key.

    This function only normalizes the value.
    It does not determine clinical suitability.
    """

    if not isinstance(
        treatment_approach,
        str,
    ):
        return ""

    treatment = (
        treatment_approach
        .strip()
        .lower()
    )

    aliases = {
        "cbh": "cbh",
        "cognitive behavioural hypnotherapy": "cbh",
        "cognitive behavioral hypnotherapy": "cbh",

        "sh": "solution_focused",
        "solution focused": "solution_focused",
        "solution-focused": "solution_focused",
        "solution focused hypnotherapy": "solution_focused",
        "solution-focused hypnotherapy": "solution_focused",

        "regression": "regression",
        "regression hypnotherapy": "regression",

        "ericksonian": "ericksonian",
        "ericksonian hypnotherapy": "ericksonian",
    }

    return aliases.get(
        treatment,
        treatment,
    )


# ============================================================
# RESPONSE VARIATION
# ============================================================

def get_response_variation(
    trust: int,
    distress: int,
    resistance: int,
    treatment_approach: str,
) -> Dict[str, Any]:
    """
    Build a communication-variation profile.

    IMPORTANT:

    This function changes communication style only.

    It must never be used to:

    - create clinical facts
    - alter symptoms
    - alter history
    - alter goals
    - create safety information
    - create memories
    - change personality
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

    treatment = _normalise_treatment(
        treatment_approach
    )

    # ========================================================
    # RESPONSE LENGTH
    # ========================================================

    # Resistance has priority because a highly resistant client
    # should not suddenly become extremely verbose merely because
    # trust is high.

    if resistance >= 70:

        response_length = "very_short"

    elif resistance >= 45:

        response_length = "short"

    elif trust >= 85:

        response_length = "very_long"

    elif trust >= 70:

        response_length = "long"

    else:

        response_length = "medium"

    # ========================================================
    # OPENNESS
    # ========================================================

    if resistance >= 70:

        openness = "guarded"

    elif trust >= 80:

        openness = "very_open"

    elif trust >= 60:

        openness = "open"

    else:

        openness = "neutral"

    # ========================================================
    # HESITATION
    # ========================================================

    # High resistance takes priority over emotional distress.

    if resistance >= 70:

        hesitation = "very_high"

    elif distress >= 75:

        hesitation = "high"

    elif distress >= 50:

        hesitation = "medium"

    else:

        hesitation = "low"

    # ========================================================
    # EMOTIONAL DEPTH
    # ========================================================

    if distress >= 80:

        emotional_depth = "deep"

    elif distress >= 55:

        emotional_depth = "moderate"

    else:

        emotional_depth = "light"

    # ========================================================
    # DEFAULT THERAPEUTIC COMMUNICATION
    # ========================================================

    reflection = "medium"
    future_focus = "medium"
    past_focus = "medium"

    # ========================================================
    # TREATMENT APPROACH MODIFIERS
    # ========================================================

    if treatment == "cbh":

        reflection = "high"
        future_focus = "low"
        past_focus = "low"

    elif treatment == "solution_focused":

        reflection = "medium"
        future_focus = "high"
        past_focus = "low"

    elif treatment == "regression":

        reflection = "high"
        future_focus = "low"
        past_focus = "high"

    elif treatment == "ericksonian":

        reflection = "high"
        future_focus = "medium"
        past_focus = "medium"

    # ========================================================
    # CONVERSATIONAL STYLE
    # ========================================================

    # Highly resistant behaviour should remain guarded even if
    # distress is also high.

    if resistance >= 70:

        conversational_style = "guarded"

    elif trust >= 80 and resistance < 30:

        conversational_style = "warm"

    elif distress >= 75:

        conversational_style = "emotional"

    else:

        conversational_style = "neutral"

    # ========================================================
    # RETURN PROFILE
    # ========================================================

    return {

        "response_length": response_length,

        "openness": openness,

        "hesitation": hesitation,

        "emotional_depth": emotional_depth,

        "reflection": reflection,

        "future_focus": future_focus,

        "past_focus": past_focus,

        "conversational_style": conversational_style,

        "natural_variation": True,

    }