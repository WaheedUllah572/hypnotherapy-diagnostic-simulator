from typing import Any, Dict, List, Optional

from services.protected_domain_engine import (
    detect_risk_question_type,
)


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
        "self-harm thoughts",
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
The therapist is asking a sensitive question about RISK.

The authored case may contain some risk information, but that does
NOT mean every type of risk question has been answered.

You MUST distinguish the exact risk question being asked.

A statement such as:

"No self-harm history"

ONLY establishes information about a HISTORY OF SELF-HARM.

It does NOT establish:

- absence of suicidal thoughts
- absence of self-harm thoughts
- absence of suicide attempts
- absence of thoughts of harming others

Therefore, never infer a complete negative risk assessment from one
risk factor.

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
- "I don't have those thoughts"
- "I've never thought about that"
- "I have no risk"
- any other definite negative answer

The response MUST clearly relate to the exact safety topic being asked
about while preserving uncertainty when that specific information is
not established.

Keep the response brief, natural and cautious.
""",

    "contraindications": """
The therapist is asking specifically about CONTRAINDICATIONS,
SUITABILITY, or factors that could make hypnosis/hypnotherapy unsafe.

The authored case does not establish a definite positive or negative
answer.

The response MUST clearly relate to suitability, contraindications,
or relevant clinical factors.

Do NOT simply say:

"I'm not sure."

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
# RISK-SPECIFIC GUIDANCE
# ============================================================

RISK_QUESTION_GUIDANCE = {

    "self_harm_history": """
The therapist is asking specifically about a HISTORY OF SELF-HARM.

The authored case may explicitly establish "No self-harm history".

If that exact fact is present in the authoritative case, the client
may answer that they do not have a history of self-harm.

Do not expand that fact into claims about:

- suicidal thoughts
- self-harm thoughts
- suicide attempts
- thoughts of harming others

Only answer the history question that was actually asked.
""",

    "suicidal_or_self_harm_ideation": """
The therapist is asking specifically about SUICIDAL THOUGHTS or
SELF-HARM IDEATION.

IMPORTANT:

A statement such as "No self-harm history" does NOT answer this
question.

The case has NOT established whether the client has suicidal thoughts
or thoughts of self-harm.

Therefore the client MUST preserve uncertainty.

Do NOT answer:

- "No."
- "Never."
- "I don't have those thoughts."
- "I have no history of self-harm."

Those answers would incorrectly convert an unestablished ideation
field into a definite negative.

The response should naturally identify that the uncertainty concerns
thoughts of self-harm or suicide.

Do not invent suicidal thoughts, self-harm thoughts, intent, plans,
or previous attempts.
""",

    "suicide_attempt": """
The therapist is asking specifically about SUICIDE ATTEMPTS.

The authored case does not establish whether a suicide attempt has
ever occurred.

A statement about self-harm history does NOT establish the answer.

The client must preserve uncertainty.

Do not invent an attempt.
Do not say definitely that there has never been an attempt.
""",

    "harm_to_others": """
The therapist is asking specifically about THOUGHTS OF HARMING
OTHER PEOPLE.

The authored case does not establish whether such thoughts exist.

Information about self-harm history does NOT answer this question.

The client must preserve uncertainty.

Do not invent violent thoughts, intent, plans, or behaviour.
Do not give a definite negative answer.
""",

    "general_risk": """
The therapist is asking a GENERAL RISK question.

Do not infer that all risk domains are negative merely because one
risk factor is known.

The case does not establish a complete risk assessment.

Preserve uncertainty and answer only what the therapist actually asks.

Do not invent risk, self-harm, suicidal thoughts, violence, intent,
plans or previous attempts.
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

    # --------------------------------------------------------
    # Import here as well so this engine remains easy to load
    # and the risk-specific classifier is used only when needed.
    # --------------------------------------------------------

    from services.protected_domain_engine import (
        detect_domain,
        get_domain_value,
        is_defined,
    )

    domain = detect_domain(student_text)

    if not domain:
        return None

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Use the protected engine's authoritative definition logic.
    #
    # This is especially important for risk because:
    #
    # "No self-harm history"
    #
    # does NOT mean:
    #
    # "No suicidal/self-harm thoughts".
    # --------------------------------------------------------

    defined = is_defined(
        persona,
        domain,
        student_text,
    )

    if defined:
        return None

    value = get_domain_value(
        persona=persona,
        domain=domain,
    )

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

    # ========================================================
    # RISK QUESTION SUBTYPE
    # ========================================================

    risk_question_type = None
    risk_guidance = ""

    if domain == "risk":

        risk_question_type = detect_risk_question_type(
            student_text
        )

        risk_guidance = RISK_QUESTION_GUIDANCE.get(
            risk_question_type,
            RISK_QUESTION_GUIDANCE["general_risk"],
        )

    # ========================================================
    # TOPIC ANCHORS
    # ========================================================

    topic_anchors = DOMAIN_TOPIC_ANCHORS.get(
        domain,
        [domain],
    )

    topic_anchor_text = ", ".join(topic_anchors)

    # ========================================================
    # FULL GENERATION INSTRUCTION
    # ========================================================

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
RISK QUESTION TYPE
============================

{f"Detected risk question type: {risk_question_type}" if domain == "risk" else "Not applicable."}

{risk_guidance if domain == "risk" else ""}

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

If the therapist asks about self-harm thoughts, the response should
naturally refer to thoughts of self-harm or the specific safety topic.

Do not mechanically copy these examples.

Use natural client language appropriate to the client.

============================
TOPIC-SPECIFIC UNCERTAINTY
============================

This is a critical requirement.

The client MUST respond to the actual topic of the therapist's
question.

The response should make it clear WHAT the client is uncertain about.

GOOD STRUCTURE:

Specific topic + natural uncertainty.

Examples:

Medication:
"I'm not certain what medication I'm currently taking, if any.
I'd need to check that."

Psychiatric care:
"I'm not sure whether I've ever seen a psychiatrist. I'd need to
think back before I could answer properly."

Previous hypnosis:
"I can't remember whether I've actually had hypnotherapy before."

Medical history:
"I'm not entirely sure about my medical history. I'd need to think
about it more before I could answer accurately."

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
RISK SAFETY OVERRIDE
============================

If the current domain is "risk", NEVER use another risk subtype
as an answer to the current question.

For example:

Question:
"Have you ever had thoughts of harming yourself?"

INVALID:
"No, I don't have a history of self-harm."

Why invalid:
That answers self-harm HISTORY, not self-harm IDEATION.

Question:
"Have you ever harmed yourself?"

If the authoritative case says:
"No self-harm history"

then that specific fact may be used.

Question:
"Have you ever attempted suicide?"

INVALID:
"No, I don't have a history of self-harm."

Why invalid:
Self-harm history does not establish suicide-attempt history.

Question:
"Have you had thoughts of harming someone else?"

INVALID:
"No, I don't have a history of self-harm."

Why invalid:
Self-harm concerns are not the same as harm-to-others ideation.

Always answer the exact risk subtype being asked.

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

If suicidal/self-harm ideation is undefined:
do not invent suicidal or self-harm thoughts.

If suicide attempts are undefined:
do not invent an attempt.

If harm-to-others ideation is undefined:
do not invent violent thoughts.

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
9. If this is a risk question, answer the EXACT risk subtype rather
   than substituting another risk fact.
"""

    return {
        "domain": domain,
        "value": value,
        "instruction": instruction.strip(),
    }