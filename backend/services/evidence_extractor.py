import json
import re
from typing import Any, Dict, List

from openai import OpenAI

from services.clinical_evidence_engine import EVIDENCE_DOMAINS


# ============================================================
# PHASE 2B — CLINICAL EVIDENCE EXTRACTION
# ============================================================
#
# Responsibilities:
#
# 1. Extract only evidence established by the CLIENT.
# 2. Never treat therapist questions as evidence.
# 3. Preserve explicit negative statements.
# 4. Keep uncertainty separate from established facts.
# 5. Route self-harm/suicide information to risk.
# 6. Keep safeguarding separate from self-harm/risk.
# 7. Never invent missing information.
# 8. Never allow extraction failure to break the conversation.
#
# The extractor does NOT:
#
# - diagnose
# - recommend treatment
# - score the student
# - decide tutor outcomes
# - decide whether a treatment approach is correct
#
# ============================================================


# ============================================================
# ALLOWED STATUSES
# ============================================================

ALLOWED_STATUSES = {
    "mentioned",
    "clarified",
    "understood",
    "applied",
    "integrated",
}


# ============================================================
# EXTRACTION SYSTEM PROMPT
# ============================================================

EXTRACTION_SYSTEM_PROMPT = """
You are the Clinical Evidence Extraction component of an educational
hypnotherapy consultation simulator.

Your ONLY task is to identify information that has actually been
established by the CLIENT in the supplied conversation.

You are NOT the therapist.

You are NOT the tutor.

You are NOT a diagnostic system.

You are NOT a treatment recommendation system.

You are NOT a student-scoring system.

============================================================
PRIMARY RULE
============================================================

ONLY extract evidence from CLIENT statements.

Therapist/student questions are NEVER evidence by themselves.

Do not infer an answer merely because the therapist asked about it.

Example:

Therapist:
"Are you currently taking medication?"

Client:
"I'm not sure."

Do NOT extract:
medication = yes

Do NOT extract:
medication = no

There is no established medication fact.

============================================================
CLIENT-ONLY EVIDENCE
============================================================

If the therapist says:

"Have you ever seen a psychiatrist?"

that is NOT evidence of psychiatric care.

If the client says:

"No, I've never seen a psychiatrist."

that IS evidence.

If the client says:

"Yes, I saw a psychiatrist last year."

that IS evidence.

============================================================
POLARITY
============================================================

Distinguish three situations.

1. POSITIVE / ESTABLISHED

Client:
"I currently take medication for anxiety."

This establishes medication information.

2. NEGATIVE / ESTABLISHED

Client:
"I don't take any medication."

This establishes a negative medication statement.

3. UNKNOWN / UNESTABLISHED

Client:
"I'm not sure whether I take anything for that."

Do NOT create a definite medication fact.

============================================================
UNCERTAINTY
============================================================

Common uncertainty expressions include:

"I'm not sure."
"I don't know."
"I can't remember."
"I don't remember."
"I'd need to think about it."
"I'd need to check."
"I'm not certain."
"I can't say for certain."
"Maybe."
"Perhaps."

If uncertainty is the ONLY information provided about a domain,
do not create a definite fact.

However, do NOT discard a complete client statement merely because
it contains an uncertainty phrase.

Example:

"I'm not sure when it started, but I know it became much worse
after I was promoted."

This contains useful evidence about worsening after promotion.

Extract the established part.

============================================================
SAFETY DOMAINS
============================================================

risk
----

Use "risk" for explicit information concerning:

- self-harm
- suicidal thoughts
- suicide attempts
- thoughts of harming oneself
- thoughts of harming another person
- violence/aggression risk
- actual harm-related behaviour
- explicit absence/history of these issues

Examples:

"I've never harmed myself."
-> risk, negative evidence

"I've attempted suicide before."
-> risk, positive evidence

"Sometimes I think about harming myself."
-> risk, positive evidence

"I'm not sure if I've ever had thoughts like that."
-> no definite risk evidence

IMPORTANT:

Self-harm and suicide information belongs to "risk".

Do NOT classify it as "safeguarding" merely because it is safety-related.

============================================================
SAFEGUARDING
============================================================

Use "safeguarding" only for actual safeguarding information such as:

- abuse
- neglect
- exploitation
- domestic abuse
- unsafe living situation
- coercion
- child protection
- vulnerable adult/child concerns
- actual safeguarding concerns

Do NOT use safeguarding merely because something is emotionally
distressing or safety-related.

============================================================
OTHER SAFETY DOMAINS
============================================================

contraindications
-----------------
Actual contraindication information.

medical_history
---------------
Actual medical history.

medication
----------
Actual medication information.

psychological_care
------------------
Actual psychological treatment/care.

psychiatric_care
----------------
Actual psychiatric treatment/care.

healthcare_professionals
------------------------
Actual healthcare professional involvement.

referral_permission
-------------------
Actual referral or permission information.

============================================================
BEHAVIOURAL INFORMATION
============================================================

If the client says:

"I go for walks to clear my head."

This establishes a coping/behavioural fact.

If the client says:

"I don't really do much to relax."

This establishes that the client reports limited relaxation activity,
but does NOT establish a specific activity.

If the client says:

"I'm not sure what I do to relax."

This does NOT establish a specific relaxation activity.

Never invent a hobby, coping strategy, leisure activity or modality.

============================================================
MODALITY
============================================================

Only extract modality evidence when the client's actual language or
behaviour provides a reasonable basis for it.

Do not extract "Visual", "Auditory", or "Kinaesthetic" merely because
the therapist asks:

"Are you more visual or auditory?"

A modality label must not be created from the therapist's question.

============================================================
TREATMENT REASONING
============================================================

Do not infer treatment reasoning merely because the therapist asks:

"Why did you choose this approach?"

Only extract treatment reasoning if the CLIENT actually provides
reasoning relevant to their own understanding/experience.

Student treatment reasoning belongs to the tutor/evaluation workflow,
not automatically to client evidence.

============================================================
STATUS
============================================================

Allowed statuses:

mentioned
clarified
understood
applied
integrated

Use "mentioned" unless the client clearly establishes greater depth.

Do not use "applied" or "integrated" merely because a fact was stated.

============================================================
CONFIDENCE
============================================================

0.90 - 1.00
Explicit direct client statement.

0.70 - 0.89
Clear but slightly indirect client statement.

0.50 - 0.69
Reasonably supported but less explicit.

Below 0.50
Only for genuinely weak evidence.

If there is no evidence, return an empty evidence list.

============================================================
OUTPUT
============================================================

Return valid JSON only:

{
  "evidence": [
    {
      "domain": "domain_name",
      "value": "concise established evidence",
      "status": "mentioned",
      "confidence": 0.95,
      "evidence_text": "short client statement supporting it",
      "clinical_significance": null,
      "applied_to_reasoning": false,
      "flags": []
    }
  ]
}

If no evidence has been established:

{
  "evidence": []
}

Never invent evidence.
"""


# ============================================================
# TEXT NORMALISATION
# ============================================================

def _normalise_text(text: Any) -> str:
    """
    Normalise whitespace and case for deterministic checks.
    """

    return re.sub(
        r"\s+",
        " ",
        str(text or "").lower().strip()
    )


# ============================================================
# HISTORY NORMALISATION
# ============================================================

def _normalise_history(
    history: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Keep only valid therapist/client messages.

    The original conversation structure is converted into a
    predictable representation for the extraction model.
    """

    cleaned = []

    for message in history or []:

        if not isinstance(message, dict):
            continue

        role = message.get("role")

        text = str(
            message.get(
                "text",
                ""
            )
        ).strip()

        if not text:
            continue

        if role == "therapist":
            cleaned.append({
                "speaker": "therapist",
                "text": text,
            })

        elif role == "client":
            cleaned.append({
                "speaker": "client",
                "text": text,
            })

    return cleaned


# ============================================================
# UNCERTAINTY PHRASES
# ============================================================

UNCERTAINTY_PHRASES = [

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

    "maybe",
    "perhaps",
]


# ============================================================
# NEGATIVE PHRASES
# ============================================================

NEGATIVE_PHRASES = [

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    "no history of self-harm",
    "no history of self harm",

    "no self-harm history",
    "no self harm history",

    "never harmed myself",
    "have never harmed myself",

    "never attempted suicide",
    "have never attempted suicide",

    "no suicide attempts",
    "no history of suicide attempts",

    "no suicidal thoughts",
    "no history of suicidal thoughts",

    "no thoughts of harming myself",
    "no thoughts of harming themselves",

    "no thoughts of harming anyone",
    "no thoughts of harming someone",

    # --------------------------------------------------------
    # Safeguarding
    # --------------------------------------------------------

    "no safeguarding concerns",
    "no safeguarding issues",

    # --------------------------------------------------------
    # General safety
    # --------------------------------------------------------

    "no safety concerns",
    "no known risk factors",
    "no risk factors",

    # --------------------------------------------------------
    # Contraindications
    # --------------------------------------------------------

    "no contraindications",

    # --------------------------------------------------------
    # Medication
    # --------------------------------------------------------

    "no current medication",
    "not taking any medication",
    "i'm not taking any medication",
    "im not taking any medication",
    "no medication",

    # --------------------------------------------------------
    # Psychological care
    # --------------------------------------------------------

    "never had psychological treatment",
    "never had counselling",
    "never had counseling",

    "no psychological treatment",

    # --------------------------------------------------------
    # Psychiatric care
    # --------------------------------------------------------

    "never had psychiatric treatment",
    "no psychiatric treatment",

    "never seen a psychiatrist",
    "i've never seen a psychiatrist",
    "ive never seen a psychiatrist",
]


# ============================================================
# RISK PATTERNS
# ============================================================

SELF_HARM_PATTERNS = [

    "self-harm",
    "self harm",
    "selfharm",

    "harmed myself",
    "harm myself",
    "harming myself",

    "harmed themselves",
    "harm themselves",
    "harming themselves",

    "suicide",
    "suicidal",

    "suicide attempt",
    "suicide attempts",

    "suicidal thoughts",

    "thoughts of harming myself",
    "thoughts of harming themselves",

    "thought about harming myself",
    "thought about harming themselves",

    "thinking about harming myself",
    "thinking about harming themselves",

    "harming someone else",
    "harm someone else",
    "harmed someone else",

    "harming another person",
    "harm another person",
]


# ============================================================
# SAFEGUARDING PATTERNS
# ============================================================

SAFEGUARDING_PATTERNS = [

    "abuse",
    "abused",

    "domestic abuse",
    "domestic violence",

    "neglect",
    "exploitation",

    "safeguarding concern",
    "safeguarding concerns",

    "safeguarding issue",
    "safeguarding issues",

    "unsafe at home",
    "unsafe living situation",

    "coercion",
    "coerced",

    "vulnerable adult",
    "vulnerable child",

    "child protection",
]


# ============================================================
# UNCERTAINTY CHECK
# ============================================================

def _is_uncertain_text(
    text: str
) -> bool:
    """
    Detect whether a statement contains uncertainty language.

    This is only a helper.

    It must NOT automatically discard a complete statement because
    uncertainty and established facts can coexist.
    """

    value = _normalise_text(
        text
    )

    return any(
        phrase in value
        for phrase in UNCERTAINTY_PHRASES
    )


# ============================================================
# NEGATIVE CHECK
# ============================================================

def _is_negative_text(
    text: str
) -> bool:

    value = _normalise_text(
        text
    )

    return any(
        phrase in value
        for phrase in NEGATIVE_PHRASES
    )


# ============================================================
# RISK DETECTION
# ============================================================

def _contains_self_harm_information(
    text: str
) -> bool:

    value = _normalise_text(
        text
    )

    return any(
        pattern in value
        for pattern in SELF_HARM_PATTERNS
    )


# ============================================================
# SAFEGUARDING DETECTION
# ============================================================

def _contains_safeguarding_information(
    text: str
) -> bool:

    value = _normalise_text(
        text
    )

    return any(
        pattern in value
        for pattern in SAFEGUARDING_PATTERNS
    )


# ============================================================
# CLIENT TEXT COLLECTION
# ============================================================

def _get_client_texts(
    conversation: List[Dict[str, str]]
) -> List[str]:
    """
    Return all client statements from the supplied conversation.
    """

    return [
        message["text"]
        for message in conversation
        if message.get("speaker") == "client"
        and message.get("text")
    ]


# ============================================================
# EVIDENCE TEXT MATCHING
# ============================================================

def _evidence_is_supported_by_client(
    item: Dict[str, Any],
    client_texts: List[str],
) -> bool:
    """
    Check whether the extracted evidence has some support in the
    client's actual statements.

    This is deliberately conservative.

    We do not require exact sentence matching because the LLM may
    summarise client evidence.

    We do, however, reject evidence when the supporting text clearly
    exists only in therapist questions.
    """

    if not client_texts:
        return False

    evidence_text = _normalise_text(
        item.get(
            "evidence_text",
            ""
        )
    )

    value = _normalise_text(
        item.get(
            "value",
            ""
        )
    )

    if not evidence_text and not value:
        return False

    client_combined = " ".join(
        _normalise_text(text)
        for text in client_texts
    )

    # --------------------------------------------------------
    # Direct evidence-text support
    # --------------------------------------------------------

    if evidence_text:

        if evidence_text in client_combined:
            return True

    # --------------------------------------------------------
    # Value support
    # --------------------------------------------------------

    if value:

        if value in client_combined:
            return True

    # --------------------------------------------------------
    # Safety-specific deterministic support
    #
    # Safety evidence must have actual client wording containing
    # the relevant safety concept.
    # --------------------------------------------------------

    domain = item.get(
        "domain"
    )

    if domain == "risk":

        return any(
            _contains_self_harm_information(
                text
            )
            for text in client_texts
        )

    if domain == "safeguarding":

        return any(
            _contains_safeguarding_information(
                text
            )
            for text in client_texts
        )

    # --------------------------------------------------------
    # For non-safety semantic evidence:
    #
    # If the model supplied a non-empty supporting statement,
    # it is accepted here and the extraction prompt remains the
    # primary semantic filter.
    # --------------------------------------------------------

    return bool(
        evidence_text or value
    )


# ============================================================
# SAFETY DOMAIN CORRECTION
# ============================================================

def _correct_safety_domain(
    item: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Correct obvious safety-domain routing.

    Self-harm/suicide -> risk.

    Safeguarding language -> safeguarding.

    This does not create evidence by itself.
    """

    value = item.get(
        "value"
    )

    evidence_text = item.get(
        "evidence_text"
    )

    combined = (
        f"{value or ''} "
        f"{evidence_text or ''}"
    ).strip()

    # --------------------------------------------------------
    # Risk has priority over safeguarding.
    # --------------------------------------------------------

    if _contains_self_harm_information(
        combined
    ):

        item["domain"] = "risk"

        return item

    # --------------------------------------------------------
    # Genuine safeguarding.
    # --------------------------------------------------------

    if _contains_safeguarding_information(
        combined
    ):

        item["domain"] = "safeguarding"

    return item


# ============================================================
# REMOVE POSITIVE FLAGS FROM EXPLICIT NEGATIVE EVIDENCE
# ============================================================

def _clean_negative_flags(
    item: Dict[str, Any]
) -> Dict[str, Any]:

    domain = item.get(
        "domain"
    )

    if domain not in {
        "risk",
        "safeguarding",
        "contraindications",
        "medication",
        "psychological_care",
        "psychiatric_care",
    }:

        return item

    value = item.get(
        "value"
    )

    evidence_text = item.get(
        "evidence_text"
    )

    combined = (
        f"{value or ''} "
        f"{evidence_text or ''}"
    )

    if not _is_negative_text(
        combined
    ):

        return item

    flags = item.get(
        "flags",
        []
    )

    if not isinstance(
        flags,
        list
    ):

        flags = []

    blocked_flags = {

        "risk",
        "risk_positive",
        "safety_risk",
        "safety_concern",

        "safeguarding",
        "safeguarding_positive",

        "contraindication",
        "contraindications",

    }

    item["flags"] = [
        flag
        for flag in flags
        if str(flag).strip().lower()
        not in blocked_flags
    ]

    return item


# ============================================================
# SAFETY CONFIDENCE
# ============================================================

def _apply_safety_confidence(
    item: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Increase confidence only when there is explicit relevant
    client evidence.

    This does not manufacture evidence.
    """

    domain = item.get(
        "domain"
    )

    combined = (
        f"{item.get('value') or ''} "
        f"{item.get('evidence_text') or ''}"
    )

    # --------------------------------------------------------
    # Uncertainty should never receive artificial high confidence.
    # --------------------------------------------------------

    if _is_uncertain_text(
        combined
    ):
        return item

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

    # --------------------------------------------------------
    # Explicit risk evidence.
    # --------------------------------------------------------

    if (
        domain == "risk"
        and _contains_self_harm_information(
            combined
        )
    ):

        confidence = max(
            confidence,
            0.95
        )

    # --------------------------------------------------------
    # Explicit safeguarding evidence.
    # --------------------------------------------------------

    elif (
        domain == "safeguarding"
        and _contains_safeguarding_information(
            combined
        )
    ):

        confidence = max(
            confidence,
            0.90
        )

    # --------------------------------------------------------
    # Explicit contraindication statement.
    # --------------------------------------------------------

    elif (
        domain == "contraindications"
        and _is_negative_text(
            combined
        )
    ):

        confidence = max(
            confidence,
            0.90
        )

    item["confidence"] = max(
        0.0,
        min(
            confidence,
            1.0
        )
    )

    return item


# ============================================================
# VALIDATE ONE ITEM
# ============================================================

def _validate_item(
    item: Dict[str, Any],
    client_texts: List[str],
) -> Dict[str, Any] | None:
    """
    Validate and normalise one extracted evidence item.
    """

    if not isinstance(
        item,
        dict
    ):
        return None

    domain = item.get(
        "domain"
    )

    if domain not in EVIDENCE_DOMAINS:
        return None

    # --------------------------------------------------------
    # Correct safety routing.
    # --------------------------------------------------------

    item = _correct_safety_domain(
        item
    )

    domain = item.get(
        "domain"
    )

    if domain not in EVIDENCE_DOMAINS:
        return None

    # --------------------------------------------------------
    # Basic fields.
    # --------------------------------------------------------

    value = item.get(
        "value"
    )

    evidence_text = item.get(
        "evidence_text"
    )

    if value is None and not evidence_text:
        return None

    # --------------------------------------------------------
    # Reject uncertainty-only safety evidence.
    # --------------------------------------------------------

    combined = (
        f"{value or ''} "
        f"{evidence_text or ''}"
    ).strip()

    if (
        _is_uncertain_text(combined)
        and domain in {
            "risk",
            "safeguarding",
            "contraindications",
            "medical_history",
            "medication",
            "psychological_care",
            "psychiatric_care",
            "healthcare_professionals",
            "referral_permission",
        }
        and not _is_negative_text(combined)
    ):
        return None

    # --------------------------------------------------------
    # Verify client support.
    # --------------------------------------------------------

    if not _evidence_is_supported_by_client(
        item,
        client_texts,
    ):
        return None

    # --------------------------------------------------------
    # Status.
    # --------------------------------------------------------

    status = item.get(
        "status",
        "mentioned"
    )

    if status not in ALLOWED_STATUSES:
        status = "mentioned"

    item["status"] = status

    # --------------------------------------------------------
    # Confidence.
    # --------------------------------------------------------

    try:
        confidence = float(
            item.get(
                "confidence",
                0.5
            )
        )
    except (
        TypeError,
        ValueError
    ):
        confidence = 0.5

    item["confidence"] = max(
        0.0,
        min(
            confidence,
            1.0
        )
    )

    # --------------------------------------------------------
    # Flags.
    # --------------------------------------------------------

    flags = item.get(
        "flags",
        []
    )

    if not isinstance(
        flags,
        list
    ):
        flags = []

    item["flags"] = flags

    # --------------------------------------------------------
    # Applied-to-reasoning.
    #
    # The extractor should be conservative here.
    # It should not claim that the student applied evidence
    # merely because the client mentioned something.
    # --------------------------------------------------------

    item["applied_to_reasoning"] = bool(
        item.get(
            "applied_to_reasoning",
            False
        )
    )

    # --------------------------------------------------------
    # Clean negative safety flags.
    # --------------------------------------------------------

    item = _clean_negative_flags(
        item
    )

    # --------------------------------------------------------
    # Safety confidence.
    # --------------------------------------------------------

    item = _apply_safety_confidence(
        item
    )

    return item


# ============================================================
# DEDUPLICATE EVIDENCE
# ============================================================

def _deduplicate_evidence(
    evidence: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Prevent duplicate evidence records from being returned
    for the same domain/value/supporting statement.
    """

    result = []

    seen = set()

    for item in evidence:

        key = (
            item.get("domain"),
            _normalise_text(
                item.get("value", "")
            ),
            _normalise_text(
                item.get("evidence_text", "")
            ),
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(item)

    return result


# ============================================================
# EXTRACT CLINICAL EVIDENCE
# ============================================================

def extract_clinical_evidence(
    client: OpenAI,
    history: List[Dict[str, Any]],
    latest_student_text: str,
    latest_client_reply: str,
) -> List[Dict[str, Any]]:
    """
    Extract clinical evidence from a therapist/client conversation.

    Only client-established information should become evidence.

    Extraction failure returns [] and never breaks the consultation.
    """

    # ========================================================
    # NORMALISE EXISTING HISTORY
    # ========================================================

    conversation = _normalise_history(
        history
    )

    # ========================================================
    # AVOID DUPLICATING CURRENT EXCHANGE
    # ========================================================

    latest_student_text = str(
        latest_student_text or ""
    ).strip()

    latest_client_reply = str(
        latest_client_reply or ""
    ).strip()

    # --------------------------------------------------------
    # Add latest therapist message only if it is not already
    # the final matching therapist message.
    # --------------------------------------------------------

    if latest_student_text:

        already_present = (
            bool(conversation)
            and conversation[-1].get(
                "speaker"
            ) == "therapist"
            and conversation[-1].get(
                "text"
            ) == latest_student_text
        )

        if not already_present:

            conversation.append({
                "speaker": "therapist",
                "text": latest_student_text,
            })

    # --------------------------------------------------------
    # Add latest client message only if it is not already
    # present.
    # --------------------------------------------------------

    if latest_client_reply:

        already_present = (
            bool(conversation)
            and conversation[-1].get(
                "speaker"
            ) == "client"
            and conversation[-1].get(
                "text"
            ) == latest_client_reply
        )

        if not already_present:

            conversation.append({
                "speaker": "client",
                "text": latest_client_reply,
            })

    # ========================================================
    # NO CLIENT RESPONSE
    # ========================================================

    client_texts = _get_client_texts(
        conversation
    )

    if not client_texts:
        return []

    # ========================================================
    # EXTRACTION PAYLOAD
    # ========================================================

    payload = {
        "conversation": conversation,

        # Explicitly identify the latest exchange separately.
        # This helps the model focus on the new evidence while
        # retaining the previous context.
        "latest_exchange": {
            "therapist": latest_student_text,
            "client": latest_client_reply,
        },
    }

    # ========================================================
    # OPENAI REQUEST
    # ========================================================

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content": EXTRACTION_SYSTEM_PROMPT,
                },

                {
                    "role": "user",
                    "content": json.dumps(
                        payload,
                        ensure_ascii=False,
                    ),
                },

            ],

            response_format={
                "type": "json_object"
            },

            temperature=0,

            timeout=15,
        )

    except Exception as exc:

        print(
            "[Clinical Evidence Extraction Error]",
            type(exc).__name__,
            str(exc),
        )

        return []

    # ========================================================
    # RESPONSE CONTENT
    # ========================================================

    try:

        content = (
            response
            .choices[0]
            .message
            .content
        )

    except Exception as exc:

        print(
            "[Clinical Evidence Extraction Response Error]",
            type(exc).__name__,
            str(exc),
        )

        return []

    if not content:
        return []

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        parsed = json.loads(
            content
        )

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:

        print(
            "[Clinical Evidence JSON Parse Error]",
            type(exc).__name__,
            str(exc),
        )

        return []

    # ========================================================
    # EXTRACT LIST
    # ========================================================

    extracted = parsed.get(
        "evidence",
        []
    )

    if not isinstance(
        extracted,
        list
    ):
        return []

    # ========================================================
    # VALIDATE
    # ========================================================

    validated = []

    for item in extracted:

        validated_item = _validate_item(
            item,
            client_texts,
        )

        if validated_item is not None:

            validated.append(
                validated_item
            )

    # ========================================================
    # DEDUPLICATE
    # ========================================================

    validated = _deduplicate_evidence(
        validated
    )

    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print(
        "\n========== CLINICAL EVIDENCE =========="
    )

    print(
        "Extracted items:",
        len(extracted)
    )

    print(
        "Validated items:",
        len(validated)
    )

    for item in validated:

        print(
            f"- {item.get('domain')}: "
            f"{item.get('value')} "
            f"(confidence={item.get('confidence')})"
        )

    print(
        "========================================\n"
    )

    return validated