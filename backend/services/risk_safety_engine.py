from typing import Any, Dict, List


# ============================================================
# PHASE 2B — CLINICAL RISK & SAFETY ENGINE
# ============================================================
#
# This engine evaluates ONLY evidence that has already been
# extracted from the client conversation.
#
# It does NOT:
#
# - diagnose
# - infer risk from therapist questions
# - treat uncertainty as a positive finding
# - treat missing information as a negative finding
# - treat negative findings as positive findings
# - invent safeguarding concerns
# - invent contraindications
#
# The three important states remain separate:
#
#   Explicit negative:
#       "No history of self-harm."
#
#   Unknown:
#       "I'm not sure whether I've had thoughts like that."
#
#   Positive:
#       "I have had thoughts of harming myself."
#
# ============================================================


# ============================================================
# SAFETY DOMAINS
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
# SAFETY LEVELS
# ============================================================

SAFETY_LEVEL_UNESTABLISHED = "unestablished"

SAFETY_LEVEL_INFORMATION = "information_established"

SAFETY_LEVEL_REVIEW = "review_required"


# ============================================================
# NEGATIVE LANGUAGE
# ============================================================

NEGATIVE_PATTERNS = [

    # --------------------------------------------------------
    # Self-harm
    # --------------------------------------------------------

    "no history of self-harm",
    "no history of self harm",
    "no self-harm history",
    "no self harm history",

    "never harmed myself",
    "never harmed themselves",
    "never harmed yourself",

    "have not harmed myself",
    "haven't harmed myself",

    # --------------------------------------------------------
    # Suicide
    # --------------------------------------------------------

    "no history of suicide",
    "no suicide history",

    "never attempted suicide",
    "never attempted anything like that",

    "no suicide attempts",
    "no history of suicide attempts",

    "no suicidal thoughts",
    "no history of suicidal thoughts",

    "no thoughts of harming myself",
    "no thoughts of harming themselves",

    # --------------------------------------------------------
    # General safety
    # --------------------------------------------------------

    "no safeguarding concerns",
    "no safeguarding issues",

    "no safety concerns",

    "no risk factors",
    "no known risk factors",

    # --------------------------------------------------------
    # Medical
    # --------------------------------------------------------

    "no medical conditions",
    "no relevant medical conditions",

    "no contraindications",
    "no known contraindications",

    # --------------------------------------------------------
    # Psychological care
    # --------------------------------------------------------

    "no psychological treatment",
    "no psychological care",

    "never had psychological treatment",
    "never had counselling",
    "never had counseling",

    # --------------------------------------------------------
    # Psychiatric care
    # --------------------------------------------------------

    "no psychiatric treatment",
    "no psychiatric care",

    "never had psychiatric treatment",
    "never seen a psychiatrist",

    # --------------------------------------------------------
    # Medication
    # --------------------------------------------------------

    "not taking any medication",
    "not taking medication",
    "no medication",
]


# ============================================================
# UNCERTAINTY LANGUAGE
# ============================================================

UNCERTAINTY_PATTERNS = [

    "i'm not sure",
    "im not sure",
    "i am not sure",

    "i'm uncertain",
    "im uncertain",
    "i am uncertain",

    "i don't know",
    "i dont know",
    "i do not know",

    "i can't remember",
    "i cant remember",
    "i cannot remember",

    "i don't remember",
    "i dont remember",
    "i do not remember",

    "i'd need to think",
    "id need to think",
    "i would need to think",

    "i need to think",

    "i'd need to check",
    "id need to check",
    "i would need to check",

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


# ============================================================
# POSITIVE RISK LANGUAGE
# ============================================================

POSITIVE_RISK_PATTERNS = [

    # --------------------------------------------------------
    # Self-harm thoughts
    # --------------------------------------------------------

    "i have thoughts of harming myself",
    "i have thoughts of hurting myself",

    "i am having thoughts of harming myself",
    "i am having thoughts of hurting myself",

    "i think about harming myself",
    "i think about hurting myself",

    "i've thought about harming myself",
    "ive thought about harming myself",

    "i've thought about hurting myself",
    "ive thought about hurting myself",

    # --------------------------------------------------------
    # Self-harm behaviour
    # --------------------------------------------------------

    "i have harmed myself",
    "i have hurt myself",

    "i've harmed myself",
    "ive harmed myself",

    "i've hurt myself",
    "ive hurt myself",

    # --------------------------------------------------------
    # Suicide attempts
    # --------------------------------------------------------

    "i have attempted suicide",
    "i attempted suicide",

    "i've attempted suicide",
    "ive attempted suicide",

    "i have attempted to kill myself",

    # --------------------------------------------------------
    # Suicidal thoughts
    # --------------------------------------------------------

    "i have thoughts of suicide",
    "i have suicidal thoughts",

    "i'm having suicidal thoughts",
    "im having suicidal thoughts",

    "i've had suicidal thoughts",
    "ive had suicidal thoughts",

    # --------------------------------------------------------
    # Intent
    # --------------------------------------------------------

    "i want to harm myself",
    "i want to hurt myself",

    "i want to kill myself",
    "i want to end my life",

    # --------------------------------------------------------
    # Harm to others
    # --------------------------------------------------------

    "i have thoughts of harming someone else",
    "i have thoughts of hurting someone else",

    "i want to harm someone else",
    "i want to hurt someone else",

    "i have harmed someone else",
    "i have hurt someone else",

    "i've harmed someone else",
    "ive harmed someone else",

    "i've hurt someone else",
    "ive hurt someone else",
]


# ============================================================
# TEXT NORMALISATION
# ============================================================

def _normalise_text(
    value: Any
) -> str:
    """
    Normalise text for deterministic safety checks.
    """

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

def _is_explicit_negative(
    value: Any
) -> bool:
    """
    Return True only when the supplied value contains an
    explicit negative safety statement.
    """

    text = _normalise_text(
        value
    )

    if not text:
        return False

    return any(
        pattern in text
        for pattern in NEGATIVE_PATTERNS
    )


# ============================================================
# UNCERTAINTY DETECTION
# ============================================================

def _is_uncertain(
    value: Any
) -> bool:
    """
    Determine whether the supplied value is explicitly uncertain.

    Empty values are treated as unknown.
    """

    text = _normalise_text(
        value
    )

    if not text:
        return True

    return any(
        pattern in text
        for pattern in UNCERTAINTY_PATTERNS
    )


# ============================================================
# POSITIVE RISK DETECTION
# ============================================================

def _is_positive_risk(
    value: Any
) -> bool:
    """
    Detect explicit positive risk language.

    Ordering is intentional:

    1. Empty/unknown -> False
    2. Uncertain -> False
    3. Explicit negative -> False
    4. Explicit positive -> True
    """

    text = _normalise_text(
        value
    )

    if not text:
        return False

    # --------------------------------------------------------
    # Uncertainty does not become positive risk.
    # --------------------------------------------------------

    if _is_uncertain(
        text
    ):
        return False

    # --------------------------------------------------------
    # Explicit negative always wins.
    # --------------------------------------------------------

    if _is_explicit_negative(
        text
    ):
        return False

    # --------------------------------------------------------
    # Explicit positive risk.
    # --------------------------------------------------------

    return any(
        pattern in text
        for pattern in POSITIVE_RISK_PATTERNS
    )


# ============================================================
# MEANINGFUL VALUE
# ============================================================

def _is_meaningful_value(
    value: Any
) -> bool:
    """
    Determine whether an evidence value contains actual
    established information.

    Unknown/missing values must not become safety findings.
    """

    if value is None:
        return False

    if isinstance(
        value,
        str
    ):

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
            "__undefined__",
        }

        if text in unknown_values:
            return False

    if isinstance(
        value,
        (
            list,
            dict,
            tuple,
            set,
        )
    ):

        return len(value) > 0

    return True


# ============================================================
# NORMALISE FLAGS
# ============================================================

def _normalise_flags(
    flags: Any
) -> List[str]:
    """
    Return clean unique flags.
    """

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

        if value and value not in cleaned:

            cleaned.append(
                value
            )

    return cleaned


# ============================================================
# CREATE SAFETY STATE
# ============================================================

def create_safety_state() -> Dict[str, Any]:
    """
    Create a clean session safety state.
    """

    return {

        "level":
            SAFETY_LEVEL_UNESTABLISHED,

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
# BUILD EVIDENCE TEXT
# ============================================================

def _combined_evidence_text(
    item: Dict[str, Any]
) -> str:
    """
    Combine structured value and supporting evidence text
    for deterministic checks.
    """

    value = item.get(
        "value"
    )

    evidence_text = item.get(
        "evidence_text"
    )

    return (
        f"{value or ''} "
        f"{evidence_text or ''}"
    ).strip()


# ============================================================
# VALIDATE SAFETY EVIDENCE
# ============================================================

def _normalise_safety_evidence(
    clinical_evidence: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter evidence down to safety-relevant domains and
    normalise its structure.

    Weak evidence below 0.5 confidence does not drive safety
    decisions.
    """

    safety_evidence = []

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

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

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

        if confidence < 0.5:
            continue

        # ----------------------------------------------------
        # Evidence record
        # ----------------------------------------------------

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

    return safety_evidence


# ============================================================
# COLLECT FLAGS
# ============================================================

def _collect_flags(
    safety_evidence: List[Dict[str, Any]]
) -> List[str]:
    """
    Collect unique flags from safety evidence.
    """

    flags = []

    for item in safety_evidence:

        for flag in item.get(
            "flags",
            []
        ):

            if flag not in flags:

                flags.append(
                    flag
                )

    return flags


# ============================================================
# REFERRAL REQUIREMENT CHECK
# ============================================================

def _requires_referral_review(
    value: Any
) -> bool:
    """
    Determine whether established referral/permission evidence
    indicates review may be required.

    Uncertainty and explicit negative information do not trigger
    review.
    """

    text = _normalise_text(
        value
    )

    if not text:
        return False

    if _is_uncertain(
        text
    ):
        return False

    if _is_explicit_negative(
        text
    ):
        return False

    referral_terms = {

        "required",
        "needed",

        "need permission",
        "requires permission",

        "professional advice",
        "medical advice",

        "refer",
        "referral",

    }

    return any(
        term in text
        for term in referral_terms
    )


# ============================================================
# EXPLICIT FLAG REQUIRES ATTENTION
# ============================================================

def _valid_attention_flag(
    item: Dict[str, Any],
    flag: str,
) -> bool:
    """
    Determine whether an explicit flag is supported by
    non-uncertain, non-negative evidence.
    """

    value = item.get(
        "value"
    )

    if _is_uncertain(
        value
    ):
        return False

    if _is_explicit_negative(
        value
    ):
        return False

    return True


# ============================================================
# EVALUATE SAFETY
# ============================================================

def evaluate_safety(
    clinical_evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate safety information already extracted from the
    therapist/client conversation.

    This function does NOT create new clinical evidence.
    """

    state = create_safety_state()

    if not isinstance(
        clinical_evidence,
        list
    ):
        return state

    # ========================================================
    # FILTER SAFETY EVIDENCE
    # ========================================================

    safety_evidence = (
        _normalise_safety_evidence(
            clinical_evidence
        )
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
    # FLAGS
    # ========================================================

    state["flags"] = _collect_flags(
        safety_evidence
    )

    # ========================================================
    # NO SAFETY EVIDENCE
    # ========================================================

    if not safety_evidence:

        state["level"] = (
            SAFETY_LEVEL_UNESTABLISHED
        )

        return state

    # ========================================================
    # INFORMATION EXISTS
    # ========================================================

    state["level"] = (
        SAFETY_LEVEL_INFORMATION
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
        # Unknown / uncertain
        # ----------------------------------------------------

        if _is_uncertain(
            value
        ):
            continue

        # ----------------------------------------------------
        # Explicit negative
        # ----------------------------------------------------

        if _is_explicit_negative(
            value
        ):
            continue

        # ----------------------------------------------------
        # Explicit positive risk
        # ----------------------------------------------------

        if _is_positive_risk(
            value
        ):

            state["requires_attention"] = True

            state["level"] = (
                SAFETY_LEVEL_REVIEW
            )

    # ========================================================
    # CONTRAINDICATIONS
    # ========================================================

    contraindication_items = [
        item
        for item in safety_evidence
        if item["domain"] == "contraindications"
    ]

    for item in contraindication_items:

        value = item.get(
            "value"
        )

        # ----------------------------------------------------
        # Explicit negative
        # ----------------------------------------------------

        if _is_explicit_negative(
            value
        ):
            continue

        # ----------------------------------------------------
        # Unknown
        # ----------------------------------------------------

        if _is_uncertain(
            value
        ):
            continue

        # ----------------------------------------------------
        # Established contraindication
        # ----------------------------------------------------

        state["requires_attention"] = True

        state["requires_referral_review"] = True

        state["level"] = (
            SAFETY_LEVEL_REVIEW
        )

    # ========================================================
    # SAFEGUARDING
    # ========================================================

    safeguarding_items = [
        item
        for item in safety_evidence
        if item["domain"] == "safeguarding"
    ]

    for item in safeguarding_items:

        value = item.get(
            "value"
        )

        # ----------------------------------------------------
        # Explicit negative
        # ----------------------------------------------------

        if _is_explicit_negative(
            value
        ):
            continue

        # ----------------------------------------------------
        # Unknown
        # ----------------------------------------------------

        if _is_uncertain(
            value
        ):
            continue

        # ----------------------------------------------------
        # Established safeguarding information
        # ----------------------------------------------------

        state["requires_attention"] = True

        state[
            "requires_safeguarding_review"
        ] = True

        state["level"] = (
            SAFETY_LEVEL_REVIEW
        )

    # ========================================================
    # REFERRAL / PERMISSION
    # ========================================================

    referral_items = [
        item
        for item in safety_evidence
        if item["domain"] == "referral_permission"
    ]

    for item in referral_items:

        value = item.get(
            "value"
        )

        if _requires_referral_review(
            value
        ):

            state["requires_attention"] = True

            state[
                "requires_referral_review"
            ] = True

            state["level"] = (
                SAFETY_LEVEL_REVIEW
            )

    # ========================================================
    # EXPLICIT FLAGS
    # ========================================================

    attention_flags = {
        "risk",
        "risk_positive",

        "safety_concern",
        "safety_risk",

        "contraindication",
        "contraindications",

        "safeguarding",
        "safeguarding_positive",

        "referral_required",
        "professional_review_required",
    }

    for item in safety_evidence:

        item_flags = {
            str(flag).strip().lower()
            for flag in item.get(
                "flags",
                []
            )
        }

        matching_flags = (
            item_flags
            & attention_flags
        )

        for flag in matching_flags:

            if not _valid_attention_flag(
                item,
                flag,
            ):
                continue

            state["requires_attention"] = True

            state["level"] = (
                SAFETY_LEVEL_REVIEW
            )

            if flag in {
                "safeguarding",
                "safeguarding_positive",
            }:

                state[
                    "requires_safeguarding_review"
                ] = True

            if flag in {
                "contraindication",
                "contraindications",
                "referral_required",
                "professional_review_required",
            }:

                state[
                    "requires_referral_review"
                ] = True

    # ========================================================
    # RETURN
    # ========================================================

    return state