from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# PHASE 2B EVIDENCE DOMAINS
# ============================================================

EVIDENCE_DOMAINS = {
    "presenting_problem": "Presenting Problem",
    "history": "History and Development",
    "symptoms": "Symptoms",
    "triggers": "Triggers",
    "maintaining_factors": "Maintaining Factors",
    "functional_impact": "Functional Impact",
    "coping_strategies": "Coping Strategies",

    "previous_hypnosis": "Previous Hypnosis Experience",

    "medical_history": "Medical History",
    "psychological_care": "Psychological Care",
    "psychiatric_care": "Psychiatric Care",
    "medication": "Medication and Medical Management",
    "healthcare_professionals": "External Healthcare Professionals",
    "referral_permission": "Permission / Referral Requirements",

    "why_now": "Motivation for Change / Why Now",
    "readiness": "Readiness for Treatment",
    "goals": "Treatment Goals",

    "risk": "Risk",
    "contraindications": "Contraindications",
    "safeguarding": "Safeguarding",
    "professional_boundaries": "Professional Boundaries",

    "modality": "Communication Modality",
    "treatment_reasoning": "Treatment Reasoning",
}


# ============================================================
# EVIDENCE MATURITY
# ============================================================

EVIDENCE_LEVELS = {
    "not_explored": 0,
    "mentioned": 1,
    "clarified": 2,
    "understood": 3,
    "applied": 4,
    "integrated": 5,
}


# ============================================================
# VALID VALUES
# ============================================================

ALLOWED_STATUSES = set(EVIDENCE_LEVELS.keys())

ALLOWED_SAFETY_SEVERITIES = {
    "review",
    "moderate",
    "high",
    "critical",
}


# ============================================================
# TIMESTAMP
# ============================================================

def _utc_timestamp() -> str:
    """
    Return a timezone-aware UTC timestamp.

    Used for audit/history records.
    """

    return datetime.now(timezone.utc).isoformat()


# ============================================================
# EMPTY DOMAIN
# ============================================================

def _empty_domain(domain_key: str) -> Dict[str, Any]:
    """
    Create a clean evidence record for one domain.

    IMPORTANT:

    None means evidence has not been established.

    It does NOT mean:
    - no
    - negative
    - absent
    - never
    """

    return {
        "domain": domain_key,
        "label": EVIDENCE_DOMAINS[domain_key],

        "value": None,

        "status": "not_explored",
        "level": EVIDENCE_LEVELS["not_explored"],
        "confidence": 0.0,

        # Individual pieces of conversational evidence.
        "evidence": [],

        # Educational/clinical explanation of why the evidence matters.
        "clinical_significance": None,

        # Whether the student has used this evidence in reasoning.
        "applied_to_reasoning": False,

        # Domain-level review/safety markers.
        "flags": [],

        "last_updated": None,
    }


# ============================================================
# CREATE EVIDENCE STATE
# ============================================================

def create_evidence_state(
    client_name: Optional[str] = None,
    condition: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a fresh Phase 2B Clinical Evidence Model.

    The state is designed to accumulate evidence throughout
    the consultation.
    """

    now = _utc_timestamp()

    return {
        "client_name": client_name,
        "condition": condition,

        "created_at": now,
        "updated_at": now,

        "domains": {
            key: _empty_domain(key)
            for key in EVIDENCE_DOMAINS
        },

        # Complete chronological audit trail.
        "history": [],

        # Session-level safety/review markers.
        "safety_flags": [],

        # Evidence that has been raised but requires clarification.
        "unresolved_evidence": [],
    }


# ============================================================
# GET DOMAIN
# ============================================================

def get_domain(
    evidence_state: Dict[str, Any],
    domain: str,
) -> Dict[str, Any]:
    """
    Return one evidence domain.
    """

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(
            f"Unknown evidence domain: {domain}"
        )

    return evidence_state["domains"][domain]


# ============================================================
# NORMALISE CONFIDENCE
# ============================================================

def _normalise_confidence(
    confidence: Any,
) -> float:
    """
    Safely normalise confidence to the range 0.0–1.0.
    """

    try:
        value = float(confidence)
    except (TypeError, ValueError):
        value = 0.0

    return max(
        0.0,
        min(value, 1.0)
    )


# ============================================================
# UPDATE EVIDENCE
# ============================================================

def update_evidence(
    evidence_state: Dict[str, Any],
    domain: str,
    value: Any,
    status: str = "mentioned",
    confidence: float = 0.5,
    evidence_text: Optional[str] = None,
    clinical_significance: Optional[str] = None,
    applied_to_reasoning: bool = False,
    flags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Add or update evidence for a domain.

    IMPORTANT:

    Evidence is cumulative.

    A later weaker extraction must not erase stronger evidence that
    has already been established.

    The function stores evidence but does not independently decide
    whether that evidence is clinically correct.
    """

    # --------------------------------------------------------
    # Validate domain
    # --------------------------------------------------------

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(
            f"Unknown evidence domain: {domain}"
        )

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Unknown evidence status: {status}. "
            f"Expected one of: {sorted(ALLOWED_STATUSES)}"
        )

    # --------------------------------------------------------
    # Normalise confidence
    # --------------------------------------------------------

    confidence = _normalise_confidence(
        confidence
    )

    record = evidence_state["domains"][domain]

    previous_record = deepcopy(record)

    previous_level = int(
        record.get("level", 0)
    )

    incoming_level = EVIDENCE_LEVELS[status]

    previous_confidence = float(
        record.get("confidence", 0.0)
    )

    # ========================================================
    # VALUE
    # ========================================================

    # Do not overwrite an established value with None.

    if value is not None:
        record["value"] = value

    # ========================================================
    # STATUS / MATURITY
    # ========================================================

    # Evidence maturity only moves forward.

    if incoming_level >= previous_level:
        record["status"] = status
        record["level"] = incoming_level

    # If incoming evidence is weaker, retain the stronger
    # previously established maturity.

    # ========================================================
    # CONFIDENCE
    # ========================================================

    # Preserve the highest confidence established so far.

    record["confidence"] = max(
        previous_confidence,
        confidence,
    )

    # ========================================================
    # APPLIED TO REASONING
    # ========================================================

    # Once evidence has been used in reasoning, do not revert it.

    record["applied_to_reasoning"] = bool(
        record.get("applied_to_reasoning", False)
        or applied_to_reasoning
    )

    # ========================================================
    # EVIDENCE TEXT
    # ========================================================

    if evidence_text:
        evidence_text = str(
            evidence_text
        ).strip()

        if evidence_text:
            if evidence_text not in record["evidence"]:
                record["evidence"].append(
                    evidence_text
                )

    # ========================================================
    # CLINICAL SIGNIFICANCE
    # ========================================================

    if clinical_significance is not None:

        significance = str(
            clinical_significance
        ).strip()

        if significance:
            record["clinical_significance"] = (
                significance
            )

    # ========================================================
    # FLAGS
    # ========================================================

    if flags:

        for flag in flags:

            if flag is None:
                continue

            flag = str(flag).strip()

            if not flag:
                continue

            if flag not in record["flags"]:
                record["flags"].append(
                    flag
                )

    # ========================================================
    # TIMESTAMP
    # ========================================================

    record["last_updated"] = _utc_timestamp()

    # ========================================================
    # AUDIT HISTORY
    # ========================================================

    evidence_state["history"].append({
        "timestamp": _utc_timestamp(),

        "domain": domain,

        "previous": previous_record,

        "current": deepcopy(record),
    })

    evidence_state["updated_at"] = _utc_timestamp()

    # ========================================================
    # AUTOMATIC UNRESOLVED CLEANUP
    # ========================================================

    # If meaningful evidence has now been established,
    # remove unresolved markers for this domain.

    if incoming_level >= EVIDENCE_LEVELS["clarified"]:

        evidence_state["unresolved_evidence"] = [
            item
            for item in evidence_state[
                "unresolved_evidence"
            ]
            if item["domain"] != domain
        ]

    return record


# ============================================================
# ADD SAFETY FLAG
# ============================================================

def add_safety_flag(
    evidence_state: Dict[str, Any],
    flag: str,
    domain: Optional[str] = None,
    severity: str = "review",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add a session-level safety/review flag.

    This function records the flag.

    It does NOT independently decide whether a safety concern
    exists. That responsibility belongs to the dedicated
    Risk & Safety Engine.
    """

    # --------------------------------------------------------
    # Validate severity
    # --------------------------------------------------------

    if severity not in ALLOWED_SAFETY_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{severity}'. "
            f"Expected one of: "
            f"{sorted(ALLOWED_SAFETY_SEVERITIES)}"
        )

    # --------------------------------------------------------
    # Validate domain
    # --------------------------------------------------------

    if domain is not None:

        if domain not in EVIDENCE_DOMAINS:
            raise ValueError(
                f"Unknown evidence domain: {domain}"
            )

    # --------------------------------------------------------
    # Validate flag
    # --------------------------------------------------------

    if not flag or not str(flag).strip():
        raise ValueError(
            "Safety flag cannot be empty."
        )

    flag = str(flag).strip()

    # --------------------------------------------------------
    # Create record
    # --------------------------------------------------------

    safety_record = {
        "flag": flag,
        "domain": domain,
        "severity": severity,
        "reason": reason,
        "timestamp": _utc_timestamp(),
    }

    # --------------------------------------------------------
    # Prevent duplicate logical flags
    # --------------------------------------------------------

    duplicate = any(
        existing.get("flag") == flag
        and existing.get("domain") == domain
        and existing.get("severity") == severity
        for existing in evidence_state["safety_flags"]
    )

    if not duplicate:
        evidence_state["safety_flags"].append(
            safety_record
        )

    # --------------------------------------------------------
    # Add flag to domain
    # --------------------------------------------------------

    if domain:

        domain_record = evidence_state[
            "domains"
        ][domain]

        if flag not in domain_record["flags"]:
            domain_record["flags"].append(
                flag
            )

        domain_record["last_updated"] = (
            _utc_timestamp()
        )

    evidence_state["updated_at"] = _utc_timestamp()

    return safety_record


# ============================================================
# MARK UNRESOLVED
# ============================================================

def mark_unresolved(
    evidence_state: Dict[str, Any],
    domain: str,
    reason: str,
) -> None:
    """
    Mark evidence that requires clarification.

    Unresolved does not mean negative.

    It means the issue has been raised but is not sufficiently
    established yet.
    """

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(
            f"Unknown evidence domain: {domain}"
        )

    reason = str(reason).strip()

    item = {
        "domain": domain,
        "reason": reason,
    }

    if item not in evidence_state[
        "unresolved_evidence"
    ]:
        evidence_state[
            "unresolved_evidence"
        ].append(item)

    evidence_state["updated_at"] = _utc_timestamp()


# ============================================================
# RESOLVE UNRESOLVED
# ============================================================

def resolve_unresolved(
    evidence_state: Dict[str, Any],
    domain: str,
) -> None:
    """
    Remove unresolved markers for a domain.
    """

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(
            f"Unknown evidence domain: {domain}"
        )

    evidence_state[
        "unresolved_evidence"
    ] = [
        item
        for item in evidence_state[
            "unresolved_evidence"
        ]
        if item.get("domain") != domain
    ]

    evidence_state["updated_at"] = _utc_timestamp()


# ============================================================
# EVIDENCE COMPLETION SUMMARY
# ============================================================

def evidence_completion_summary(
    evidence_state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Produce a session evidence summary.

    This is NOT a tutor score.

    It only describes how much evidence has been established.
    """

    domains = evidence_state["domains"]

    total_domains = len(domains)

    # --------------------------------------------------------
    # Explored
    # --------------------------------------------------------

    explored = [
        key
        for key, record in domains.items()
        if record["level"]
        >= EVIDENCE_LEVELS["mentioned"]
    ]

    # --------------------------------------------------------
    # Clarified
    # --------------------------------------------------------

    clarified = [
        key
        for key, record in domains.items()
        if record["level"]
        >= EVIDENCE_LEVELS["clarified"]
    ]

    # --------------------------------------------------------
    # Understood
    # --------------------------------------------------------

    understood = [
        key
        for key, record in domains.items()
        if record["level"]
        >= EVIDENCE_LEVELS["understood"]
    ]

    # --------------------------------------------------------
    # Applied
    # --------------------------------------------------------

    applied = [
        key
        for key, record in domains.items()
        if (
            record["level"]
            >= EVIDENCE_LEVELS["applied"]
        )
        or record["applied_to_reasoning"]
    ]

    # --------------------------------------------------------
    # Integrated
    # --------------------------------------------------------

    integrated = [
        key
        for key, record in domains.items()
        if record["level"]
        >= EVIDENCE_LEVELS["integrated"]
    ]

    # --------------------------------------------------------
    # Not explored
    # --------------------------------------------------------

    not_explored = [
        key
        for key in domains
        if key not in explored
    ]

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "total_domains": total_domains,

        "explored_count": len(explored),
        "clarified_count": len(clarified),
        "understood_count": len(understood),
        "applied_count": len(applied),
        "integrated_count": len(integrated),

        "explored_domains": explored,

        "not_explored_domains": not_explored,

        "clarified_domains": clarified,

        "understood_domains": understood,

        "applied_domains": applied,

        "integrated_domains": integrated,

        "unresolved_evidence": deepcopy(
            evidence_state[
                "unresolved_evidence"
            ]
        ),

        "safety_flags": deepcopy(
            evidence_state[
                "safety_flags"
            ]
        ),
    }


# ============================================================
# TUTOR EVIDENCE
# ============================================================

def get_evidence_for_tutor(
    evidence_state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Return a clean immutable-style snapshot for Tutor Mode.

    The tutor receives the evidence record but this function does
    not calculate a final pass/fail/verified decision.
    """

    return {
        "client_name": evidence_state.get(
            "client_name"
        ),

        "condition": evidence_state.get(
            "condition"
        ),

        "domains": deepcopy(
            evidence_state["domains"]
        ),

        "safety_flags": deepcopy(
            evidence_state["safety_flags"]
        ),

        "unresolved_evidence": deepcopy(
            evidence_state[
                "unresolved_evidence"
            ]
        ),

        "summary": evidence_completion_summary(
            evidence_state
        ),
    }


# ============================================================
# EVIDENCE HISTORY
# ============================================================

def get_evidence_history(
    evidence_state: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Return the chronological evidence audit trail.
    """

    return deepcopy(
        evidence_state.get(
            "history",
            []
        )
    )