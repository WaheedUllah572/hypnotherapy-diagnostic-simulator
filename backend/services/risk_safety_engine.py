from typing import Any, Dict, List


# ============================================================
# PHASE 2B — CLINICAL RISK & SAFETY ENGINE
# ============================================================
#
# This engine DOES NOT diagnose.
# It DOES NOT infer risk from therapist questions.
#
# It evaluates only clinical evidence that has already been
# established by the Clinical Evidence Engine.
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


def create_safety_state() -> Dict[str, Any]:
    """
    Create a fresh safety state for a consultation session.
    """

    return {
        "level": "unestablished",
        "requires_attention": False,
        "requires_referral_review": False,
        "requires_safeguarding_review": False,
        "evidence": [],
        "flags": [],
        "established_domains": [],
    }


def _normalise_flags(flags: Any) -> List[str]:
    """
    Ensure flags are represented as a clean list of strings.
    """

    if not isinstance(flags, list):
        return []

    cleaned = []

    for flag in flags:
        if flag is None:
            continue

        value = str(flag).strip()

        if value and value not in cleaned:
            cleaned.append(value)

    return cleaned


def _is_meaningful_value(value: Any) -> bool:
    """
    Determine whether an evidence value contains an actual
    established fact.

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
        }

        if text in unknown_values:
            return False

    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0

    return True


def evaluate_safety(
    clinical_evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate established clinical evidence and produce a structured
    safety state.

    IMPORTANT:
    - Therapist questions alone are not evidence.
    - Unknown client answers are not evidence.
    - The engine does not invent positive or negative risk findings.
    - Empty evidence means safety is UNESTABLISHED, not automatically safe.
    """

    state = create_safety_state()

    if not isinstance(clinical_evidence, list):
        return state

    safety_evidence = []

    for item in clinical_evidence:

        if not isinstance(item, dict):
            continue

        domain = item.get("domain")

        if domain not in SAFETY_DOMAINS:
            continue

        value = item.get("value")

        if not _is_meaningful_value(value):
            continue

        try:
            confidence = float(
                item.get("confidence", 0.0)
            )
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(
            0.0,
            min(confidence, 1.0)
        )

        # Very weak/ambiguous extraction should not drive
        # clinical safety behaviour.
        if confidence < 0.5:
            continue

        evidence_item = {
            "domain": domain,
            "value": value,
            "status": item.get(
                "status",
                "mentioned"
            ),
            "confidence": confidence,
            "evidence_text": item.get(
                "evidence_text"
            ),
            "clinical_significance": item.get(
                "clinical_significance"
            ),
            "flags": _normalise_flags(
                item.get("flags", [])
            ),
        }

        safety_evidence.append(evidence_item)

    state["evidence"] = safety_evidence

    state["established_domains"] = list(
        dict.fromkeys(
            item["domain"]
            for item in safety_evidence
        )
    )

    # ========================================================
    # COLLECT EXPLICIT FLAGS
    # ========================================================

    all_flags = []

    for item in safety_evidence:
        for flag in item["flags"]:
            if flag not in all_flags:
                all_flags.append(flag)

    state["flags"] = all_flags

    # ========================================================
    # STRUCTURED SAFETY INTERPRETATION
    # ========================================================

    if not safety_evidence:
        # No established safety evidence does NOT mean
        # that the client has been assessed as safe.
        state["level"] = "unestablished"
        return state

    state["level"] = "information_established"

    # --------------------------------------------------------
    # Direct safety/risk evidence
    # --------------------------------------------------------

    risk_items = [
        item
        for item in safety_evidence
        if item["domain"] == "risk"
    ]

    if risk_items:
        state["requires_attention"] = True
        state["level"] = "review_required"

    # --------------------------------------------------------
    # Contraindications
    # --------------------------------------------------------

    contraindication_items = [
        item
        for item in safety_evidence
        if item["domain"] == "contraindications"
    ]

    if contraindication_items:
        state["requires_attention"] = True
        state["requires_referral_review"] = True
        state["level"] = "review_required"

    # --------------------------------------------------------
    # Safeguarding
    # --------------------------------------------------------

    safeguarding_items = [
        item
        for item in safety_evidence
        if item["domain"] == "safeguarding"
    ]

    if safeguarding_items:
        state["requires_attention"] = True
        state["requires_safeguarding_review"] = True
        state["level"] = "review_required"

    # --------------------------------------------------------
    # Explicit referral / permission evidence
    # --------------------------------------------------------

    referral_items = [
        item
        for item in safety_evidence
        if item["domain"] == "referral_permission"
    ]

    if referral_items:

        for item in referral_items:

            value_text = str(
                item["value"]
            ).lower()

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
                state["level"] = "review_required"

    # --------------------------------------------------------
    # Explicit extractor flags
    # --------------------------------------------------------

    attention_flags = {
        "risk",
        "safety_concern",
        "contraindication",
        "safeguarding",
        "referral_required",
        "professional_review_required",
    }

    if any(
        flag.lower() in attention_flags
        for flag in all_flags
    ):
        state["requires_attention"] = True
        state["level"] = "review_required"

    return state