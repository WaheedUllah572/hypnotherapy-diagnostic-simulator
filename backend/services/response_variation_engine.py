"""
Response Variation Engine

This engine determines HOW the client should communicate.

It never changes the clinical facts.

It only adjusts the behavioural style of responses based on:

- trust
- distress
- resistance
- treatment approach

The returned profile is consumed by the Persona Engine and
Prompt Builder.
"""


def get_response_variation(
    trust: int,
    distress: int,
    resistance: int,
    treatment_approach: str
):

    # ==========================================
    # RESPONSE LENGTH
    # ==========================================

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

    # ==========================================
    # OPENNESS
    # ==========================================

    if trust >= 80:
        openness = "very_open"

    elif trust >= 60:
        openness = "open"

    elif resistance >= 70:
        openness = "guarded"

    else:
        openness = "neutral"

    # ==========================================
    # HESITATION
    # ==========================================

    if resistance >= 70:
     hesitation = "very_high"

    elif distress >= 75:
     hesitation = "high"

    elif distress >= 50:
     hesitation = "medium"

    else:
      hesitation = "low"

    # ==========================================
    # EMOTIONAL DEPTH
    # ==========================================

    if distress >= 80:
        emotional_depth = "deep"

    elif distress >= 55:
        emotional_depth = "moderate"

    else:
        emotional_depth = "light"

    # ==========================================
    # DEFAULT THERAPY BEHAVIOUR
    # ==========================================

    reflection = "medium"
    future_focus = "medium"
    past_focus = "medium"

    # ==========================================
    # TREATMENT MODIFIERS
    # ==========================================

    treatment = treatment_approach.lower()

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

        # ==========================================
    # CONVERSATIONAL STYLE
    # ==========================================

    if trust >= 80 and resistance < 30:
        conversational_style = "warm"

    elif resistance >= 70:
        conversational_style = "guarded"

    elif distress >= 75:
        conversational_style = "emotional"

    else:
        conversational_style = "neutral"

    # ==========================================
    # RETURN PROFILE
    # ==========================================

    return {

        "response_length": response_length,

        "openness": openness,

        "hesitation": hesitation,

        "emotional_depth": emotional_depth,

        "reflection": reflection,

        "future_focus": future_focus,

        "past_focus": past_focus,

        "natural_variation": True
    }