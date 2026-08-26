# ============================================================
# PROTECTED CLINICAL DOMAINS
# ============================================================

PROTECTED_DOMAINS = {
    "medication": [
        "medication",
        "medicine",
        "medicines",
        "tablets",
        "prescription",
        "prescribed",
        "drug",
    ],

    "psychological_care": [
        "psychologist",
        "psychological care",
        "psychological treatment",
        "psychological support",
        "therapy",
        "therapist",
        "counselling",
        "counseling",
        "counsellor",
        "counselor",
    ],

    "psychiatric_care": [
        "psychiatrist",
        "psychiatric",
        "psychiatric care",
        "psychiatric treatment",
    ],

    "previous_hypnosis": [
        "hypnotherapy",
        "hypnosis",
        "hypnotherapist",
    ],

    "risk": [
        "harm yourself",
        "harm myself",
        "harming yourself",
        "hurt yourself",
        "hurt myself",
        "suicide",
        "suicidal",
        "self harm",
        "self-harm",
        "harm someone else",
        "hurt someone else",
        "thoughts of harming",
        "thoughts of hurting",
        "suicidal thoughts",
        "self-harm thoughts",
        "self harm thoughts",
    ],

    "healthcare_professionals": [
        "healthcare professional",
        "healthcare professionals",
        "doctor",
        "doctors",
        "gp",
        "supporting you medically",
        "medical professional",
        "professional involved",
        "professionals involved",
    ],

    "medical_history": [
        "medical history",
        "medical condition",
        "medical conditions",
        "health condition",
        "health conditions",
        "health problems",
        "medical problems",
        "physical health",
        "health history",
    ],

    "referral_permission": [
        "referral",
        "permission",
        "medical clearance",
        "doctor's permission",
        "doctor permission",
        "gp permission",
        "gp referral",
        "medical approval",
    ],

    "contraindications": [
        "contraindication",
        "contraindications",
        "unsuitable",
        "make hypnosis unsafe",
        "make hypnotherapy unsafe",
        "additional professional advice",
    ],

    "safeguarding": [
        "safeguarding",
        "abuse",
        "being harmed",
        "someone hurting you",
        "safe at home",
        "feel safe at home",
    ],
}


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(question: str):

    question = (question or "").lower().strip()

    # Risk first
    for keyword in PROTECTED_DOMAINS["risk"]:
        if keyword in question:
            return "risk"

    # Safeguarding
    for keyword in PROTECTED_DOMAINS["safeguarding"]:
        if keyword in question:
            return "safeguarding"

    # Contraindications
    for keyword in PROTECTED_DOMAINS["contraindications"]:
        if keyword in question:
            return "contraindications"

    # Medication
    for keyword in PROTECTED_DOMAINS["medication"]:
        if keyword in question:
            return "medication"

    # Previous hypnosis
    for keyword in PROTECTED_DOMAINS["previous_hypnosis"]:
        if keyword in question:
            return "previous_hypnosis"

    # Psychiatric care
    for keyword in PROTECTED_DOMAINS["psychiatric_care"]:
        if keyword in question:
            return "psychiatric_care"

    # Psychological care
    for keyword in PROTECTED_DOMAINS["psychological_care"]:
        if keyword in question:
            return "psychological_care"

    # Referral / permission
    for keyword in PROTECTED_DOMAINS["referral_permission"]:
        if keyword in question:
            return "referral_permission"

    # Healthcare professionals
    for keyword in PROTECTED_DOMAINS["healthcare_professionals"]:
        if keyword in question:
            return "healthcare_professionals"

    # Medical history
    for keyword in PROTECTED_DOMAINS["medical_history"]:
        if keyword in question:
            return "medical_history"

    return None


# ============================================================
# RISK QUESTION TYPE
# ============================================================

def detect_risk_question_type(question: str):
    """
    Distinguish the exact type of risk information being asked.

    This is critical because:
    
    "No self-harm history"

    does NOT establish:

    "No thoughts of harming yourself."
    """

    text = (question or "").lower().strip()

    # --------------------------------------------------------
    # THOUGHTS / IDEATION
    # --------------------------------------------------------

    if any(x in text for x in [
        "thoughts of harming yourself",
        "thoughts of harming myself",
        "thoughts of hurting yourself",
        "thoughts of hurting myself",
        "thought about harming yourself",
        "thought about harming myself",
        "thought about hurting yourself",
        "thought about hurting myself",
        "suicidal thoughts",
        "thoughts of suicide",
        "thought about suicide",
        "thinking about suicide",
        "wanted to die",
        "wanting to die",
    ]):
        return "suicidal_or_self_harm_ideation"

    # --------------------------------------------------------
    # SUICIDE ATTEMPT
    # --------------------------------------------------------

    if any(x in text for x in [
        "suicide attempt",
        "suicide attempts",
        "attempted suicide",
        "tried to kill yourself",
        "tried to kill myself",
    ]):
        return "suicide_attempt"

    # --------------------------------------------------------
    # SELF-HARM ACT / HISTORY
    # --------------------------------------------------------

    if any(x in text for x in [
        "history of self-harm",
        "history of self harm",
        "history of harming yourself",
        "history of hurting yourself",
        "ever harmed yourself",
        "ever harmed myself",
        "ever hurt yourself",
        "ever hurt myself",
        "self-harm history",
        "self harm history",
        "previous self-harm",
        "previous self harm",
    ]):
        return "self_harm_history"

    # --------------------------------------------------------
    # HARM TO OTHERS
    # --------------------------------------------------------

    if any(x in text for x in [
        "thoughts of harming someone",
        "thoughts of harming anyone",
        "thoughts of hurting someone",
        "thoughts of hurting anyone",
        "harm someone else",
        "harm anyone else",
        "hurt someone else",
        "hurt anyone else",
        "violent thoughts",
        "thoughts of violence",
    ]):
        return "harm_to_others"

    # --------------------------------------------------------
    # GENERAL RISK
    # --------------------------------------------------------

    return "general_risk"


# ============================================================
# AUTHORITATIVE VALUE CHECK
# ============================================================

def is_defined(persona: dict, domain: str, question: str = ""):

    healthcare = persona.get("healthcare", {})
    hypnosis = persona.get("hypnosis_history", {})
    safety = persona.get("safety", {})

    # --------------------------------------------------------
    # MEDICATION
    # --------------------------------------------------------

    if domain == "medication":

        medication = healthcare.get("medication", {})

        return (
            medication.get("current") is not None
            and medication.get("current") != ""
        )

    # --------------------------------------------------------
    # PSYCHOLOGICAL CARE
    # --------------------------------------------------------

    if domain == "psychological_care":

        value = healthcare.get("psychological_care")

        return value not in (None, "")

    # --------------------------------------------------------
    # PSYCHIATRIC CARE
    # --------------------------------------------------------

    if domain == "psychiatric_care":

        value = healthcare.get("psychiatric_care")

        return value not in (None, "")

    # --------------------------------------------------------
    # PREVIOUS HYPNOSIS
    # --------------------------------------------------------

    if domain == "previous_hypnosis":

        value = hypnosis.get("previous_experience")

        return value not in (None, "")

    # --------------------------------------------------------
    # HEALTHCARE PROFESSIONALS
    # --------------------------------------------------------

    if domain == "healthcare_professionals":

        value = healthcare.get("professionals_involved")

        return value not in (None, [])

    # --------------------------------------------------------
    # MEDICAL HISTORY
    # --------------------------------------------------------

    if domain == "medical_history":

        value = healthcare.get("medical_history")

        return value not in (None, "")

    # --------------------------------------------------------
    # REFERRAL / PERMISSION
    # --------------------------------------------------------

    if domain == "referral_permission":

        value = healthcare.get(
            "referral_or_permission_required"
        )

        return value not in (None, "")

    # --------------------------------------------------------
    # CONTRAINDICATIONS
    # --------------------------------------------------------

    if domain == "contraindications":

        value = safety.get("contraindications")

        return value not in (None, [])

    # --------------------------------------------------------
    # SAFEGUARDING
    # --------------------------------------------------------

    if domain == "safeguarding":

        value = safety.get("safeguarding_concerns")

        return value not in (None, [])

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    if domain == "risk":

        risk_type = detect_risk_question_type(
            question
        )

        risk_factors = safety.get(
            "risk_factors"
        )

        # --------------------------------------------
        # Empty risk field = nothing established
        # --------------------------------------------

        if risk_factors in (None, []):
            return False

        # --------------------------------------------
        # IMPORTANT:
        #
        # "No self-harm history" ONLY establishes
        # absence of self-harm history.
        #
        # It does NOT establish:
        # - no suicidal thoughts
        # - no self-harm thoughts
        # - no suicide attempts
        # - no thoughts of harming others
        # --------------------------------------------

        risk_text = " ".join(
            str(x).lower()
            for x in risk_factors
        )

        if risk_type == "self_harm_history":

            return (
                "no self-harm history" in risk_text
                or
                "no self harm history" in risk_text
            )

        # Ideation is not established by self-harm history.
        if risk_type == "suicidal_or_self_harm_ideation":

            return False

        # Suicide attempts are not established.
        if risk_type == "suicide_attempt":

            return False

        # Harm to others is not established.
        if risk_type == "harm_to_others":

            return False

        # General risk:
        #
        # Do not infer a complete risk assessment merely because
        # one risk factor is present.
        return False

    return True


# ============================================================
# LEGACY BYPASS CHECK
# ============================================================

def should_bypass_llm(
    question: str,
    persona: dict
):

    domain = detect_domain(question)

    if domain is None:
        return False

    return not is_defined(
        persona,
        domain,
        question
    )


# ============================================================
# PROTECTED QUESTION PROCESSOR
# ============================================================

def process_protected_question(
    question: str,
    persona: dict
):

    """
    Identify protected clinical questions.

    This function does NOT generate a client response.

    Undefined protected questions continue through the normal
    unknown_response_engine / LLM pipeline.
    """

    domain = detect_domain(question)

    if domain is None:

        return {
            "handled": False,
            "domain": None,
            "defined": None,
        }

    defined = is_defined(
        persona,
        domain,
        question
    )

    return {
        "handled": False,
        "domain": domain,
        "defined": defined,
    }