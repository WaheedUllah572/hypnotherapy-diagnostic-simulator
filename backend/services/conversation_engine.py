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
    "how do you relax",
    "what do you enjoy",
    "what do you enjoy outside work",
    "what do you enjoy outside of work",
    "what do you like doing",
    "what do you do for fun",
    "how do you switch off",
    "downtime",
    "free time",
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
    "self harm",
    "harm yourself",
    "hurt yourself",
    "ending your life",
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
def set_stage(session_id, stage):

    if stage in stages_order:
        session_stages[session_id] = stages_order.index(stage)


# ============================
# STAGE DETECTION
# ============================
def detect_stage_from_question(text):

    text = text.lower()

    if any(x in text for x in [
        "hello",
        "hi",
        "how can i help",
        "what brings",
        "what brought you",
        "what brings you here",
        "what made you seek",
        "what would you like to talk about",
        "how can i support you"
    ]):
        return "presenting_problem"

    elif any(x in text for x in [
        "when did",
        "when did it start",
        "when did this start",
        "when did you first",
        "how long",
        "first notice",
        "first begin",
        "started",
        "began"
    ]):
        return "timeline"

    elif any(x in text for x in [
        "what do you think",
        "what goes through your mind",
        "what was going through your mind",
        "what were you thinking",
        "thoughts",
        "mind"
    ]):
        return "thoughts"

    elif any(x in text for x in [
        "how do you feel",
        "how did you feel",
        "emotionally",
        "what was that like emotionally",
        "how does that make you feel",
        "feel inside"
    ]):
        return "feelings"

    elif any(x in text for x in [
        "body",
        "physical",
        "physically",
        "what happens physically",
        "heart",
        "breathing",
        "chest",
        "tension"
    ]):
        return "body"

    elif any(x in text for x in [
        "past",
        "before",
        "earlier",
        "previously",
        "have you experienced",
        "does this remind you",
        "first remember"
    ]):
        return "past"

    elif any(x in text for x in [
        "goal",
        "what would you like",
        "what are you hoping",
        "what would be different",
        "what would success",
        "six months",
        "future"
    ]):
        return "goal"

    elif any(x in text for x in [
        "hypnosis",
        "hypnotherapy",
        "concerns about hypnosis",
        "questions about hypnosis",
        "worried about hypnosis"
    ]):
        return "hypnosis_question"

    return None