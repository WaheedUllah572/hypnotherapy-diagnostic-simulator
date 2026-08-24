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

            # ============================
            # MODALITY / BEHAVIOUR
            # ============================
            "behaviour_explored": False,
            "behaviour_question_count": 0,
            "behaviour_topic_progress": 0,
            "last_behaviour_question": None,
            "student_changed_tack": False,
            "client_has_given_behaviour_clue": False,

            # ============================
            # STRESS INDICATOR
            # ============================
            "stress_indicator": False,

            "last_question_type": None,

            "good_responses": 0,
            "poor_responses": 0,

            "response_history": [],

            "clarification_count": 0,
            "last_student_question": None,
            "last_client_understood": True,
        }
def is_behaviour_question(text):

    text = text.lower().strip()

    behaviour_patterns = [
        "what do you do to relax",
        "what helps you relax",
        "how do you relax",
        "what did you used to do to relax",
        "what do you enjoy",
        "what hobbies",
        "what are your hobbies",
        "what do you enjoy outside work",
        "what do you enjoy outside of work",
        "what do you like doing",
        "what do you do for fun",
        "how do you spend your free time",
        "how do you spend your spare time",
        "how do you spend your downtime",
        "what do you do when you're not working",
        "what do you do when you are not working",
        "what do you do outside work",
        "what do you do outside of work",
        "how do you unwind",
        "what helps you switch off"
    ]

    return any(
        pattern in text
        for pattern in behaviour_patterns
    )

# ============================
# STATE UPDATE
# ============================
def update_state(session_id, student_text):

    init_session_state(session_id)

    text = student_text.lower().strip()

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

        state["trust"] += 4
        state["engagement"] += 3
        state["distress"] -= 2
        state["good_responses"] += 1

    # ============================
    # REFLECTION
    # ============================
    if any(x in text for x in [
        "it sounds like",
        "what i'm hearing",
        "so you're saying",
        "it seems like",
        "if i understand correctly"
    ]):

        state["trust"] += 4
        state["resistance"] -= 2
        state["good_responses"] += 1

    # ============================
    # VALIDATION
    # ============================
    if any(x in text for x in [
        "thank you for sharing",
        "i appreciate you sharing",
        "thank you for telling me",
        "that sounds really difficult",
        "that must have been hard",
        "i can understand why"
    ]):

        state["trust"] += 4
        state["distress"] -= 2
        state["good_responses"] += 1

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

        state["resistance"] += 5
        state["trust"] -= 4
        state["poor_responses"] += 1

    # ============================
    # GOOD EXPLORATORY QUESTIONS
    # ============================
    if any(x in text for x in [
        "how do you feel",
        "how have you been feeling",
        "can you tell me more",
        "could you tell me more",
        "what does that feel like",
        "can you describe",
        "how has",
        "affected your life",
        "affected your day",
        "affected your daily life",
        "how has this affected",
        "what effect has this had",
        "impact",
        "how is this affecting",
        "what happens when",
        "what usually happens",
        "could you explain",
        "help me understand"
    ]):

        state["engagement"] += 3
        state["trust"] += 2
        state["good_responses"] += 1

        # ============================
    # MODALITY / BEHAVIOURAL RULE
    # ============================
    if is_behaviour_question(text):

        previous_question = state.get(
            "last_behaviour_question"
        )

        state["behaviour_explored"] = True
        state["behaviour_question_count"] += 1
        state["engagement"] += 1

        # --------------------------------
        # Detect whether student changed tack
        # --------------------------------
        if previous_question:

            if text != previous_question:

                state["student_changed_tack"] = True
                state["behaviour_topic_progress"] += 1

        # --------------------------------
        # Track the latest behaviour question
        # --------------------------------
        state["last_behaviour_question"] = text
        state["last_student_question"] = text

        # --------------------------------
        # Behavioural exploration progress
        # --------------------------------
        if any(x in text for x in [
            "used to",
            "what did you",
            "what do you enjoy",
            "what hobbies",
            "what do you like doing",
            "what do you do for fun",
            "how do you spend your free time",
            "how do you spend your spare time",
            "how do you spend your downtime",
            "when you're not working",
            "when you are not working",
            "outside work",
            "outside of work"
        ]):

            state["client_has_given_behaviour_clue"] = True
            state["behaviour_topic_progress"] += 1

        # --------------------------------
        # STRESS INDICATOR RECOGNITION
        # --------------------------------
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
    # QUESTION STYLE
    # ============================
    if text.startswith((
        "do ",
        "did ",
        "are ",
        "is ",
        "have ",
        "has ",
        "can ",
        "will "
    )):

        if state["last_question_type"] == "closed":
            state["engagement"] -= 3
            state["resistance"] += 2

        state["last_question_type"] = "closed"

    else:

        state["last_question_type"] = "open"

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
        "began",
        "when did this begin",
"when did this first happen",
"when did you notice",
"how long has this been happening",
"since when",
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
"have you ever experienced",
"have you had anything similar",
"anything like this before",
"does this remind you",
"first remember",
"has this happened before",
"have you had treatment",
"have you received treatment",
"medication",
"therapy before"
    ]):
        return "past"

    elif any(x in text for x in [
    "goal",
    "what would you like",
    "what are you hoping",
    "what would be different",
    "what would success",
    "what outcome",
    "if therapy were successful",
    "if therapy was successful",
    "what would you like to achieve",
    "what would you hope",
    "what would improve",
    "six months",
    "future"
]):
        return "goal"

    elif any(x in text for x in [
        "hypnosis",
"hypnotherapy",
"hypnotised",
"hypnotized",
"concerns about hypnosis",
"questions about hypnosis",
"worried about hypnosis",
"how do you feel about hypnosis",
"what are your thoughts about hypnosis",
"any concerns about hypnotherapy"
    ]):
        return "hypnosis_question"

    return None