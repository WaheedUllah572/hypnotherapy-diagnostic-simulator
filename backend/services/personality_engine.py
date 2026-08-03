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

        "communication": (
            "Claire naturally analyses situations carefully. "
            "She often explains her thoughts logically and is comfortable reflecting on them."
        )
    },

    "Daniel": {

        "baseline_style": "optimistic",

        "emotional_expression": "moderate",

        "talkativeness": "medium",

        "openness": "high",

        "reflection": "medium",

        "communication": (
            "Daniel is naturally approachable and cooperative. "
            "He generally speaks openly and responds positively to supportive questions."
        )
    },

    "Sophie": {

        "baseline_style": "reflective",

        "emotional_expression": "high",

        "talkativeness": "medium",

        "openness": "guarded",

        "reflection": "high",

        "communication": (
            "Sophie tends to think carefully before answering. "
            "She expresses emotion gently and often reflects on her experiences."
        )
    },

    "Mark": {

        "baseline_style": "guarded",

        "emotional_expression": "low",

        "talkativeness": "short",

        "openness": "low",

        "reflection": "medium",

        "communication": (
            "Mark is naturally reserved. "
            "He answers cautiously and takes longer to trust the therapist."
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
            "communication": (
                "Respond naturally."
            )
        }

    )