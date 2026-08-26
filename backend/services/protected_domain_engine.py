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

    # Risk must be checked first because questions can contain
    # overlapping clinical terminology.

    risk_keywords = PROTECTED_DOMAINS["risk"]

    for keyword in risk_keywords:
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
# AUTHORITATIVE VALUE CHECK
# ============================================================

def is_defined(persona: dict, domain: str):

    healthcare = persona.get("healthcare", {})
    hypnosis = persona.get("hypnosis_history", {})
    safety = persona.get("safety", {})

    if domain == "medication":
        medication = healthcare.get("medication", {})

        return (
            medication.get("current") is not None
            and medication.get("current") != ""
        )

    if domain == "psychological_care":
        value = healthcare.get("psychological_care")

        return value not in (None, "")

    if domain == "psychiatric_care":
        value = healthcare.get("psychiatric_care")

        return value not in (None, "")

    if domain == "previous_hypnosis":
        value = hypnosis.get("previous_experience")

        return value not in (None, "")

    if domain == "healthcare_professionals":
        value = healthcare.get("professionals_involved")

        return value not in (None, [])

    if domain == "risk":
        value = safety.get("risk_factors")

        return value not in (None, [])

    if domain == "contraindications":
        value = safety.get("contraindications")

        return value not in (None, [])

    if domain == "safeguarding":
        value = safety.get("safeguarding_concerns")

        return value not in (None, [])

    if domain == "medical_history":
        value = healthcare.get("medical_history")

        return value not in (None, "")

    if domain == "referral_permission":
        value = healthcare.get("referral_or_permission_required")

        return value not in (None, "")

    return True


# ============================================================
# LEGACY BYPASS CHECK
# ============================================================

def should_bypass_llm(question: str, persona: dict):

    """
    Kept for compatibility with existing code.

    This function identifies whether a protected domain is undefined.

    IMPORTANT:
    It does NOT generate a response.

    Undefined protected questions must be passed to the
    unknown_response_engine so that the response can be
    topic-specific, natural and varied.
    """

    domain = detect_domain(question)

    if domain is None:
        return False

    return not is_defined(persona, domain)


# ============================================================
# PROTECTED QUESTION PROCESSOR
# ============================================================

def process_protected_question(
    question: str,
    persona: dict
):

    """
    Identify protected clinical questions.

    This function NO LONGER generates a hard-coded client response.

    Undefined protected information must be handled by
    unknown_response_engine.py.

    Returning handled=False is intentional so that /chat continues
    through the normal LLM generation pipeline.
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
        domain
    )

    return {
        "handled": False,
        "domain": domain,
        "defined": defined,
    }