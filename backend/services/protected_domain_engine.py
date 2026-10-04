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

    # IMPORTANT:
    # Do NOT use generic "hypnosis" or "hypnotherapy" keywords
    # here. Previous hypnosis experience is detected separately
    # based on the actual intent of the question.
    "previous_hypnosis": [],

    "risk": [
        "harm yourself",
        "harmed yourself",
        "harming yourself",

        "harm myself",
        "harmed myself",
        "harming myself",

        "hurt yourself",
        "hurt myself",
        "hurt someone else",
        "hurt anyone else",

        "harming someone else",
        "harming anyone else",
        "harmed someone else",
        "harmed anyone else",

        "harm someone else",
        "harm anyone else",

        "thoughts of harming yourself",
        "thoughts of harming myself",

        "thoughts of hurting yourself",
        "thoughts of hurting myself",

        "thoughts of harming someone else",
        "thoughts of harming anyone else",

        "thoughts of hurting someone else",
        "thoughts of hurting anyone else",

        "thoughts about harming someone",
        "thoughts about hurting someone",

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
        "attempted to kill yourself",
        "attempted to kill myself",
        "tried to kill yourself",
        "tried to kill myself",
        "tried to end your life",
        "tried to end my life",
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
# HYPNOSIS CONTROL CONCERN PATTERNS
# ============================================================
#
# These questions are specifically about the client's concern
# regarding control, awareness, or autonomy during hypnosis.
#
# IMPORTANT:
# Generic "hypnosis" must NOT be treated as protected.
#
# Only hypnosis-related CONTROL concerns are protected here.
# ============================================================

HYPNOSIS_CONTROL_PATTERNS = [

    "losing control during hypnosis",
    "lose control during hypnosis",
    "control during hypnosis",

    "losing control while hypnotized",
    "lose control while hypnotized",
    "control while hypnotized",

    "losing control while in hypnosis",
    "lose control while in hypnosis",
    "control while in hypnosis",

    "remain in control during hypnosis",
    "remain in control while hypnotized",
    "remain in control while in hypnosis",

    "stay in control during hypnosis",
    "stay in control while hypnotized",
    "stay in control while in hypnosis",

    "still be in control during hypnosis",
    "still be in control while hypnotized",
    "still be in control while in hypnosis",

    "still have control during hypnosis",
    "still have control while hypnotized",

    "aware during hypnosis",
    "aware while hypnotized",
    "aware while in hypnosis",

    "aware of everything during hypnosis",
    "aware of what is happening during hypnosis",

    "remain aware during hypnosis",
    "remain aware while hypnotized",

    "stay aware during hypnosis",
    "stay aware while hypnotized",

    "guide myself through hypnosis",
    "guide myself during hypnosis",
    "guide myself through the process",

    "manage my thoughts during hypnosis",
    "manage my feelings during hypnosis",

    "manage my thoughts and feelings during hypnosis",

    "losing control during hypnotherapy",
    "lose control during hypnotherapy",
    "control during hypnotherapy",

    "remain in control during hypnotherapy",
    "stay in control during hypnotherapy",

    "still be in control during hypnotherapy",
    "aware during hypnotherapy",
    "remain aware during hypnotherapy",
]


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(question: str) -> Optional[str]:

    text = (question or "").lower().strip()

    # ========================================================
    # HYPNOSIS CONTROL CONCERN
    #
    # This must be detected before generic protected domains.
    #
    # Example:
    #
    # "Are you worried about losing control during hypnosis?"
    #
    # -> risk
    #
    # But:
    #
    # "What are you expecting from hypnosis?"
    #
    # -> None
    #
    # "Have you had hypnosis before?"
    #
    # -> previous_hypnosis
    # ========================================================

    for pattern in HYPNOSIS_CONTROL_PATTERNS:

        if pattern in text:
            return "risk"

    # ========================================================
    # RISK FIRST
    # ========================================================

    for keyword in PROTECTED_DOMAINS["risk"]:

        if keyword in text:
            return "risk"

    # ========================================================
    # PREVIOUS HYPNOSIS EXPERIENCE
    #
    # IMPORTANT:
    # We detect the QUESTION INTENT here.
    #
    # "Have you ever had hypnosis before?"
    #     -> previous_hypnosis
    #
    # "Do you have any concerns about hypnosis?"
    #     -> NOT previous_hypnosis
    #
    # "Are you worried about losing control during hypnosis?"
    #     -> risk
    #
    # "What are you expecting from hypnosis?"
    #     -> NOT previous_hypnosis
    #
    # "Are you ready to go into hypnosis?"
    #     -> NOT previous_hypnosis
    # ========================================================

    hypnosis_history_patterns = [

        # Direct previous-experience questions
        "have you ever had hypnosis",
        "have you had hypnosis",
        "have you ever experienced hypnosis",
        "have you experienced hypnosis",

        "have you ever had hypnotherapy",
        "have you had hypnotherapy",
        "have you ever experienced hypnotherapy",
        "have you experienced hypnotherapy",

        # Hypnotherapist experience
        "have you ever seen a hypnotherapist",
        "have you seen a hypnotherapist",
        "have you ever worked with a hypnotherapist",
        "have you worked with a hypnotherapist",

        # Received treatment
        "have you received hypnotherapy",
        "have you ever received hypnotherapy",

        "have you received hypnosis",
        "have you ever received hypnosis",

        # Explicit history / previous experience
        "previous experience with hypnosis",
        "previous experience of hypnosis",
        "previous experience with hypnotherapy",
        "previous experience of hypnotherapy",

        "history of hypnosis",
        "history of hypnotherapy",

        "past experience with hypnosis",
        "past experience of hypnosis",
        "past experience with hypnotherapy",
        "past experience of hypnotherapy",
    ]

    for pattern in hypnosis_history_patterns:

        if pattern in text:
            return "previous_hypnosis"

    # ========================================================
    # OTHER PROTECTED DOMAINS
    #
    # NOTE:
    # "hypnosis" itself is intentionally NOT included here.
    #
    # General hypnosis questions should be handled naturally
    # by the persona/LLM unless they are specifically about:
    #
    # - previous hypnosis experience
    # - hypnosis control concern
    # ========================================================

    domain_order = [
        "safeguarding",
        "contraindications",
        "medication",
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
# VALUE NORMALISATION
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
    #
    # "Have you ever had thoughts of harming yourself?"
    #
    # The same principle applies to hypnosis-control concern.
    # The presence of another risk factor does NOT establish
    # that the client has a defined answer about control during
    # hypnosis.
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
    # HYPNOSIS CONTROL CONCERN
    #
    # This MUST be checked before general risk.
    #
    # It is intentionally separate from self-harm,
    # suicide, and harm-to-others questions.
    # --------------------------------------------------------

    if any(
        x in text
        for x in HYPNOSIS_CONTROL_PATTERNS
    ):

        return "hypnosis_control_concern"

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

            "thought about harming yourself",
            "thought about harming myself",

            "thought about hurting yourself",
            "thought about hurting myself",

            "thinking about suicide",
            "wanted to die",
            "wanting to die",

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
        # HYPNOSIS CONTROL CONCERN
        # ----------------------------------------------------
        #
        # IMPORTANT:
        #
        # This response addresses the specific concern.
        # It does NOT invent a clinical fact such as:
        #
        # "I have lost control during hypnosis before."
        #
        # It simply preserves the client's uncertainty/
        # concern around control during hypnosis.
        # ----------------------------------------------------

        if risk_type == "hypnosis_control_concern":

            return (
                "I'm concerned about losing control during hypnosis. "
                "I want to make sure I'm aware of what's happening "
                "and can still guide myself through the process."
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
    #
    # This includes:
    #
    # - self_harm_thoughts
    # - suicide_attempt
    # - self_harm_history
    # - harm_to_others
    # - hypnosis_control_concern
    # - general_risk
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