# backend/services/conversation_engine.py

session_stages = {}

stages_order = [
    "presenting_problem",
    "timeline",
    "thoughts",
    "feelings",
    "body",
    "past",
    "goal",
    "hypnosis_question"
]


def get_stage(session_id):
    if session_id not in session_stages:
        session_stages[session_id] = 0
    return stages_order[session_stages[session_id]]


def advance_stage(session_id):
    if session_id in session_stages:
        if session_stages[session_id] < len(stages_order) - 1:
            session_stages[session_id] += 1


def detect_stage_from_question(text):
    text = text.lower()

    if "what brings" in text or "hello" in text:
        return "presenting_problem"
    elif "when did" in text or "how long" in text:
        return "timeline"
    elif "what goes through" in text or "what do you think" in text:
        return "thoughts"
    elif "how do you feel" in text:
        return "feelings"
    elif "body" in text:
        return "body"
    elif "before" in text or "childhood" in text or "past" in text:
        return "past"
    elif "what would you like" in text or "goal" in text:
        return "goal"
    elif "hypnotherapy" in text:
        return "hypnosis_question"
    else:
        return None


# ✅ NEW: CLINICAL RESPONSE CHECK (THIS IS THE KEY FEATURE)
def detect_bad_response(student_text: str):
    text = student_text.lower()

    # ❌ No empathy
    empathy_keywords = ["understand", "that sounds", "i hear", "that must"]
    has_empathy = any(k in text for k in empathy_keywords)

    # ❌ No question / engagement
    asking_question = "?" in text

    # ❌ Inappropriate suggestion (too early)
    bad_suggestions = ["just relax", "you should", "don't worry"]
    inappropriate = any(k in text for k in bad_suggestions)

    if not has_empathy or not asking_question or inappropriate:
        return True

    return False