def evaluate_response(student_text: str, mode: str, chat_history=None):

    text = student_text.lower()

    # ============================
    # QUESTION 1 — APPROACH
    # ============================
    if mode == "approach":

        return any(x in text for x in [
            "cognitive behavioural",
            "cbt",
            "cbh",
            "solution focused",
            "ericksonian",
            "regression"
        ])

    # ============================
    # QUESTION 2 — MODALITY
    # MUST COME FROM BEHAVIOURAL QUESTIONING
    # ============================
    if mode == "modality":

        behavioural_question = False

        if chat_history:

            behavioural_question = any(
                any(x in m["text"].lower() for x in [
                    "relax",
                    "hobbies",
                    "fun",
                    "downtime",
                    "what do you enjoy",
                    "what do you like to do",
                    "how do you switch off",
                    "what helps you relax"
                ])
                for m in chat_history
                if m["role"] == "therapist"
            )

        modality_present = any(x in text for x in [
            "visual",
            "auditory",
            "kinaesthetic"
        ])

        return behavioural_question and modality_present

    # ============================
    # QUESTION 3 — OBJECTIVE
    # ============================
    if mode == "objective":

        return any(x in text for x in [
            "want",
            "goal",
            "reduce",
            "manage",
            "control",
            "cope"
        ])

    # ============================
    # QUESTION 4 — SAFETY + REASSURANCE
    # ============================
    if mode == "safety":

        safety = any(x in text for x in [
            "risk",
            "safety",
            "medical",
            "history",
            "screen",
            "suitability",
            "safe",
            "supported"
        ])

        readiness = any(x in text for x in [
            "ready",
            "proceed",
            "continue",
            "comfortable",
            "move forward",
            "begin"
        ])

        # ============================
        # STRESS INDICATOR CHECK
        # ============================
        stress_handled = any(x in text for x in [
            "used to",
            "stress",
            "affecting",
            "impact",
            "return",
            "again",
            "able to"
        ])

        return safety and readiness and stress_handled

    return False