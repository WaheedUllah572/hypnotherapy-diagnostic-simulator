# backend/services/conversation_engine.py

# Track session stages per conversation
session_stages = {}


def get_stage(session_id):
    return session_stages.get(session_id, 1)


def advance_stage(session_id):
    current = session_stages.get(session_id, 1)
    if current < 8:
        session_stages[session_id] = current + 1
    return session_stages[session_id]


def detect_stage_from_question(question):
    q = question.lower()

    if "what brings" in q or "why are you here" in q:
        return 1
    elif "when did" in q or "when did this start" in q:
        return 2
    elif "what do you think" in q or "goes through your mind" in q:
        return 3
    elif "how do you feel" in q:
        return 4
    elif "body" in q or "feel in your body" in q:
        return 5
    elif "past" in q or "before" in q:
        return 6
    elif "what would you like" in q or "goal" in q:
        return 7
    elif "hypnosis" in q:
        return 8
    else:
        return None