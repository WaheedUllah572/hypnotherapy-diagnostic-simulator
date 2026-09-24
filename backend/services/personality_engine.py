"""
Personality Engine

This engine defines each client's stable personality.

IMPORTANT:

The personality NEVER changes.

Treatment approach changes HOW the client communicates.

Conversation state changes HOW OPEN the client is.

Clinical facts NEVER change.

This engine does not generate responses and does not determine
clinical information.
"""

from copy import deepcopy
from typing import Any, Dict


# ============================================================
# STABLE CLIENT PERSONALITIES
# ============================================================

PERSONALITIES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # CLAIRE
    # --------------------------------------------------------

    "Claire": {

        "baseline_style": "analytical",

        "emotional_expression": "moderate",

        "talkativeness": "medium",

        "openness": "medium",

        "reflection": "high",

        "vocabulary": "precise and thoughtful",

        "sentence_style": "longer structured sentences",

        "confidence": "confident",

        "social_style": "polite and slightly formal",

        "communication": (
            "Claire naturally analyses situations carefully. "
            "She organises her thoughts before speaking and "
            "explains experiences step by step."
        ),

        "never_becomes": (
            "Even when trust is high, Claire remains analytical "
            "and organised. She does not become impulsive or "
            "overly emotional."
        ),
    },

    # --------------------------------------------------------
    # DANIEL
    # --------------------------------------------------------

    "Daniel": {

        "baseline_style": "optimistic",

        "emotional_expression": "moderate",

        "talkativeness": "medium",

        "openness": "high",

        "reflection": "medium",

        "vocabulary": "simple and practical",

        "sentence_style": "short to medium sentences",

        "confidence": "confident",

        "social_style": "friendly and relaxed",

        "communication": (
            "Daniel speaks in a straightforward conversational "
            "way. He focuses more on practical experiences than "
            "analysing emotions."
        ),

        "never_becomes": (
            "Even when distressed, Daniel remains practical and "
            "approachable. He does not become overly analytical "
            "or formal."
        ),
    },

    # --------------------------------------------------------
    # SOPHIE
    # --------------------------------------------------------

    "Sophie": {

        "baseline_style": "reflective",

        "emotional_expression": "high",

        "talkativeness": "medium",

        "openness": "guarded",

        "reflection": "high",

        "vocabulary": "gentle and emotional",

        "sentence_style": "hesitant with occasional pauses",

        "confidence": "low",

        "social_style": "shy but polite",

        "communication": (
            "Sophie thinks carefully before answering. "
            "She becomes more expressive as trust develops "
            "but remains gentle and reflective."
        ),

        "never_becomes": (
            "Even when trust is high, Sophie remains gentle "
            "and thoughtful. She never becomes loud, blunt "
            "or overly confident."
        ),
    },

    # --------------------------------------------------------
    # MARK
    # --------------------------------------------------------

    "Mark": {

        "baseline_style": "guarded",

        "emotional_expression": "low",

        "talkativeness": "short",

        "openness": "low",

        "reflection": "medium",

        "vocabulary": "brief and direct",

        "sentence_style": "short sentences",

        "confidence": "guarded",

        "social_style": "reserved",

        "communication": (
            "Mark prefers short direct answers. "
            "He rarely volunteers information and only becomes "
            "more open after trust develops."
        ),

        "never_becomes": (
            "Even after building trust, Mark remains naturally "
            "reserved. He becomes slightly more open but never "
            "overly talkative."
        ),
    },
}


# ============================================================
# DEFAULT PERSONALITY
# ============================================================

DEFAULT_PERSONALITY: Dict[str, Any] = {

    "baseline_style": "neutral",

    "emotional_expression": "moderate",

    "talkativeness": "medium",

    "openness": "medium",

    "reflection": "medium",

    "vocabulary": "natural",

    "sentence_style": "medium length",

    "confidence": "moderate",

    "social_style": "neutral",

    "communication": (
        "Speak naturally using a balanced conversational style. "
        "Remain consistent throughout the session."
    ),

    "never_becomes": (
        "Remain consistent with your underlying personality "
        "throughout the consultation."
    ),
}


# ============================================================
# CLIENT NAME NORMALISATION
# ============================================================

def _normalise_client_name(
    client_name: Any,
) -> str:
    """
    Normalize a client name without changing its identity.
    """

    if not isinstance(
        client_name,
        str,
    ):
        return ""

    return client_name.strip()


# ============================================================
# GET PERSONALITY
# ============================================================

def get_personality(
    client_name: str,
) -> Dict[str, Any]:
    """
    Return a copy of the client's stable personality profile.

    A copy is returned so callers cannot accidentally modify the
    global personality definitions.
    """

    name = _normalise_client_name(
        client_name
    )

    personality = PERSONALITIES.get(
        name,
        DEFAULT_PERSONALITY,
    )

    return deepcopy(
        personality
    )


# ============================================================
# CHECK CLIENT
# ============================================================

def has_personality(
    client_name: str,
) -> bool:
    """
    Check whether a named client has an authored personality.
    """

    name = _normalise_client_name(
        client_name
    )

    return name in PERSONALITIES


# ============================================================
# GET SUPPORTED CLIENTS
# ============================================================

def get_supported_clients():
    """
    Return the names of clients with authored personalities.
    """

    return list(
        PERSONALITIES.keys()
    )