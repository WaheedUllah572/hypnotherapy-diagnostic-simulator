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


# ============================
# SESSION INITIALIZATION
# ============================
def init_session_state(session_id):

    if session_id not in session_state:

        session_state[session_id] = {
            "trust": 50,
            "distress": 30,
            "engagement": 50,
            "resistance": 20,
            "risk_flag": "none",

            # ✅ REQUIRED FOR MODALITY RULE
            "behaviour_explored": False,

            # ✅ REQUIRED FOR STRESS INDICATOR
            "stress_indicator": False
        }


# ============================
# STATE UPDATE
# ============================
def update_state(session_id, student_text):

    init_session_state(session_id)

    text = student_text.lower()

    state = session_state[session_id]

    # ============================
    # EMPATHY / SUPPORT
    # ============================
    if any(x in text for x in [
        "i understand",
        "that sounds",
        "i hear you",
        "you’re safe",
        "you're safe",
        "i'm here",
        "i am here",
        "we can work through this",
        "it's okay",
        "that must be difficult"
    ]):

        state["trust"] += 10
        state["engagement"] += 5
        state["distress"] -= 5

    # ============================
    # POOR THERAPEUTIC RESPONSES
    # ============================
    if any(x in text for x in [
        "just relax",
        "don't worry",
        "calm down",
        "it's nothing",
        "you'll be fine"
    ]):

        state["resistance"] += 15
        state["trust"] -= 10

    # ============================
    # GOOD EXPLORATORY QUESTIONS
    # ============================
    if any(x in text for x in [
        "how do you feel",
        "can you tell me more",
        "what does that feel like",
        "can you describe",
        "how has that affected you"
    ]):

        state["engagement"] += 5
        state["trust"] += 5

    # ============================
    # MODALITY / BEHAVIOURAL RULE
    # ============================
    if any(x in text for x in [
        "what do you do to relax",
        "what helps you relax",
        "what do you enjoy",
        "what do you do for fun",
        "how do you switch off",
        "downtime",
        "spare time",
        "hobbies"
    ]):

        state["behaviour_explored"] = True

    # ============================
    # STRESS INDICATOR RECOGNITION
    # ============================
    if any(x in text for x in [
        "used to",
        "stress",
        "overwhelmed",
        "impact",
        "affecting",
        "return to",
        "begin again"
    ]):

        state["stress_indicator"] = True

    # ============================
    # RISK DETECTION
    # ============================
    if any(x in text for x in [
        "suicide",
        "can't go on",
        "give up"
    ]):

        state["risk_flag"] = "moderate"
        state["distress"] += 20
        state["trust"] -= 10

    # ============================
    # CLAMP VALUES
    # ============================
    for k in [
        "trust",
        "distress",
        "engagement",
        "resistance"
    ]:

        state[k] = max(
            0,
            min(100, state[k])
        )

    return state


# ============================
# GET STATE
# ============================
def get_state(session_id):

    init_session_state(session_id)

    return session_state[session_id]


# ============================
# GET STAGE
# ============================
def get_stage(session_id):

    if session_id not in session_stages:
        session_stages[session_id] = 0

    return stages_order[
        session_stages[session_id]
    ]


# ============================
# ADVANCE STAGE
# ============================
def advance_stage(session_id):

    if session_id in session_stages:

        if session_stages[session_id] < len(stages_order) - 1:
            session_stages[session_id] += 1


# ============================
# STAGE DETECTION
# ============================
def detect_stage_from_question(text):

    text = text.lower()

    if any(x in text for x in [
        "hello",
        "hi",
        "how can i help"
    ]):
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