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
        "taking tablets",
        "taking any medication",
        "currently taking",
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
        "tried hypnotherapy",
        "tried hypnosis",
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
        "seen a psychiatrist",
        "see a psychiatrist",
    ]):
        return "psychiatric_care"

    # --------------------------------------------------------
    # PSYCHOLOGICAL CARE
    # --------------------------------------------------------

    if any(x in text for x in [
        "psychological care",
        "psychological treatment",
        "psychologist",
        "psychological support",
        "psychological therapy",
        "seeing a therapist",
        "seen a therapist",
        "seeing a counsellor",
        "seen a counsellor",
        "seeing a counselor",
        "seen a counselor",
        "currently in therapy",
        "receiving therapy",
        "had therapy",
        "had counselling",
        "had counseling",
        "previous therapy",
        "previous counselling",
        "previous counseling",
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
        "any doctors",
        "any doctor",
        "any healthcare professional",
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
        "doctor permission",
        "gp permission",
        "gp referral",
        "doctor approval",
        "medical approval",
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
        "health history",
        "physical health",
        "medical problems",
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
# DOMAIN-SPECIFIC TOPIC ANCHORS
# ============================================================

DOMAIN_TOPIC_ANCHORS = {

    "medication": [
        "medication",
        "medicine",
        "prescription",
        "what I'm currently taking",
    ],

    "medical_history": [
        "medical history",
        "health history",
        "health conditions",
        "physical health",
    ],

    "psychological_care": [
        "therapy",
        "counselling",
        "counseling",
        "psychological support",
        "psychological treatment",
    ],

    "psychiatric_care": [
        "psychiatrist",
        "psychiatric care",
        "psychiatric treatment",
    ],

    "healthcare_professionals": [
        "doctor",
        "GP",
        "healthcare professional",
        "medical professional",
    ],

    "previous_hypnosis": [
        "hypnosis",
        "hypnotherapy",
        "hypnotherapist",
    ],

    "referral_permission": [
        "referral",
        "permission",
        "medical clearance",
        "doctor's approval",
    ],

    "risk": [
        "self-harm",
        "suicidal thoughts",
        "thoughts of harming myself",
        "thoughts of harming someone else",
    ],

    "contraindications": [
        "contraindication",
        "suitability",
        "medical or psychological factors",
        "factors that could make hypnosis unsafe",
    ],

    "safeguarding": [
        "safeguarding",
        "personal safety",
        "feeling safe",
        "being harmed",
    ],
}


# ============================================================
# DOMAIN-SPECIFIC CONVERSATIONAL GUIDANCE
# ============================================================

DOMAIN_GUIDANCE = {

    "medication": """
The therapist is asking specifically about CURRENT MEDICATION.

The authored case does not establish a definite medication status.

The response MUST clearly relate to medication, medicines,
prescriptions, or what the client is currently taking.

Do NOT give a generic uncertainty response that could apply to
any unrelated question.

For example, avoid responses consisting only of:
- "I'm not sure."
- "I can't say."
- "I'd need to check."
- "I don't know."

Instead, naturally make the uncertainty specific to medication.

The client may indicate that they are unsure what medication they
currently take, cannot confidently recall the details, or would need
to check.

Do not invent:
- a medication
- a prescription
- a reason for taking medication
- medication adherence
- medication side effects

Do not claim definitely that the client takes no medication.
""",

    "medical_history": """
The therapist is asking specifically about MEDICAL HISTORY.

The authored case does not establish a definite medical history.

The response MUST clearly relate to medical history, health conditions,
or previous/current physical health.

Do NOT respond with a generic uncertainty sentence alone.

The client may naturally say that they are unsure about their medical
history, cannot confidently recall the relevant details, or would need
to think/check before answering accurately.

Do not invent a diagnosis, medical condition, illness, procedure,
or clean bill of health.

Do not claim that there is no medical history.
""",

    "psychological_care": """
The therapist is asking specifically about PSYCHOLOGICAL CARE,
such as previous or current therapy, counselling, or psychological
support.

The authored case does not establish a definite answer.

The response MUST clearly relate to psychological treatment,
therapy, counselling, or psychological support.

Do NOT respond with a generic uncertainty sentence alone.

The client may naturally indicate uncertainty about whether they have
previously received psychological support or whether a particular
experience counts as psychological treatment.

Do not invent:
- therapy
- counselling
- psychological treatment
- a therapist
- a psychologist
- dates or treatment details

Do not claim definitely that no psychological care has occurred.
""",

    "psychiatric_care": """
The therapist is asking specifically about PSYCHIATRIC CARE.

The authored case does not establish a definite answer.

The response MUST clearly relate to psychiatric care, seeing a
psychiatrist, psychiatric treatment, or psychiatric support.

Do NOT respond with a generic uncertainty sentence alone.

The client may naturally say that they are unsure whether they have
ever seen a psychiatrist, cannot confidently recall any psychiatric
care, or would need to check before answering accurately.

Do not invent:
- a psychiatrist
- psychiatric treatment
- psychiatric diagnosis
- psychiatric medication
- appointments
- dates
- treatment outcomes

Do not claim definitely that the client has never received psychiatric
care.
""",

    "healthcare_professionals": """
The therapist is asking specifically about HEALTHCARE PROFESSIONALS.

The authored case does not establish a definite answer.

The response MUST clearly relate to doctors, healthcare professionals,
or other professionals involved in the client's care.

Do NOT respond with a generic uncertainty sentence alone.

The client may naturally indicate uncertainty about who, if anyone,
has been involved in their healthcare or may need to check before
answering accurately.

Do not invent:
- a GP
- doctor
- psychiatrist
- psychologist
- specialist
- other healthcare professional

Do not state definitely that nobody is involved.
""",

    "previous_hypnosis": """
The therapist is asking specifically about PREVIOUS HYPNOSIS OR
HYPNOTHERAPY.

The authored case does not establish whether the client has previous
experience.

The response MUST clearly relate to hypnosis or hypnotherapy.

Do NOT respond with a generic uncertainty sentence alone.

The client may naturally indicate uncertainty about whether they have
experienced hypnosis or hypnotherapy before and may need to think
before answering.

Do not invent:
- a previous hypnosis session
- a hypnotherapist
- an experience
- beliefs about hypnosis
- outcomes
- dates

Do not claim definitely that the client has never experienced hypnosis.
""",

    "referral_permission": """
The therapist is asking specifically about REFERRAL, PERMISSION,
MEDICAL CLEARANCE, or whether another professional needs to be involved.

The authored case does not establish a definite answer.

The response MUST clearly relate to the referral or permission question.

Do NOT respond with a generic uncertainty sentence alone.

The client may naturally indicate that they are unsure whether a
referral, permission, or medical clearance is required and would need
to clarify it.

Do not invent a referral.
Do not invent medical clearance.
Do not claim definitely that no permission is required.
""",

    "risk": """
The therapist is asking a sensitive question about RISK, including
self-harm, suicidal thoughts, or harm to others.

The authored case does not establish a definite positive OR negative
answer.

This is safety-critical.

The response MUST clearly acknowledge the specific safety topic being
asked about while preserving genuine uncertainty.

Do NOT invent:
- suicidal thoughts
- self-harm
- violent thoughts
- intent
- plans
- previous attempts

Do NOT convert missing information into:
- "No"
- "Never"
- "I've never had those thoughts"
- any other definite negative answer

Do not use a generic uncertainty sentence with no indication of what
the client is uncertain about.

Keep the response brief and cautious.
""",

    "contraindications": """
The therapist is asking specifically about CONTRAINDICATIONS,
SUITABILITY, or factors that could make hypnosis/hypnotherapy unsafe.

The authored case does not establish a definite positive or negative
answer.

The response MUST clearly relate to suitability, contraindications,
or relevant clinical factors.

Do NOT simply say "I'm not sure."

Do not declare hypnotherapy safe.
Do not declare hypnotherapy unsafe.
Do not invent a contraindication.
Do not claim there are no contraindications.

The client may indicate that they do not know whether there are any
relevant medical or psychological factors and that this would need
appropriate clarification.
""",

    "safeguarding": """
The therapist is asking specifically about SAFEGUARDING or PERSONAL
SAFETY.

The authored case does not establish a definite positive OR negative
answer.

The response MUST clearly relate to the safeguarding or personal
safety question.

Do NOT respond with a generic uncertainty sentence alone.

Do not invent:
- abuse
- neglect
- danger
- threats
- safeguarding concerns

Do not claim definitely that there are no safeguarding concerns.

Respond carefully and briefly while preserving uncertainty.
""",
}


# ============================================================
# BUILD UNKNOWN RESPONSE INSTRUCTION
# ============================================================

def build_unknown_response_guidance(
    student_text: str,
    persona: Dict[str, Any],
    behaviour: Dict[str, Any],
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
        domain=domain,
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

The response must clearly relate to the exact clinical topic the
therapist asked about.

Do not use a generic uncertainty statement by itself.
""",
    )

    topic_anchors = DOMAIN_TOPIC_ANCHORS.get(
        domain,
        [domain],
    )

    topic_anchor_text = ", ".join(topic_anchors)

    instruction = f"""
============================
UNESTABLISHED CLINICAL FIELD
============================

Protected domain:
{domain}

Student's current question:
{student_text}

{guidance}

============================
MANDATORY TOPIC ANCHOR
============================

The response MUST naturally refer to the specific topic being asked
about.

Relevant topic words/concepts for this question are:

{topic_anchor_text}

At least ONE natural reference to the relevant topic MUST appear
in the response.

Do not merely express uncertainty.

For example:

If the therapist asks about medication, the response should naturally
mention medication, medicine, prescription, or what the client is
currently taking.

If the therapist asks about psychiatric care, the response should
naturally mention a psychiatrist or psychiatric care.

If the therapist asks about previous hypnosis, the response should
naturally mention hypnosis or hypnotherapy.

Do not mechanically copy these examples.

Use natural client language appropriate to the client personality.

============================
TOPIC-SPECIFIC UNCERTAINTY
============================

This is a critical requirement.

The client MUST respond to the actual topic of the therapist's
question.

The response should make it clear WHAT the client is uncertain about.

GOOD STRUCTURE:

Specific topic + natural uncertainty.

For example:

Medication:
"I'm not certain what medication I'm currently taking, if any.
I'd need to check that."

Psychiatric care:
"I'm not sure whether I've ever seen a psychiatrist. I'd need to
think back before I could answer properly."

Previous hypnosis:
"I can't remember whether I've actually had hypnotherapy before."

These examples demonstrate the required structure only.

Do NOT copy them mechanically.

Generate natural wording appropriate to this client.

============================
NO GENERIC UNCERTAINTY
============================

Never answer an undefined protected question using ONLY:

- "I'm not sure."
- "I don't know."
- "I can't say."
- "I can't say for certain."
- "I'd need to check."
- "I can't remember."
- "I'm not certain."
- "I'd have to think about that."

These phrases may appear as part of a longer,
topic-specific response, but they MUST NOT constitute the entire
answer.

The response must contain a natural reference to the actual domain.

============================
DO NOT OVERDISCLOSE
============================

Topic-specific does NOT mean inventing details.

If medication is undefined:
do not invent a medication.

If psychiatric care is undefined:
do not invent a psychiatrist.

If psychological care is undefined:
do not invent therapy.

If previous hypnosis is undefined:
do not invent hypnosis experience.

If risk is undefined:
do not invent risk.

The response should identify the uncertainty without filling the
missing fact.

============================
CONVERSATIONAL VARIATION
============================

Avoid repeating the same uncertainty wording from recent responses.

Do not mechanically rotate through a fixed list.

Vary:

- sentence openings
- sentence structure
- length
- vocabulary
- rhythm
- degree of hesitation

Never begin two consecutive responses with the same wording when
natural variation is possible.

Recent client responses:

{recent_text if recent_text else "No recent client responses supplied."}

The recent responses are provided to help avoid repetition.

Do not copy their wording.

============================
CLIENT NATURALNESS
============================

The response must sound like the client speaking during an actual
consultation.

Do not sound like:
- a database
- a medical form
- a system
- a tutor
- an AI assistant

Do not say:
- "the case"
- "the information provided"
- "not established"
- "not specified"
- "according to my records"
- "there is no information"
- "my case"
- "my clinical history"

The client should simply respond naturally to the therapist.

============================
CURRENT BEHAVIOUR
============================

Trust:
{behaviour["trust_level"]}

Resistance:
{behaviour["resistance_level"]}

Distress:
{behaviour["distress_level"]}

Match the client's current behaviour.

If trust is low:
- keep the response brief
- remain cautious

If trust is high:
- allow slightly more natural explanation

If resistance is high:
- hesitation may increase

If distress is high:
- the uncertainty may sound slightly more emotionally difficult

However, behaviour MUST NOT change the underlying uncertainty.

============================
FINAL REQUIREMENT
============================

Produce ONE concise client response.

It must:

1. Answer the therapist's exact question.
2. Identify the specific topic being discussed.
3. Preserve uncertainty because the case does not establish the fact.
4. Avoid inventing clinical information.
5. Sound natural for the client.
6. Avoid generic uncertainty-only responses.
7. Avoid repeating the previous uncertainty wording.
8. Include at least one natural topic reference.
"""

    return {
        "domain": domain,
        "value": value,
        "instruction": instruction.strip(),
    }