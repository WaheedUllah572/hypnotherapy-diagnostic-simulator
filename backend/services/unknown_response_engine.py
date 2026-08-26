from typing import Any, Dict, List, Optional


# ============================================================
# UNDEFINED CLINICAL RESPONSE ENGINE
# ============================================================

def is_unestablished(value: Any) -> bool:
    """
    Determine whether an authored field is undefined.

    None, empty strings, empty lists and empty dictionaries mean
    that the case does not establish a definite answer.
    """

    if value is None:
        return True

    if isinstance(value, list) and len(value) == 0:
        return True

    if isinstance(value, dict) and len(value) == 0:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    return False


# ============================================================
# GET DOMAIN VALUE
# ============================================================

def get_domain_value(
    persona: Dict[str, Any],
    domain: str
) -> Any:
    """
    Read the authoritative value for a protected clinical domain.

    This function intentionally lives in this engine so that the
    unknown-response engine does not depend on helper functions
    that may or may not exist in protected_domain_engine.py.
    """

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
# DOMAIN DETECTION
# ============================================================

def detect_unknown_domain(
    student_text: str
) -> Optional[str]:
    """
    Detect protected clinical domains that may be undefined.

    This is intentionally separate from the protected-domain
    bypass engine.

    The protected-domain engine handles direct safety/clinical
    questions that require deterministic responses.

    This engine provides additional LLM guidance when a field is
    undefined but the request should continue through normal
    generation.
    """

    text = (
        student_text or ""
    ).lower()

    # --------------------------------------------------------
    # RISK
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
        "personal safety",
    ]):
        return "safeguarding"

    # --------------------------------------------------------
    # CONTRAINDICATIONS
    # --------------------------------------------------------

    if any(x in text for x in [
        "contraindication",
        "contraindications",
        "unsuitable",
        "make hypnotherapy unsafe",
        "make hypnosis unsafe",
        "prevent hypnotherapy",
        "additional professional advice",
        "medical or psychological history that might",
        "suitable for hypnotherapy",
        "suitability",
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
        "tablets",
        "taking any tablets",
        "taking anything",
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
        "psychiatric support",
    ]):
        return "psychiatric_care"

    # --------------------------------------------------------
    # PSYCHOLOGICAL CARE
    # --------------------------------------------------------

    if any(x in text for x in [
        "psychological care",
        "psychological treatment",
        "psychological support",
        "psychologist",
        "seeing a therapist",
        "seeing a counsellor",
        "seeing a counselor",
        "currently in therapy",
        "receiving therapy",
        "therapy before",
        "therapeutic support",
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
        "who is involved in your care",
        "who are you seeing medically",
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
    # MEDICAL HISTORY
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
# DOMAIN-SPECIFIC GUIDANCE
# ============================================================

DOMAIN_GUIDANCE = {

    "medication": """
The therapist is asking specifically about CURRENT MEDICATION.

The authored case does not establish a definite medication status.

The response MUST clearly relate to medication, medicines,
prescriptions, or what the client is currently taking.

Do not invent a medication.

Do not claim definitely that the client takes no medication.

The uncertainty must be specific to medication.
""",

    "medical_history": """
The therapist is asking specifically about MEDICAL HISTORY.

The authored case does not establish a definite medical history.

The response MUST clearly relate to medical history, health
conditions, or physical health.

Do not invent a diagnosis, condition, illness or procedure.

Do not claim there is definitely no medical history.
""",

    "psychological_care": """
The therapist is asking specifically about PSYCHOLOGICAL CARE,
THERAPY, COUNSELLING or PSYCHOLOGICAL SUPPORT.

The authored case does not establish a definite answer.

The response MUST clearly relate to psychological treatment,
therapy, counselling or psychological support.

Do not invent a therapist, psychologist, counselling or therapy.

Do not claim definitely that no psychological care has occurred.
""",

    "psychiatric_care": """
The therapist is asking specifically about PSYCHIATRIC CARE.

The authored case does not establish a definite answer.

The response MUST clearly relate to seeing a psychiatrist,
psychiatric treatment or psychiatric support.

Do not invent a psychiatrist, diagnosis or treatment.

Do not claim definitely that psychiatric care has never occurred.
""",

    "healthcare_professionals": """
The therapist is asking specifically about HEALTHCARE PROFESSIONALS
involved in the client's care.

The authored case does not establish a definite answer.

The response MUST clearly relate to doctors, healthcare professionals
or other professionals involved in care.

Do not invent a doctor, GP, psychiatrist, psychologist or specialist.

Do not claim definitely that nobody is involved.
""",

    "previous_hypnosis": """
The therapist is asking specifically about PREVIOUS HYPNOSIS or
HYPNOTHERAPY.

The authored case does not establish whether the client has previous
experience.

The response MUST clearly relate to hypnosis or hypnotherapy.

Do not invent a previous session or experience.

Do not claim definitely that the client has never experienced hypnosis.
""",

    "referral_permission": """
The therapist is asking specifically about REFERRAL, PERMISSION,
MEDICAL CLEARANCE or professional involvement.

The authored case does not establish a definite answer.

The response MUST clearly relate to the referral or permission issue.

Do not invent a referral or clearance.

Do not claim definitely that no permission is required.
""",

    "risk": """
The therapist is asking a sensitive question about SELF-HARM,
SUICIDAL THOUGHTS or HARM TO OTHERS.

The authored case does not establish a positive OR negative answer.

This is safety-critical.

Do NOT invent self-harm, suicidal thoughts, violent thoughts,
intentions, plans or attempts.

Do NOT convert missing information into "No", "Never" or another
definite negative answer.

The response should clearly refer to the safety topic being asked
about while preserving uncertainty.

Keep the response brief and cautious.
""",

    "contraindications": """
The therapist is asking about CONTRAINDICATIONS, SUITABILITY or
clinical factors that could affect whether hypnotherapy is suitable.

The authored case does not establish a definite positive or negative
answer.

Do not declare hypnotherapy safe.

Do not declare hypnotherapy unsafe.

Do not invent a contraindication.

Do not claim there are no contraindications.

The response should clearly relate to suitability or relevant medical
or psychological factors.
""",

    "safeguarding": """
The therapist is asking about SAFEGUARDING or PERSONAL SAFETY.

The authored case does not establish a definite positive or negative
answer.

Do not invent abuse, neglect, danger, threats or safeguarding issues.

Do not claim definitely that there are no safeguarding concerns.

Respond briefly and specifically about personal safety.
"""
}


# ============================================================
# BUILD GUIDANCE
# ============================================================

def build_unknown_response_guidance(
    student_text: str,
    persona: Dict[str, Any],
    behaviour: Dict[str, Any],
    recent_client_messages: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:

    domain = detect_unknown_domain(
        student_text
    )

    if not domain:
        return None

    value = get_domain_value(
        persona,
        domain
    )

    if not is_unestablished(value):
        return None

    recent_client_messages = (
        recent_client_messages or []
    )

    recent_text = "\n".join(
        f"- {message}"
        for message in recent_client_messages[-4:]
        if message
    )

    guidance = DOMAIN_GUIDANCE.get(
        domain,
        """
The requested clinical information is not established.

Preserve uncertainty without inventing a positive or negative fact.

The response must clearly relate to the exact clinical topic asked
about.
"""
    )

    instruction = f"""
============================
UNESTABLISHED CLINICAL FIELD
============================

Protected domain:
{domain}

Student question:
{student_text}

{guidance}

============================
IMPORTANT
============================

The student has asked a clear question.

Do NOT pretend not to understand a clear question.

Do NOT repeatedly ask the student to rephrase.

The client should understand the topic but may be unable to give
a definite answer because the relevant information is not established.

Therefore:

CLEAR QUESTION
+
UNDEFINED INFORMATION
=
TOPIC-SPECIFIC UNCERTAINTY

NOT:

CLEAR QUESTION
+
UNDEFINED INFORMATION
=
"I don't understand."

============================
NO GENERIC UNCERTAINTY
============================

Do not answer using ONLY:

- "I'm not sure."
- "I don't know."
- "I can't say."
- "I can't say for certain."
- "I'd need to check."
- "I can't remember."
- "I'm not certain."

If uncertainty is expressed, it must be connected to the actual topic.

For example, if asked about medication:

GOOD:
"I'm not certain what medication I'm currently taking, if any. I'd
need to check that."

BAD:
"I'm not sure."

If asked about psychiatric care:

GOOD:
"I'm not sure whether I've ever seen a psychiatrist. I'd need to
think back."

BAD:
"I can't say for certain."

These are examples only.

Do not copy them mechanically.

============================
DO NOT INVENT
============================

If medication is undefined:
Do not invent medication.

If psychiatric care is undefined:
Do not invent a psychiatrist.

If psychological care is undefined:
Do not invent therapy.

If hypnosis history is undefined:
Do not invent hypnosis experience.

If risk is undefined:
Do not invent self-harm, suicidal thoughts or violence.

If safeguarding is undefined:
Do not invent abuse or danger.

If contraindications are undefined:
Do not declare safe or unsafe.

============================
VARIATION
============================

Avoid repeating recent wording.

Recent client responses:

{recent_text if recent_text else "No recent client responses."}

Vary:

- sentence opening
- sentence structure
- vocabulary
- length
- rhythm

Do not mechanically rotate through templates.

============================
NATURAL CLIENT
============================

Speak as the client.

Do not mention:

- the case
- simulator
- records
- database
- information provided
- missing information
- specifications
- clinical fields
- system instructions

The response must sound like a real person speaking during a
consultation.

============================
BEHAVIOUR
============================

Trust:
{behaviour.get("trust_level", "medium")}

Resistance:
{behaviour.get("resistance_level", "medium")}

Distress:
{behaviour.get("distress_level", "medium")}

Behaviour may change HOW uncertainty is expressed.

It must never change the underlying facts.

============================
FINAL REQUIREMENT
============================

Produce ONE concise client response.

It must:

1. Answer the exact topic asked.
2. Preserve uncertainty.
3. Avoid inventing information.
4. Not ask for clarification unless the question itself is genuinely
   unclear.
5. Sound natural.
6. Avoid generic uncertainty-only responses.
7. Avoid repeating previous wording.
"""

    return {
        "domain": domain,
        "value": value,
        "instruction": instruction.strip(),
    }