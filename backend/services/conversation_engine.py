session_stages = {}
session_state = {}

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


def init_session_state(session_id):
    if session_id not in session_state:
        session_state[session_id] = {
            "trust": 50,
            "distress": 30,
            "engagement": 50,
            "resistance": 20,
            "risk_flag": "none"
        }


def update_state(session_id, student_text):
    init_session_state(session_id)
    text = student_text.lower()

    state = session_state[session_id]

    # ✅ STRONGER EMPATHY DETECTION (FIX)
    if any(x in text for x in [
        "i understand",
        "that sounds",
        "i hear you",
        "you’re safe",
        "i'm here",
        "i am here",
        "we can work through this",
        "it's okay"
    ]):
        state["trust"] += 10
        state["engagement"] += 5
        state["distress"] -= 5

    # ✅ BAD / DISMISSIVE RESPONSES (FIX)
    if any(x in text for x in [
        "just relax",
        "don't worry",
        "calm down",
        "it's nothing",
        "you'll be fine"
    ]):
        state["resistance"] += 15
        state["trust"] -= 10

    # ✅ QUESTION QUALITY (NEW MINIMAL FIX)
    if any(x in text for x in [
        "how do you feel",
        "can you tell me more",
        "what does that feel like",
        "can you describe"
    ]):
        state["engagement"] += 5
        state["trust"] += 5

    # ✅ RISK DETECTION (UNCHANGED BUT SLIGHTLY STRONGER)
    if any(x in text for x in ["suicide", "can't go on", "give up"]):
        state["risk_flag"] = "moderate"
        state["distress"] += 20
        state["trust"] -= 10

    # ✅ CLAMP VALUES (UNCHANGED)
    for k in ["trust", "distress", "engagement", "resistance"]:
        state[k] = max(0, min(100, state[k]))

    return state


def get_state(session_id):
    init_session_state(session_id)
    return session_state[session_id]


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

    if any(x in text for x in ["hello", "hi", "how can i help"]):
        return "presenting_problem"
    elif "what brings" in text:
        return "presenting_problem"
    elif "when did" in text:
        return "timeline"
    elif "what do you think" in text:
        return "thoughts"
    elif "how do you feel" in text:
        return "feelings"
    elif "body" in text:
        return "body"
    elif "past" in text:
        return "past"
    elif "goal" in text:
        return "goal"
    elif "hypnotherapy" in text:
        return "hypnosis_question"

    return None