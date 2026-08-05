"""
Personality Engine

This engine defines each client's stable personality.

The personality NEVER changes.

Treatment approach changes HOW the client communicates.

Conversation state changes HOW OPEN the client is.

Clinical facts NEVER change.
"""

PERSONALITIES = {

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
    "She organises her thoughts before speaking and explains experiences step by step."
)
    },

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
    "Daniel speaks in a straightforward conversational way. "
    "He focuses more on practical experiences than analysing emotions."
)
    },

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
    "She becomes more expressive as trust develops but remains gentle and reflective."
)
    },

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
    "He rarely volunteers information and only becomes more open after trust develops."
)
    }

}


def get_personality(client_name: str):

    return PERSONALITIES.get(

        client_name,

        {
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
    )
}

    )