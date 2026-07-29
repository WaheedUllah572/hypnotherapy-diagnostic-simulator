from typing import Any, Dict, List, Optional


# ============================================================
# PROTECTED CLINICAL DOMAINS
# ============================================================

PROTECTED_DOMAINS = {
    "medication",
    "medical_history",
    "psychological_care",
    "psychiatric_care",
    "healthcare_professionals",
    "previous_hypnosis",
    "referral_permission",
    "risk",
    "contraindications",
    "safeguarding",
}


# ============================================================
# QUESTION → DOMAIN DETECTION
# ============================================================

def detect_unknown_domain(student_text: str) -> Optional[str]:
    """
    Detect whether the therapist is asking about a protected
    clinical-history/safety domain.

    This does NOT decide whether the answer is known or unknown.
    """

    text = (student_text or "").lower()

    # --------------------------------------------------------
    # RISK / HARM
    # Check before generic medical/psychological detection.
    # --------------------------------------------------------

    if any(x in text for x in [
        "harm yourself",
        "harm myself",
        "harming yourself",
        "hurt yourself",
        "hurt myself",
        "suicidal",
        "suicide",
        "self-harm",
        "self harm",
        "harm anyone else",
        "harm someone else",
        "hurt anyone else",
        "hurt someone else",
        "thoughts of harming",
    ]):
        return "risk"

    # --------------------------------------------------------
    # SAFEGUARDING
    # --------------------------------------------------------

    if any(x in text for x in [
        "safeguarding",
        "abuse",
        "being harmed",
        "someone hurting you",
        "feel safe at home",
        "safe at home",
    ]):
        return "safeguarding"

    # --------------------------------------------------------
    # CONTRAINDICATION / SUITABILITY
    # --------------------------------------------------------

    if any(x in text for x in [
        "unsuitable",
        "contraindication",
        "contraindications",
        "make hypnotherapy unsafe",
        "make hypnosis unsafe",
        "might prevent hypnotherapy",
        "additional professional advice",
        "medical or psychological history that might",
    ]):
        return "contraindications"

    # --------------------------------------------------------
    # MEDICATION
    # --------------------------------------------------------

    if any(x in text for x in [
        "medication",
        "medications",
        "medicine",
        "medicines",
        "prescription",
        "prescribed",
        "taking any tablets",
    ]):
        return "medication"

    # --------------------------------------------------------
    # PREVIOUS HYPNOSIS
    # --------------------------------------------------------

    if any(x in text for x in [
        "had hypnotherapy before",
        "had hypnosis before",
        "previous hypnotherapy",
        "previous hypnosis",
        "experienced hypnotherapy",
        "experienced hypnosis",
    ]):
        return "previous_hypnosis"

    # --------------------------------------------------------
    # PSYCHIATRIC CARE
    # --------------------------------------------------------

    if any(x in text for x in [
        "psychiatric care",
        "psychiatrist",
        "psychiatric treatment",
        "mental health psychiatrist",
    ]):
        return "psychiatric_care"

    # --------------------------------------------------------
    # PSYCHOLOGICAL CARE
    # --------------------------------------------------------

    if any(x in text for x in [
        "psychological care",
        "psychological treatment",
        "psychologist",
        "seeing a therapist",
        "seeing a counsellor",
        "seeing a counselor",
        "currently in therapy",
        "receiving therapy",
    ]):
        return "psychological_care"

    # --------------------------------------------------------
    # HEALTHCARE PROFESSIONALS
    # --------------------------------------------------------

    if any(x in text for x in [
        "healthcare professional",
        "healthcare professionals",
        "doctor involved",
        "doctors involved",
        "professional involved",
        "professionals involved",
        "supporting you medically",
        "involved in supporting you",
    ]):
        return "healthcare_professionals"

    # --------------------------------------------------------
    # REFERRAL / PERMISSION
    # --------------------------------------------------------

    if any(x in text for x in [
        "referral",
        "permission",
        "medical clearance",
        "doctor's permission",
        "doctors permission",
        "gp permission",
        "gp referral",
    ]):
        return "referral_permission"

    # --------------------------------------------------------
    # GENERAL MEDICAL HISTORY
    # --------------------------------------------------------

    if any(x in text for x in [
        "medical history",
        "medical condition",
        "medical conditions",
        "physical health condition",
        "health condition",
        "health problems",
    ]):
        return "medical_history"

    return None


# ============================================================
# GET AUTHORITATIVE VALUE FOR DOMAIN
# ============================================================

def get_domain_value(
    persona: Dict[str, Any],
    domain: str
) -> Any:
    """
    Read the relevant value directly from the authoritative
    case structure.
    """

    healthcare = persona.get("healthcare", {})
    hypnosis_history = persona.get("hypnosis_history", {})
    safety = persona.get("safety", {})

    medication = healthcare.get("medication", {})

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
            healthcare.get("referral_or_permission_required"),

        "risk":
            safety.get("risk_factors"),

        "contraindications":
            safety.get("contraindications"),

        "safeguarding":
            safety.get("safeguarding_concerns"),
    }

    return mapping.get(domain)


# ============================================================
# DETERMINE WHETHER CASE VALUE IS UNESTABLISHED
# ============================================================

def is_unestablished(value: Any) -> bool:
    """
    Null or empty protected fields mean that the authored case
    has not established a definite positive OR negative fact.

    They must therefore not automatically become "No".
    """

    if value is None:
        return True

    if isinstance(value, list) and len(value) == 0:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    return False


# ============================================================
# DOMAIN-SPECIFIC CONVERSATIONAL GUIDANCE
# ============================================================

DOMAIN_GUIDANCE = {

    "medication": """
The therapist is asking about current medication.

The authored case does not establish a definite medication status.

Respond as a real client who cannot confidently give a definite
medication answer at this point.

Do not say:
- "the case"
- "not established"
- "not specified"
- "no information is available"

Do not invent a medication and do not claim definitely that you take
no medication.

Use natural first-person uncertainty. If appropriate, indicate that
this is something that may need checking or clarifying.
""",

    "medical_history": """
The therapist is asking about medical history.

The authored case does not establish a definite answer.

Respond naturally as the client without inventing a diagnosis,
condition or clean medical history.

Do not describe internal simulator information.

If appropriate, communicate that you would need to think about,
check, or clarify the relevant history.
""",

    "psychological_care": """
The therapist is asking about current or previous psychological care.

The authored case does not establish a definite answer.

Do not invent therapy, counselling or psychological treatment.
Do not claim definitely that none has occurred.

Respond in natural first-person language and allow the therapist
to continue clarifying the history.
""",

    "psychiatric_care": """
The therapist is asking about psychiatric care.

The authored case does not establish a definite answer.

Do not invent psychiatric treatment and do not convert missing
information into a definite negative answer.

Respond naturally and personally rather than referring to records,
cases, specifications or missing data.
""",

    "healthcare_professionals": """
The therapist is asking whether healthcare professionals are involved.

The authored case does not establish a definite answer.

Do not invent a GP, doctor, psychiatrist, psychologist or other
professional.

Do not state definitely that nobody is involved.

Use concise first-person uncertainty and leave room for appropriate
clarification.
""",

    "previous_hypnosis": """
The therapist is asking about previous hypnosis or hypnotherapy.

The authored case does not establish whether the client has previous
experience.

Do not invent an experience and do not state definitely that the
client has never had hypnosis.

Respond as a real person who cannot confidently confirm the history.
""",

    "referral_permission": """
The therapist is asking about referral, professional permission
or medical clearance.

The authored case does not establish a definite answer.

Do not invent a referral or clearance requirement and do not claim
definitely that none is required.

Respond naturally and allow the issue to remain open for appropriate
professional clarification.
""",

    "risk": """
The therapist is asking a sensitive question about self-harm,
suicidal thoughts, harm to others or related risk.

The authored case does not establish a positive OR negative answer.

This is safety-critical.

Do NOT invent suicidal thoughts, self-harm or violent thoughts.
Do NOT turn missing information into "No", "Never" or
"I haven't had those thoughts."

Respond briefly, naturally and cautiously while preserving genuine
uncertainty.

Do not mention simulator data, the case, records, specifications,
or what has or has not been established.
""",

    "contraindications": """
The therapist is asking about suitability, contraindications or
clinical factors that could require additional professional advice.

The authored case does not establish a definite positive or negative
answer.

Do not declare hypnotherapy safe or unsafe.
Do not invent a contraindication.
Do not claim that there are no contraindications.

Respond naturally and indicate uncertainty in a way that allows
appropriate assessment or professional clarification to continue.
""",

    "safeguarding": """
The therapist is asking about safeguarding or personal safety.

The authored case does not establish a definite positive or negative
answer.

Do not invent abuse, danger or safeguarding concerns.
Do not automatically state that there are none.

Respond carefully in first-person language while preserving
uncertainty and allowing further appropriate assessment.
"""
}


# ============================================================
# BUILD UNKNOWN RESPONSE INSTRUCTION
# ============================================================

def build_unknown_response_guidance(
    student_text: str,
    persona: Dict[str, Any],
    recent_client_messages: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Return additional generation guidance only when:

    1. The therapist asks about a protected clinical domain.
    2. The authoritative case does not establish the answer.

    The function does NOT generate the final client response.
    """

    domain = detect_unknown_domain(student_text)

    if not domain:
        return None

    value = get_domain_value(
        persona=persona,
        domain=domain
    )

    if not is_unestablished(value):
        return None

    recent_client_messages = recent_client_messages or []

    recent_text = "\n".join(
        f"- {message}"
        for message in recent_client_messages[-4:]
        if message
    )

    guidance = DOMAIN_GUIDANCE.get(
        domain,
        """
The requested clinical information is not established by the
authoritative case.

Preserve uncertainty without inventing a positive or negative fact.
Respond naturally as the client.
"""
    )

    instruction = f"""
============================
UNESTABLISHED CLINICAL FIELD
============================

Protected domain:
{domain}

Student's current question:
{student_text}

{guidance}

VARIATION REQUIREMENT

Avoid reusing the same uncertainty sentence from earlier responses.

Recent client responses:
{recent_text if recent_text else "No recent client responses supplied."}

The response must sound like something the client would actually say
during a consultation.

Do NOT use system-like phrases such as:
- "it hasn't been established"
- "it hasn't been specified"
- "there is no information"
- "in my case"
- "in my situation"
- "in my background"
- "according to the case"

Do not merely replace those phrases with another repetitive template.

Keep the answer concise and relevant to the therapist's exact question.
"""

    return {
        "domain": domain,
        "value": value,
        "instruction": instruction.strip(),
    }