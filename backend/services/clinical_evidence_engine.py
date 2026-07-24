from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# Phase 2B evidence domains.
#
# These are intentionally broader than the original Phase 2A scoring fields.
# The engine records whether evidence has actually been established during
# the consultation rather than assuming that missing information means "no".
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


# Evidence maturity follows a progressive model.
# A domain can move from being merely mentioned to being integrated
# into clinical reasoning.
EVIDENCE_LEVELS = {
    "not_explored": 0,
    "mentioned": 1,
    "clarified": 2,
    "understood": 3,
    "applied": 4,
    "integrated": 5,
}


def _utc_timestamp() -> str:
    """Return a timezone-aware timestamp for audit/history records."""
    return datetime.now(timezone.utc).isoformat()


def _empty_domain(domain_key: str) -> Dict[str, Any]:
    """Create a clean evidence record for one assessment domain."""
    return {
        "domain": domain_key,
        "label": EVIDENCE_DOMAINS[domain_key],

        # Important:
        # None means the evidence has not yet been established.
        # It does NOT mean "no".
        "value": None,

        "status": "not_explored",
        "level": EVIDENCE_LEVELS["not_explored"],
        "confidence": 0.0,

        # What in the conversation supports the evidence.
        "evidence": [],

        # Why this evidence matters clinically/educationally.
        "clinical_significance": None,

        # Whether the student has used the evidence in reasoning.
        "applied_to_reasoning": False,

        # Potential safety/review markers.
        "flags": [],

        "last_updated": None,
    }


def create_evidence_state(
    client_name: Optional[str] = None,
    condition: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a fresh Phase 2B Clinical Evidence Model for a session.
    """

    return {
        "client_name": client_name,
        "condition": condition,
        "created_at": _utc_timestamp(),
        "updated_at": _utc_timestamp(),

        "domains": {
            key: _empty_domain(key)
            for key in EVIDENCE_DOMAINS
        },

        # Chronological record of evidence changes.
        "history": [],

        # Session-level safety markers.
        "safety_flags": [],

        # Evidence that still needs clarification.
        "unresolved_evidence": [],
    }


def get_domain(
    evidence_state: Dict[str, Any],
    domain: str,
) -> Dict[str, Any]:
    """Return one evidence domain."""

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(f"Unknown evidence domain: {domain}")

    return evidence_state["domains"][domain]


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
    Add or update evidence for a clinical domain.

    This function does not decide whether the evidence is clinically
    correct. It stores structured evidence established elsewhere by
    the conversation/evidence extraction process.
    """

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(f"Unknown evidence domain: {domain}")

    if status not in EVIDENCE_LEVELS:
        raise ValueError(f"Unknown evidence status: {status}")

    confidence = max(0.0, min(float(confidence), 1.0))

    record = evidence_state["domains"][domain]

    previous_record = deepcopy(record)

    record["value"] = value
    record["status"] = status
    record["level"] = EVIDENCE_LEVELS[status]
    record["confidence"] = confidence
    record["applied_to_reasoning"] = applied_to_reasoning
    record["last_updated"] = _utc_timestamp()

    if evidence_text:
        if evidence_text not in record["evidence"]:
            record["evidence"].append(evidence_text)

    if clinical_significance is not None:
        record["clinical_significance"] = clinical_significance

    if flags:
        for flag in flags:
            if flag not in record["flags"]:
                record["flags"].append(flag)

    evidence_state["history"].append({
        "timestamp": _utc_timestamp(),
        "domain": domain,
        "previous": previous_record,
        "current": deepcopy(record),
    })

    evidence_state["updated_at"] = _utc_timestamp()

    return record


def add_safety_flag(
    evidence_state: Dict[str, Any],
    flag: str,
    domain: Optional[str] = None,
    severity: str = "review",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add a session-level safety flag.

    Actual safety decisions will later belong to the dedicated
    Risk & Safety Engine.
    """

    allowed_severity = {"review", "moderate", "high", "critical"}

    if severity not in allowed_severity:
        raise ValueError(
            f"Invalid severity '{severity}'. "
            f"Expected one of: {sorted(allowed_severity)}"
        )

    safety_record = {
        "flag": flag,
        "domain": domain,
        "severity": severity,
        "reason": reason,
        "timestamp": _utc_timestamp(),
    }

    if safety_record not in evidence_state["safety_flags"]:
        evidence_state["safety_flags"].append(safety_record)

    if domain:
        if domain not in EVIDENCE_DOMAINS:
            raise ValueError(f"Unknown evidence domain: {domain}")

        domain_record = evidence_state["domains"][domain]

        if flag not in domain_record["flags"]:
            domain_record["flags"].append(flag)

    evidence_state["updated_at"] = _utc_timestamp()

    return safety_record


def mark_unresolved(
    evidence_state: Dict[str, Any],
    domain: str,
    reason: str,
) -> None:
    """
    Mark evidence that has been raised but still needs clarification.
    """

    if domain not in EVIDENCE_DOMAINS:
        raise ValueError(f"Unknown evidence domain: {domain}")

    item = {
        "domain": domain,
        "reason": reason,
    }

    if item not in evidence_state["unresolved_evidence"]:
        evidence_state["unresolved_evidence"].append(item)

    evidence_state["updated_at"] = _utc_timestamp()


def resolve_unresolved(
    evidence_state: Dict[str, Any],
    domain: str,
) -> None:
    """Remove unresolved markers for a domain."""

    evidence_state["unresolved_evidence"] = [
        item
        for item in evidence_state["unresolved_evidence"]
        if item["domain"] != domain
    ]

    evidence_state["updated_at"] = _utc_timestamp()


def evidence_completion_summary(
    evidence_state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Produce a simple session evidence summary.

    This is NOT the final Tutor Mode score.
    Tutor Mode will later apply Ursula's assessment matrix,
    weighting, safety overrides and educational judgement.
    """

    domains = evidence_state["domains"]

    total_domains = len(domains)

    explored = [
        key
        for key, value in domains.items()
        if value["status"] != "not_explored"
    ]

    clarified = [
        key
        for key, value in domains.items()
        if value["level"] >= EVIDENCE_LEVELS["clarified"]
    ]

    applied = [
        key
        for key, value in domains.items()
        if value["level"] >= EVIDENCE_LEVELS["applied"]
        or value["applied_to_reasoning"]
    ]

    return {
        "total_domains": total_domains,
        "explored_count": len(explored),
        "clarified_count": len(clarified),
        "applied_count": len(applied),

        "explored_domains": explored,
        "not_explored_domains": [
            key
            for key in domains
            if key not in explored
        ],

        "unresolved_evidence": deepcopy(
            evidence_state["unresolved_evidence"]
        ),

        "safety_flags": deepcopy(
            evidence_state["safety_flags"]
        ),
    }


def get_evidence_for_tutor(
    evidence_state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Return a clean copy for the future Tutor Mode 2.0 assessment engine.
    """

    return {
        "client_name": evidence_state.get("client_name"),
        "condition": evidence_state.get("condition"),
        "domains": deepcopy(evidence_state["domains"]),
        "safety_flags": deepcopy(evidence_state["safety_flags"]),
        "unresolved_evidence": deepcopy(
            evidence_state["unresolved_evidence"]
        ),
        "summary": evidence_completion_summary(evidence_state),
    }