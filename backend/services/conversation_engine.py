"""
Conversation Engine

Responsible for:

- session state
- assessment stage
- therapist interaction state
- behavioural-question tracking
- trust / distress / engagement / resistance

IMPORTANT:

This engine tracks the therapist's interaction with the client.

It does NOT determine clinical risk from therapist questions.

Clinical risk must be established from the client's actual response
and handled by the clinical evidence / safety engines.
"""

from typing import Optional


# ============================================================
# SESSION STORAGE
# ============================================================

session_stages = {}
session_state = {}


# ============================================================
# ASSESSMENT STAGES
# ============================================================

stages_order = [
    "presenting_problem",
    "timeline",
    "thoughts",
    "feelings",
    "body",
    "past",
    "goal",
    "hypnosis_question",
]


# ============================================================
# TEXT NORMALISATION
# ============================================================

def _normalise_text(
    text: Optional[str]
) -> str:

    if text is None:
        return ""

    return (
        str(text)
        .strip()
        .lower()
    )


# ============================================================
# SESSION INITIALIZATION
# ============================================================

def init_session_state(
    session_id: str
):

    if session_id not in session_state:

        session_state[session_id] = {

            # ------------------------------------------------
            # CORE CONVERSATION STATE
            # ------------------------------------------------

            "trust": 50,

            "distress": 30,

            "engagement": 50,

            "resistance": 20,

            # IMPORTANT:
            #
            # This value is NOT changed merely because a therapist
            # asks a safety question.
            #
            # Actual clinical risk is handled by the evidence /
            # safety engines.
            "risk_flag": "none",

            # ------------------------------------------------
            # BEHAVIOURAL EXPLORATION
            # ------------------------------------------------

            "behaviour_explored": False,

            "behaviour_question_count": 0,

            "behaviour_topic_progress": 0,

            "last_behaviour_question": None,

            "student_changed_tack": False,

            # IMPORTANT:
            #
            # This means that the client actually provided some
            # behavioural information.
            #
            # Asking a behavioural question does NOT set this True.
            "client_has_given_behaviour_clue": False,

            # ------------------------------------------------
            # STRESS INDICATOR
            # ------------------------------------------------

            "stress_indicator": False,

            # ------------------------------------------------
            # QUESTION STYLE
            # ------------------------------------------------

            "last_question_type": None,

            # ------------------------------------------------
            # RESPONSE QUALITY
            # ------------------------------------------------

            "good_responses": 0,

            "poor_responses": 0,

            # ------------------------------------------------
            # RESPONSE HISTORY
            # ------------------------------------------------

            "response_history": [],

            # ------------------------------------------------
            # CLARIFICATION
            # ------------------------------------------------

            "clarification_count": 0,

            "last_student_question": None,

            "last_client_understood": True,
        }


# ============================================================
# BEHAVIOURAL QUESTION DETECTION
# ============================================================

def is_behaviour_question(
    text: str
) -> bool:

    text = _normalise_text(
        text
    )

    if not text:
        return False

    behaviour_patterns = [

        # ----------------------------------------------------
        # RELAXATION
        # ----------------------------------------------------

        "what do you do to relax",

        "what do you usually do to relax",

        "what helps you relax",

        "how do you relax",

        "what did you used to do to relax",

        "what did you use to do to relax",

        "how do you unwind",

        "what helps you unwind",

        "what do you do to unwind",

        # ----------------------------------------------------
        # HOBBIES / ENJOYMENT
        # ----------------------------------------------------

        "what do you enjoy",

        "what do you enjoy doing",

        "what hobbies",

        "what are your hobbies",

        "what do you like doing",

        "what do you like to do",

        "what do you do for fun",

        "what do you do for enjoyment",

        "what activities do you enjoy",

        # ----------------------------------------------------
        # FREE / SPARE TIME
        # ----------------------------------------------------

        "how do you spend your free time",

        "what do you do in your free time",

        "how do you spend your spare time",

        "what do you do in your spare time",

        "how do you spend your downtime",

        "what do you do in your downtime",

        # ----------------------------------------------------
        # OUTSIDE WORK
        # ----------------------------------------------------

        "what do you enjoy outside work",

        "what do you enjoy outside of work",

        "what do you do when you're not working",

        "what do you do when you are not working",

        "what do you usually do when you're not working",

        "what do you usually do when you are not working",

        "what do you do outside work",

        "what do you do outside of work",

        # ----------------------------------------------------
        # SWITCHING OFF
        # ----------------------------------------------------

        "how do you switch off",

        "what helps you switch off",

        "what do you do to switch off",
    ]

    return any(
        pattern in text
        for pattern in behaviour_patterns
    )


# ============================================================
# QUESTION TYPE
# ============================================================

def _is_closed_question(
    text: str
) -> bool:

    text = _normalise_text(
        text
    )

    if not text:
        return False

    return text.startswith(
        (
            "do ",
            "did ",
            "are ",
            "is ",
            "was ",
            "were ",
            "have ",
            "has ",
            "had ",
            "can ",
            "could ",
            "will ",
            "would ",
            "should ",
            "didn't ",
            "don't ",
            "does ",
            "doesn't ",
        )
    )


# ============================================================
# EMPATHY / SUPPORT DETECTION
# ============================================================

def _contains_empathy(
    text: str
) -> bool:

    return any(
        phrase in text
        for phrase in [

            "i understand",

            "that sounds",

            "i hear you",

            "you're safe",

            "you’re safe",

            "i'm here",

            "i’m here",

            "i am here",

            "we can work through this",

            "it's okay",

            "it’s okay",

            "that must be difficult",

            "that sounds difficult",
        ]
    )


# ============================================================
# REFLECTION DETECTION
# ============================================================

def _contains_reflection(
    text: str
) -> bool:

    return any(
        phrase in text
        for phrase in [

            "it sounds like",

            "what i'm hearing",

            "what i’m hearing",

            "so you're saying",

            "so you’re saying",

            "it seems like",

            "if i understand correctly",

            "if i've understood correctly",

            "if i’ve understood correctly",
        ]
    )


# ============================================================
# VALIDATION DETECTION
# ============================================================

def _contains_validation(
    text: str
) -> bool:

    return any(
        phrase in text
        for phrase in [

            "thank you for sharing",

            "i appreciate you sharing",

            "thank you for telling me",

            "that sounds really difficult",

            "that must have been hard",

            "i can understand why",

            "i can see why that would be difficult",
        ]
    )


# ============================================================
# POOR THERAPEUTIC RESPONSE DETECTION
# ============================================================

def _contains_poor_response(
    text: str
) -> bool:

    return any(
        phrase in text
        for phrase in [

            "just relax",

            "don't worry",

            "don’t worry",

            "calm down",

            "it's nothing",

            "it’s nothing",

            "you'll be fine",

            "you’ll be fine",

            "just stop worrying",

        ]
    )


# ============================================================
# EXPLORATORY QUESTION DETECTION
# ============================================================

def _contains_exploration(
    text: str
) -> bool:

    return any(
        phrase in text
        for phrase in [

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

            "what impact has this had",

            "impact",

            "how is this affecting",

            "what happens when",

            "what usually happens",

            "could you explain",

            "help me understand",

            "can you explain",

            "tell me more about",
        ]
    )


# ============================================================
# STRESS INDICATOR — THERAPIST QUESTION
# ============================================================

def _contains_stress_exploration(
    text: str
) -> bool:

    return any(
        phrase in text
        for phrase in [

            "used to",

            "what did you use to do",

            "what did you used to do",

            "what do you enjoy",

            "what hobbies",

            "what do you do for fun",

            "what do you do in your free time",

            "what do you do in your spare time",

            "what do you do outside work",

            "what do you do outside of work",

            "what do you do when you're not working",

            "what do you do when you are not working",
        ]
    )


# ============================================================
# STATE UPDATE
# ============================================================

def update_state(
    session_id: str,
    student_text: str
):

    init_session_state(
        session_id
    )

    text = _normalise_text(
        student_text
    )

    state = session_state[
        session_id
    ]

    if not text:
        return state

    # ========================================================
    # STORE QUESTION
    # ========================================================

    state[
        "last_student_question"
    ] = student_text

    # ========================================================
    # EMPATHY / SUPPORT
    # ========================================================

    if _contains_empathy(
        text
    ):

        state["trust"] += 4

        state["engagement"] += 3

        state["distress"] -= 2

        state["good_responses"] += 1

    # ========================================================
    # REFLECTION
    # ========================================================

    if _contains_reflection(
        text
    ):

        state["trust"] += 4

        state["resistance"] -= 2

        state["good_responses"] += 1

    # ========================================================
    # VALIDATION
    # ========================================================

    if _contains_validation(
        text
    ):

        state["trust"] += 4

        state["distress"] -= 2

        state["good_responses"] += 1

    # ========================================================
    # POOR THERAPEUTIC RESPONSE
    # ========================================================

    if _contains_poor_response(
        text
    ):

        state["resistance"] += 5

        state["trust"] -= 4

        state["poor_responses"] += 1

    # ========================================================
    # GOOD EXPLORATORY QUESTIONS
    # ========================================================

    if _contains_exploration(
        text
    ):

        state["engagement"] += 3

        state["trust"] += 2

        state["good_responses"] += 1

    # ========================================================
    # BEHAVIOURAL QUESTION
    # ========================================================

    if is_behaviour_question(
        text
    ):

        previous_question = (
            state.get(
                "last_behaviour_question"
            )
        )

        state[
            "behaviour_explored"
        ] = True

        state[
            "behaviour_question_count"
        ] += 1

        state[
            "engagement"
        ] += 1

        # ----------------------------------------------------
        # Detect a change of behavioural question
        # ----------------------------------------------------

        if previous_question:

            if text != previous_question:

                state[
                    "student_changed_tack"
                ] = True

                state[
                    "behaviour_topic_progress"
                ] += 1

        # ----------------------------------------------------
        # Store latest behavioural question
        # ----------------------------------------------------

        state[
            "last_behaviour_question"
        ] = text

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT set:
        #
        # client_has_given_behaviour_clue = True
        #
        # merely because the therapist asked a question.
        #
        # The client answer is processed separately.
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Behavioural exploration progress
        # ----------------------------------------------------

        if _contains_stress_exploration(
            text
        ):

            state[
                "stress_indicator"
            ] = True

    # ========================================================
    # RISK
    # ========================================================
    #
    # IMPORTANT:
    #
    # We deliberately DO NOT infer clinical risk from the
    # therapist's question.
    #
    # Example:
    #
    # Therapist:
    # "Have you ever had thoughts of harming yourself?"
    #
    # This is a safety question, not evidence of risk.
    #
    # Actual risk is determined from the CLIENT'S response by
    # evidence_extractor.py + risk_safety_engine.py.
    #
    # Therefore this section does not modify risk_flag.
    # ========================================================

    # Keep existing state value unchanged.
    state[
        "risk_flag"
    ] = state.get(
        "risk_flag",
        "none"
    )

    # ========================================================
    # QUESTION STYLE
    # ========================================================

    current_question_type = (
        "closed"
        if _is_closed_question(text)
        else "open"
    )

    if (
        current_question_type == "closed"
        and state.get(
            "last_question_type"
        ) == "closed"
    ):

        state["engagement"] -= 3

        state["resistance"] += 2

    state[
        "last_question_type"
    ] = current_question_type

    # ========================================================
    # RESPONSE HISTORY
    # ========================================================

    response_history = state.get(
        "response_history",
        []
    )

    response_history.append({

        "student_text":
            student_text,

        "question_type":
            current_question_type,

        "behaviour_question":
            is_behaviour_question(
                text
            ),

        "good_response":
            (
                _contains_empathy(text)
                or
                _contains_reflection(text)
                or
                _contains_validation(text)
                or
                _contains_exploration(text)
            ),

        "poor_response":
            _contains_poor_response(
                text
            )
    })

    # Keep the in-memory history bounded.
    if len(
        response_history
    ) > 50:

        response_history = (
            response_history[-50:]
        )

    state[
        "response_history"
    ] = response_history

    # ========================================================
    # CLAMP VALUES
    # ========================================================

    for key in [

        "trust",

        "distress",

        "engagement",

        "resistance",
    ]:

        state[key] = max(
            0,
            min(
                100,
                int(
                    state.get(
                        key,
                        0
                    )
                )
            )
        )

    return state


# ============================================================
# RECORD CLIENT BEHAVIOURAL EVIDENCE
# ============================================================

def record_client_behavioural_evidence(
    session_id: str,
    client_response: str
):
    """
    Record that the CLIENT actually supplied behavioural
    information.

    This is intentionally separate from update_state().

    A therapist question is not evidence that the client has
    provided a behavioural clue.
    """

    init_session_state(
        session_id
    )

    text = _normalise_text(
        client_response
    )

    if not text:
        return session_state[
            session_id
        ]

    state = session_state[
        session_id
    ]

    # --------------------------------------------------------
    # Only mark a behavioural clue when the client actually
    # provides meaningful behavioural information.
    #
    # We deliberately do NOT treat phrases such as:
    #
    # "I don't know"
    # "nothing specific"
    # "I'm not sure"
    #
    # as positive behavioural information.
    # --------------------------------------------------------

    uncertainty_patterns = [

        "i don't know",

        "i dont know",

        "i'm not sure",

        "im not sure",

        "i am not sure",

        "nothing specific",

        "can't think of anything",

        "cant think of anything",

        "nothing comes to mind",

        "not really",
    ]

    if any(
        phrase in text
        for phrase in uncertainty_patterns
    ):

        return state

    # --------------------------------------------------------
    # A meaningful client answer can now be recorded.
    #
    # This is deliberately broad because the evidence extractor
    # remains responsible for deciding the clinical meaning.
    # --------------------------------------------------------

    state[
        "client_has_given_behaviour_clue"
    ] = True

    state[
        "behaviour_topic_progress"
    ] += 1

    return state


# ============================================================
# RECORD CLIENT UNDERSTANDING
# ============================================================

def record_client_understanding(
    session_id: str,
    understood: bool
):

    init_session_state(
        session_id
    )

    state = session_state[
        session_id
    ]

    state[
        "last_client_understood"
    ] = bool(
        understood
    )

    if not understood:

        state[
            "clarification_count"
        ] += 1

    return state


# ============================================================
# GET STATE
# ============================================================

def get_state(
    session_id: str
):

    init_session_state(
        session_id
    )

    return session_state[
        session_id
    ]


# ============================================================
# GET STAGE
# ============================================================

def get_stage(
    session_id: str
):

    if session_id not in session_stages:

        session_stages[
            session_id
        ] = 0

    index = session_stages[
        session_id
    ]

    index = max(
        0,
        min(
            index,
            len(stages_order) - 1
        )
    )

    return stages_order[
        index
    ]


# ============================================================
# SET STAGE
# ============================================================

def set_stage(
    session_id: str,
    stage: str
):

    if stage not in stages_order:
        return get_stage(
            session_id
        )

    session_stages[
        session_id
    ] = stages_order.index(
        stage
    )

    return stage


# ============================================================
# STAGE DETECTION
# ============================================================

def detect_stage_from_question(
    text: str
):

    text = _normalise_text(
        text
    )

    if not text:
        return None

    # ========================================================
    # PRESENTING PROBLEM
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "hello",

            "hi",

            "how can i help",

            "what brings you",

            "what brought you",

            "what made you seek",

            "what would you like to talk about",

            "how can i support you",

            "what's brought you here",

            "what's bringing you here",

            "what is bringing you here",

            "what is it that brings you here",
        ]
    ):

        return "presenting_problem"

    # ========================================================
    # TIMELINE
    # ========================================================

    if any(
        phrase in text
        for phrase in [

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

            "how long has this been going on",

            "since when",

            "when did you first notice",
        ]
    ):

        return "timeline"

    # ========================================================
    # THOUGHTS
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "what do you think",

            "what goes through your mind",

            "what was going through your mind",

            "what were you thinking",

            "what are you thinking",

            "what thoughts come up",

            "what thoughts do you have",

            "thoughts",

            "mind",
        ]
    ):

        return "thoughts"

    # ========================================================
    # FEELINGS
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "how do you feel",

            "how did you feel",

            "how have you been feeling",

            "emotionally",

            "what was that like emotionally",

            "how does that make you feel",

            "how does that feel",

            "feel inside",

            "what emotions",

            "what are you feeling",
        ]
    ):

        return "feelings"

    # ========================================================
    # BODY / PHYSICAL
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "what happens physically",

            "what happens in your body",

            "what do you notice physically",

            "what physical symptoms",

            "physical symptoms",

            "physically",

            "body",

            "breathing",

            "heart",

            "chest",

            "tension",

            "sweating",

            "hands",

            "physical sensations",
        ]
    ):

        return "body"

    # ========================================================
    # PAST / HISTORY
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "have you experienced",

            "have you ever experienced",

            "have you had anything similar",

            "anything like this before",

            "does this remind you",

            "when do you first remember",

            "first remember",

            "has this happened before",

            "have you had treatment",

            "have you received treatment",

            "have you had therapy before",

            "have you received therapy",

            "have you had psychological treatment",

            "have you seen a therapist",

            "have you seen a doctor",

            "have you seen a psychiatrist",

            "medication",

            "medical history",

            "psychiatric history",

            "psychological history",

            "safeguarding",

            "self-harm",

            "self harm",

            "suicide",
        ]
    ):

        return "past"

    # ========================================================
    # GOAL
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "what are you hoping",

            "what would you like to achieve",

            "what would you like to change",

            "what would you like to be different",

            "what would be different",

            "what would success look like",

            "what outcome are you hoping for",

            "what outcome would you like",

            "if therapy were successful",

            "if therapy was successful",

            "what would you like to achieve",

            "what would you hope to achieve",

            "what would improve",

            "what do you want to change",

            "what do you want to achieve",

            "what would you like from therapy",

            "what are your goals",

            "what is your goal",

            "six months",

            "in the future",

            "future",
        ]
    ):

        return "goal"

    # ========================================================
    # HYPNOSIS QUESTION
    # ========================================================

    if any(
        phrase in text
        for phrase in [

            "what do you think about hypnosis",

            "how do you feel about hypnosis",

            "what are your thoughts about hypnosis",

            "any concerns about hypnosis",

            "concerns about hypnosis",

            "questions about hypnosis",

            "worried about hypnosis",

            "hypnosis",

            "hypnotherapy",

            "hypnotised",

            "hypnotized",

            "being hypnotised",

            "being hypnotized",
        ]
    ):

        return "hypnosis_question"

    return None