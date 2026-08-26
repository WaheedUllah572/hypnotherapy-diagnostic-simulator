from typing import Any, Dict, Optional


# ============================================================
# PROTECTED CLINICAL DOMAINS
# ============================================================

PROTECTED_DOMAINS = {
    "medication": [
        "medication",
        "medications",
        "medicine",
        "medicines",
        "tablets",
        "prescription",
        "prescribed",
        "drug",
        "drugs",
    ],

    "psychological_care": [
        "psychological care",
        "psychological treatment",
        "psychological support",
        "psychologist",
        "psychotherapy",
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
        "psychiatric support",
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
        "harming myself",
        "hurt yourself",
        "hurt myself",
        "thoughts of harming yourself",
        "thoughts of harming myself",
        "thoughts of hurting yourself",
        "thoughts of hurting myself",
        "thoughts of self harm",
        "thoughts of self-harm",
        "self harm",
        "self-harm",
        "suicidal",
        "suicide",
        "suicidal thoughts",
        "thoughts about suicide",
        "thoughts of suicide",
        "attempted suicide",
        "suicide attempt",
        "harm someone else",
        "harm anyone else",
        "hurt someone else",
        "hurt anyone else",
        "harming someone else",
        "harming anyone else",
        "thoughts of harming someone",
        "thoughts of harming anyone",
        "thoughts of hurting someone",
        "thoughts of hurting anyone",
    ],

    "healthcare_professionals": [
        "healthcare professional",
        "healthcare professionals",
        "health care professional",
        "doctor involved",
        "doctors involved",
        "doctor",
        "doctors",
        "gp",
        "general practitioner",
        "supporting you medically",
        "involved in supporting you",
        "professional involved",
        "professionals involved",
    ],

    "medical_history": [
        "medical history",
        "medical condition",
        "medical conditions",
        "health condition",
        "health conditions",
        "physical health condition",
        "physical health",
        "health problems",
        "medical problems",
    ],

    "referral_permission": [
        "referral",
        "permission",
        "medical clearance",
        "doctor's permission",
        "doctors permission",
        "gp permission",
        "gp referral",
    ],

    "contraindications": [
        "contraindication",
        "contraindications",
        "unsuitable",
        "make hypnotherapy unsafe",
        "make hypnosis unsafe",
        "might prevent hypnotherapy",
        "additional professional advice",
    ],

    "safeguarding": [
        "safeguarding",
        "abuse",
        "being harmed",
        "someone hurting you",
        "feel safe at home",
        "safe at home",
    ],
}


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(question: str) -> Optional[str]:

    text = (question or "").lower().strip()

    # ========================================================
    # RISK FIRST
    # ========================================================

    for keyword in PROTECTED_DOMAINS["risk"]:

        if keyword in text:
            return "risk"

    # ========================================================
    # OTHER PROTECTED DOMAINS
    # ========================================================

    domain_order = [
        "safeguarding",
        "contraindications",
        "medication",
        "previous_hypnosis",
        "psychiatric_care",
        "psychological_care",
        "healthcare_professionals",
        "referral_permission",
        "medical_history",
    ]

    for domain in domain_order:

        for keyword in PROTECTED_DOMAINS[domain]:

            if keyword in text:
                return domain

    return None


# ============================================================
# VALUE NORMALISISATION
# ============================================================

def _is_empty(value: Any) -> bool:

    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0

    return False


# ============================================================
# GET AUTHORITATIVE DOMAIN VALUE
#
# This function is intentionally included here so other modules
# can safely import it if required.
# ============================================================

def get_domain_value(
    persona: Dict[str, Any],
    domain: str
) -> Any:

    healthcare = persona.get(
        "healthcare",
        {}
    )

    hypnosis_history = persona.get(
        "hypnosis_history",
        {}
    )

    safety = persona.get(
        "safety",
        {}
    )

    medication = healthcare.get(
        "medication",
        {}
    )

    mapping = {

        "medication":
            medication.get("current"),

        "medical_history":
            healthcare.get("medical_history"),

        "psychological_care":
            healthcare.get("psychological_care"),

        "psychiatric_care":
            healthcare.get("psychiatric_care"),

        "healthcare_professionals":
            healthcare.get("professionals_involved"),

        "previous_hypnosis":
            hypnosis_history.get("previous_experience"),

        "referral_permission":
            healthcare.get(
                "referral_or_permission_required"
            ),

        "risk":
            safety.get("risk_factors"),

        "contraindications":
            safety.get("contraindications"),

        "safeguarding":
            safety.get("safeguarding_concerns"),
    }

    return mapping.get(domain)


# ============================================================
# CHECK WHETHER DOMAIN IS DEFINED
# ============================================================

def is_defined(
    persona: Dict[str, Any],
    domain: str
) -> bool:

    value = get_domain_value(
        persona,
        domain
    )

    # --------------------------------------------------------
    # RISK REQUIRES EXACT QUESTION INTERPRETATION.
    #
    # A case saying:
    # "No self-harm history"
    #
    # does NOT automatically answer:
    # "Have you ever had thoughts of harming yourself?"
    # --------------------------------------------------------

    if domain == "risk":
        return False

    return not _is_empty(value)


# ============================================================
# SHOULD BYPASS LLM
# ============================================================

def should_bypass_llm(
    question: str,
    persona: dict
) -> bool:

    domain = detect_domain(
        question
    )

    if domain is None:
        return False

    return not is_defined(
        persona,
        domain
    )


# ============================================================
# EXACT RISK QUESTION TYPE
# ============================================================

def detect_risk_question_type(
    question: str
) -> str:

    text = (
        question or ""
    ).lower().strip()

    # --------------------------------------------------------
    # SELF-HARM / SUICIDAL THOUGHTS
    # --------------------------------------------------------

    if any(
        x in text
        for x in [

            "thoughts of harming yourself",
            "thoughts of harming myself",

            "thoughts of hurting yourself",
            "thoughts of hurting myself",

            "thoughts of self harm",
            "thoughts of self-harm",

            "suicidal thoughts",
            "thoughts about suicide",
            "thoughts of suicide",

            "have you ever thought about harming yourself",
            "have you ever thought about hurting yourself",

            "have you had thoughts of harming yourself",
            "have you had thoughts of hurting yourself",

        ]
    ):

        return "self_harm_thoughts"

    # --------------------------------------------------------
    # SUICIDE ATTEMPT
    # --------------------------------------------------------

    if any(
        x in text
        for x in [

            "attempted suicide",
            "suicide attempt",
            "attempted to kill yourself",
            "attempted to kill myself",
            "tried to kill yourself",
            "tried to kill myself",
            "tried to end your life",
            "tried to end my life",

        ]
    ):

        return "suicide_attempt"

    # --------------------------------------------------------
    # SELF-HARM HISTORY
    # --------------------------------------------------------

    if any(
        x in text
        for x in [

            "history of self harm",
            "history of self-harm",
            "history of harming yourself",
            "history of hurting yourself",

            "ever harmed yourself",
            "ever harmed myself",

            "ever hurt yourself",
            "ever hurt myself",

            "self harm before",
            "self-harm before",

            "self harm history",
            "self-harm history",

            "have you self harmed",
            "have you ever self harmed",

        ]
    ):

        return "self_harm_history"

    # --------------------------------------------------------
    # HARM TO OTHERS
    # --------------------------------------------------------

    if any(
        x in text
        for x in [

            "thoughts of harming someone else",
            "thoughts of harming anyone else",
            "thoughts of hurting someone else",
            "thoughts of hurting anyone else",

            "thoughts about harming someone",
            "thoughts about hurting someone",

            "harm someone else",
            "hurt someone else",

            "harm anyone else",
            "hurt anyone else",

        ]
    ):

        return "harm_to_others"

    # --------------------------------------------------------
    # GENERAL RISK
    # --------------------------------------------------------

    return "general_risk"


# ============================================================
# GET PROTECTED UNCERTAIN RESPONSE
# ============================================================

def get_uncertain_response(
    domain: str,
    question: str,
    persona: Dict[str, Any]
) -> str:

    # ========================================================
    # RISK
    # ========================================================

    if domain == "risk":

        risk_type = detect_risk_question_type(
            question
        )

        # ----------------------------------------------------
        # THOUGHTS OF SELF-HARM
        # ----------------------------------------------------

        if risk_type == "self_harm_thoughts":

            return (
                "I'm not sure whether I've had thoughts like that. "
                "I'd need to think about it."
            )

        # ----------------------------------------------------
        # SUICIDE ATTEMPT
        # ----------------------------------------------------

        if risk_type == "suicide_attempt":

            return (
                "I'm not certain whether I've ever attempted "
                "anything like that. I'd need to think about it."
            )

        # ----------------------------------------------------
        # SELF-HARM HISTORY
        # ----------------------------------------------------

        if risk_type == "self_harm_history":

            safety = persona.get(
                "safety",
                {}
            )

            risk_factors = safety.get(
                "risk_factors",
                []
            )

            for item in risk_factors:

                if "no self-harm history" in str(
                    item
                ).lower():

                    return (
                        "No, I don't have a history of self-harm. "
                        "My main difficulty has been the anxiety "
                        "around driving on motorways."
                    )

            return (
                "I'm not certain about my history in that area. "
                "I'd need to think about it."
            )

        # ----------------------------------------------------
        # HARM TO OTHERS
        # ----------------------------------------------------

        if risk_type == "harm_to_others":

            return (
                "I'm not sure whether I've had thoughts like that "
                "about harming someone else."
            )

        # ----------------------------------------------------
        # GENERAL RISK
        # ----------------------------------------------------

        return (
            "I'm not sure how to answer that properly. "
            "I'd need to think about it."
        )

    # ========================================================
    # MEDICATION
    # ========================================================

    if domain == "medication":

        return (
            "I'm not certain what medication I'm currently taking, "
            "if any. I'd need to check that."
        )

    # ========================================================
    # PSYCHOLOGICAL CARE
    # ========================================================

    if domain == "psychological_care":

        return (
            "I'm not sure whether I've had psychological treatment "
            "or support before. I'd need to think back."
        )

    # ========================================================
    # PSYCHIATRIC CARE
    # ========================================================

    if domain == "psychiatric_care":

        return (
            "I'm not sure whether I've ever seen a psychiatrist. "
            "I'd need to think back before I could answer properly."
        )

    # ========================================================
    # PREVIOUS HYPNOSIS
    # ========================================================

    if domain == "previous_hypnosis":

        return (
            "I can't remember whether I've had hypnotherapy or "
            "hypnosis before."
        )

    # ========================================================
    # HEALTHCARE PROFESSIONALS
    # ========================================================

    if domain == "healthcare_professionals":

        return (
            "I'm not sure which healthcare professionals, if any, "
            "are currently involved in my care."
        )

    # ========================================================
    # MEDICAL HISTORY
    # ========================================================

    if domain == "medical_history":

        return (
            "I'm not completely sure about my medical history. "
            "I'd need to think about it more."
        )

    # ========================================================
    # REFERRAL / PERMISSION
    # ========================================================

    if domain == "referral_permission":

        return (
            "I'm not sure whether I need a referral or medical "
            "clearance for this."
        )

    # ========================================================
    # CONTRAINDICATIONS
    # ========================================================

    if domain == "contraindications":

        return (
            "I'm not sure whether there are any medical or "
            "psychological factors that could affect my suitability."
        )

    # ========================================================
    # SAFEGUARDING
    # ========================================================

    if domain == "safeguarding":

        return (
            "I'm not sure how to answer the question about my "
            "personal safety without thinking about it more."
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    return (
        "I'm not certain about that particular part of my history."
    )


# ============================================================
# MAIN PROCESSOR
# ============================================================

def process_protected_question(
    question: str,
    persona: dict
):

    domain = detect_domain(
        question
    )

    # --------------------------------------------------------
    # NOT PROTECTED
    # --------------------------------------------------------

    if domain is None:

        return {
            "handled": False,
            "domain": None,
        }

    # --------------------------------------------------------
    # DEFINED NON-RISK DOMAIN
    # --------------------------------------------------------

    if domain != "risk":

        if is_defined(
            persona,
            domain
        ):

            return {
                "handled": False,
                "domain": domain,
            }

    # --------------------------------------------------------
    # RISK IS ALWAYS INTERPRETED BY EXACT QUESTION TYPE
    # --------------------------------------------------------

    response = get_uncertain_response(
        domain=domain,
        question=question,
        persona=persona
    )

    return {
        "handled": True,
        "domain": domain,
        "response": response,
    }