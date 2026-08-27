from typing import Any, Dict, List


# ============================================================
# PHASE 2B — CLINICAL RISK & SAFETY ENGINE
# ============================================================
#
# This engine:
#
# - DOES NOT diagnose.
# - DOES NOT infer risk from therapist questions.
# - DOES NOT treat uncertainty as a positive finding.
# - DOES NOT treat negative findings as positive findings.
# - Evaluates only evidence already extracted from the
#   therapist/client conversation.
#
# IMPORTANT:
#
# The following are different states:
#
#   "No history of self-harm"
#       -> explicit negative finding
#
#   "I'm not sure whether I've had thoughts like that"
#       -> unknown / unestablished
#
#   "Yes, I have had thoughts of harming myself"
#       -> positive risk evidence
#
# These MUST NOT be collapsed into the same state.
# ============================================================


SAFETY_DOMAINS = {
    "risk",
    "contraindications",
    "safeguarding",
    "medical_history",
    "psychological_care",
    "psychiatric_care",
    "medication",
    "healthcare_professionals",
    "referral_permission",
}


# ============================================================
# NEGATIVE / UNKNOWN LANGUAGE
# ============================================================

NEGATIVE_PATTERNS = [

    # Self-harm history
    "no history of self-harm",
    "no history of self harm",
    "no self-harm history",
    "no self harm history",
    "never harmed myself",
    "never harmed themselves",
    "never harmed yourself",
    "have not harmed myself",
    "haven't harmed myself",
    "do not harm myself",
    "don't harm myself",

    # Suicide
    "no history of suicide",
    "no suicide history",
    "never attempted suicide",
    "never attempted anything like that",
    "no suicide attempts",
    "no history of suicide attempts",

    # General negative safety
    "no safeguarding concerns",
    "no safeguarding issues",
    "no safety concerns",
    "no risk factors",
    "no known risk factors",

    # Medical / contraindication negatives
    "no medical conditions",
    "no relevant medical conditions",
    "no contraindications",
    "no known contraindications",

    # Psychological / psychiatric negatives
    "no psychological treatment",
    "no psychological care",
    "no psychiatric treatment",
    "no psychiatric care",

    # Medication
    "not taking any medication",
    "not taking medication",
    "no medication",
]


UNCERTAINTY_PATTERNS = [

    "i'm not sure",
    "im not sure",
    "i am not sure",
    "i'm uncertain",
    "im uncertain",
    "i am uncertain",
    "i don't know",
    "i dont know",
    "i can't remember",
    "i cant remember",
    "i don't remember",
    "i dont remember",
    "i'd need to think",
    "id need to think",
    "i need to think",
    "i'd need to check",
    "id need to check",
    "i need to check",
    "not certain",
    "not sure whether",
    "not sure if",
    "can't say for certain",
    "cannot say for certain",
    "can't say",
    "cannot say",
    "unclear",
    "uncertain",
]


POSITIVE_RISK_PATTERNS = [

    "i have thoughts of harming myself",
    "i have thoughts of harming yourself",
    "i have thoughts of hurting myself",
    "i have thoughts of hurting yourself",

    "i have harmed myself",
    "i have harmed themselves",

    "i have hurt myself",
    "i have hurt themselves",

    "i have attempted suicide",
    "i attempted suicide",
    "i have attempted to kill myself",

    "i have thoughts of suicide",
    "i have suicidal thoughts",

    "i want to harm myself",
    "i want to hurt myself",

    "i want to kill myself",
    "i want to end my life",

    "i have thoughts of harming someone else",
    "i have thoughts of hurting someone else",

    "i want to harm someone else",
    "i want to hurt someone else",

    "i have harmed someone else",
    "i have hurt someone else",
]


# ============================================================
# TEXT NORMALISATION
# ============================================================

def _normalise_text(value: Any) -> str:

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


# ============================================================
# NEGATIVE STATEMENT DETECTION
# ============================================================

def _is_explicit_negative(value: Any) -> bool:

    text = _normalise_text(value)

    if not text:
        return False

    return any(
        pattern in text
        for pattern in NEGATIVE_PATTERNS
    )


# ============================================================
# UNCERTAINTY DETECTION
# ============================================================

def _is_uncertain(value: Any) -> bool:

    text = _normalise_text(value)

    if not text:
        return True

    return any(
        pattern in text
        for pattern in UNCERTAINTY_PATTERNS
    )


# ============================================================
# POSITIVE RISK DETECTION
# ============================================================

def _is_positive_risk(value: Any) -> bool:

    text = _normalise_text(value)

    if not text:
        return False

    # --------------------------------------------------------
    # Never classify an explicitly uncertain statement as
    # positive merely because it contains a risk word.
    # --------------------------------------------------------

    if _is_uncertain(text):
        return False

    # --------------------------------------------------------
    # Explicit negative statement always wins.
    # --------------------------------------------------------

    if _is_explicit_negative(text):
        return False

    return any(
        pattern in text
        for pattern in POSITIVE_RISK_PATTERNS
    )


# ============================================================
# MEANINGFUL VALUE
# ============================================================

def _is_meaningful_value(value: Any) -> bool:
    """
    Determine whether an evidence value contains actual content.

    Unknown / empty values must not become safety findings.
    """

    if value is None:
        return False

    if isinstance(value, str):

        text = value.strip().lower()

        if not text:
            return False

        unknown_values = {
            "unknown",
            "not established",
            "not specified",
            "unclear",
            "uncertain",
            "not discussed",
            "not known",
            "none established",
        }

        if text in unknown_values:
            return False

    if isinstance(
        value,
        (
            list,
            dict,
            tuple,
            set
        )
    ):
        return len(value) > 0

    return True


# ============================================================
# FLAGS
# ============================================================

def _normalise_flags(
    flags: Any
) -> List[str]:

    if not isinstance(
        flags,
        list
    ):
        return []

    cleaned = []

    for flag in flags:

        if flag is None:
            continue

        value = str(
            flag
        ).strip()

        if (
            value
            and value not in cleaned
        ):
            cleaned.append(
                value
            )

    return cleaned


# ============================================================
# CREATE SAFETY STATE
# ============================================================

def create_safety_state() -> Dict[str, Any]:

    return {

        "level":
            "unestablished",

        "requires_attention":
            False,

        "requires_referral_review":
            False,

        "requires_safeguarding_review":
            False,

        "evidence":
            [],

        "flags":
            [],

        "established_domains":
            [],
    }


# ============================================================
# EVALUATE SAFETY
# ============================================================

def evaluate_safety(
    clinical_evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:

    state = create_safety_state()

    if not isinstance(
        clinical_evidence,
        list
    ):
        return state


    safety_evidence = []


    # ========================================================
    # FILTER AND NORMALISE EVIDENCE
    # ========================================================

    for item in clinical_evidence:

        if not isinstance(
            item,
            dict
        ):
            continue


        domain = item.get(
            "domain"
        )


        if domain not in SAFETY_DOMAINS:
            continue


        value = item.get(
            "value"
        )


        if not _is_meaningful_value(
            value
        ):
            continue


        try:

            confidence = float(
                item.get(
                    "confidence",
                    0.0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0


        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )


        # ----------------------------------------------------
        # Weak extraction does not drive safety state.
        # ----------------------------------------------------

        if confidence < 0.5:
            continue


        evidence_item = {

            "domain":
                domain,

            "value":
                value,

            "status":
                item.get(
                    "status",
                    "mentioned"
                ),

            "confidence":
                confidence,

            "evidence_text":
                item.get(
                    "evidence_text"
                ),

            "clinical_significance":
                item.get(
                    "clinical_significance"
                ),

            "flags":
                _normalise_flags(
                    item.get(
                        "flags",
                        []
                    )
                ),

        }


        safety_evidence.append(
            evidence_item
        )


    state["evidence"] = (
        safety_evidence
    )


    # ========================================================
    # ESTABLISHED DOMAINS
    # ========================================================

    state["established_domains"] = list(
        dict.fromkeys(

            item["domain"]

            for item in safety_evidence
        )
    )


    # ========================================================
    # COLLECT FLAGS
    # ========================================================

    all_flags = []


    for item in safety_evidence:

        for flag in item["flags"]:

            if flag not in all_flags:

                all_flags.append(
                    flag
                )


    state["flags"] = all_flags


    # ========================================================
    # NO EVIDENCE
    # ========================================================

    if not safety_evidence:

        state["level"] = (
            "unestablished"
        )

        return state


    # ========================================================
    # INFORMATION EXISTS
    # ========================================================

    state["level"] = (
        "information_established"
    )


    # ========================================================
    # DIRECT RISK
    # ========================================================

    risk_items = [

        item

        for item in safety_evidence

        if item["domain"] == "risk"
    ]


    for item in risk_items:

        value = item.get(
            "value"
        )


        # ----------------------------------------------------
        # Unknown risk answer:
        #
        # Do NOT mark as positive risk.
        # ----------------------------------------------------

        if _is_uncertain(
            value
        ):

            continue


        # ----------------------------------------------------
        # Explicit negative risk:
        #
        # Information established, but no attention required.
        # ----------------------------------------------------

        if _is_explicit_negative(
            value
        ):

            continue


        # ----------------------------------------------------
        # Explicit positive risk:
        # ----------------------------------------------------

        if _is_positive_risk(
            value
        ):

            state["requires_attention"] = True

            state["level"] = (
                "review_required"
            )


    # ========================================================
    # CONTRAINDICATIONS
    # ========================================================

    contraindication_items = [

        item

        for item in safety_evidence

        if item["domain"]
        == "contraindications"
    ]


    for item in contraindication_items:

        value = item.get(
            "value"
        )


        # "No contraindications" is NOT a concern.
        if _is_explicit_negative(
            value
        ):
            continue


        # Uncertainty does not equal contraindication.
        if _is_uncertain(
            value
        ):
            continue


        state["requires_attention"] = True

        state["requires_referral_review"] = True

        state["level"] = (
            "review_required"
        )


    # ========================================================
    # SAFEGUARDING
    # ========================================================

    safeguarding_items = [

        item

        for item in safety_evidence

        if item["domain"]
        == "safeguarding"
    ]


    for item in safeguarding_items:

        value = item.get(
            "value"
        )


        # ----------------------------------------------------
        # CRITICAL:
        #
        # Negative safeguarding information does NOT require
        # safeguarding review.
        #
        # Example:
        #
        # "No history of self-harm."
        #
        # must NOT become:
        #
        # requires_safeguarding_review = True
        # ----------------------------------------------------

        if _is_explicit_negative(
            value
        ):

            continue


        # ----------------------------------------------------
        # Unknown does not equal safeguarding concern.
        # ----------------------------------------------------

        if _is_uncertain(
            value
        ):

            continue


        # ----------------------------------------------------
        # Actual positive safeguarding information.
        # ----------------------------------------------------

        state["requires_attention"] = True

        state["requires_safeguarding_review"] = True

        state["level"] = (
            "review_required"
        )


    # ========================================================
    # REFERRAL / PERMISSION
    # ========================================================

    referral_items = [

        item

        for item in safety_evidence

        if item["domain"]
        == "referral_permission"
    ]


    for item in referral_items:

        value_text = _normalise_text(
            item.get("value")
        )


        if _is_uncertain(
            value_text
        ):
            continue


        if _is_explicit_negative(
            value_text
        ):
            continue


        referral_terms = [

            "required",
            "needed",
            "need permission",
            "requires permission",
            "professional advice",
            "medical advice",
            "refer",
            "referral",
        ]


        if any(
            term in value_text
            for term in referral_terms
        ):

            state["requires_attention"] = True

            state["requires_referral_review"] = True

            state["level"] = (
                "review_required"
            )


    # ========================================================
    # EXPLICIT FLAGS
    # ========================================================

    attention_flags = {

        "risk",

        "safety_concern",

        "contraindication",

        "safeguarding",

        "referral_required",

        "professional_review_required",
    }


    for flag in all_flags:

        flag_normalised = (
            str(flag)
            .strip()
            .lower()
        )


        if flag_normalised not in attention_flags:
            continue


        # ----------------------------------------------------
        # Do not allow an explicit flag attached to an
        # uncertain/negative item to create a false concern.
        # ----------------------------------------------------

        matching_items = [

            item

            for item in safety_evidence

            if flag in item["flags"]
        ]


        valid_positive_item = False


        for item in matching_items:

            value = item.get(
                "value"
            )


            if _is_uncertain(
                value
            ):
                continue


            if _is_explicit_negative(
                value
            ):
                continue


            valid_positive_item = True

            break


        if not valid_positive_item:
            continue


        state["requires_attention"] = True

        state["level"] = (
            "review_required"
        )


        if flag_normalised == "safeguarding":

            state[
                "requires_safeguarding_review"
            ] = True


        if flag_normalised in {
            "contraindication",
            "referral_required",
            "professional_review_required",
        }:

            state[
                "requires_referral_review"
            ] = True


    return state