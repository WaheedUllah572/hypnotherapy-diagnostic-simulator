import json
import re
from typing import Any, Dict, List

from openai import OpenAI

from services.clinical_evidence_engine import (
    EVIDENCE_DOMAINS
)


# ============================================================
# PHASE 2B — CLINICAL EVIDENCE EXTRACTION
# ============================================================
#
# IMPORTANT ARCHITECTURE
#
# The LLM is used for semantic extraction.
#
# Deterministic validation is then applied to safety-critical
# evidence so that an LLM domain-classification mistake cannot
# turn a negative risk statement into safeguarding evidence.
#
# Examples:
#
# "No history of self-harm."
#     -> risk
#
# "I have harmed myself."
#     -> risk
#
# "I'm not sure whether I've harmed myself."
#     -> NO risk evidence
#
# "There are safeguarding concerns at home."
#     -> safeguarding
#
# ============================================================


# ============================================================
# EXTRACTION SYSTEM PROMPT
# ============================================================

EXTRACTION_SYSTEM_PROMPT = """
You are the Clinical Evidence Extraction component of an educational
hypnotherapy consultation simulator.

Your task is NOT to diagnose the client.

Your task is NOT to recommend treatment.

Your task is NOT to score the student.

Your task is ONLY to identify clinical evidence that has actually been
established in the supplied therapist/client conversation.

============================================================
CORE RULE
============================================================

Only extract information actually stated or clearly established
by the CLIENT.

A therapist question is NOT evidence.

A client's uncertainty is NOT evidence of the thing being asked.

A client's lack of memory is NOT evidence of the thing being asked.

Do not infer facts from the therapist's question.

============================================================
POLARITY
============================================================

You MUST distinguish:

1. POSITIVE / ESTABLISHED

Example:

Client:
"Yes, I have taken medication for anxiety."

This establishes medication information.

2. NEGATIVE / ESTABLISHED

Example:

Client:
"No, I don't have a history of self-harm."

This establishes a NEGATIVE self-harm-history fact.

It does NOT establish positive self-harm risk.

3. UNKNOWN / UNESTABLISHED

Example:

Client:
"I'm not sure whether I've ever had thoughts like that."

This does NOT establish self-harm thoughts.

If the only client response is uncertainty, return no evidence
for that domain unless another part of the conversation establishes
an actual fact.

============================================================
SAFETY DOMAIN DEFINITIONS
============================================================

Use these domains carefully.

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
- explicit absence/history of the above

Examples:

"No, I don't have a history of self-harm."
-> risk

"I have never attempted suicide."
-> risk

"I sometimes think about harming myself."
-> risk

"I'm not sure whether I've had thoughts like that."
-> NO risk evidence

IMPORTANT:
Self-harm and suicide-related information belongs to "risk",
NOT "safeguarding".

safeguarding
------------
Use "safeguarding" only for actual safeguarding information,
such as:

- abuse
- neglect
- exploitation
- domestic abuse
- child/adult safeguarding concerns
- unsafe living situation
- coercion
- vulnerability requiring safeguarding consideration

Do NOT classify self-harm history as safeguarding merely because
it is safety-related.

contraindications
-----------------
Use for actual contraindication information.

medical_history
---------------
Use for actual medical history.

medication
----------
Use for actual medication information.

psychological_care
------------------
Use for actual psychological treatment/care.

psychiatric_care
----------------
Use for actual psychiatric treatment/care.

healthcare_professionals
------------------------
Use for actual healthcare professional involvement.

referral_permission
-------------------
Use for actual referral/permission information.

============================================================
NEGATION
============================================================

Preserve explicit negative statements as negative evidence when
they are clinically relevant.

Examples:

"No history of self-harm."
"No current medication."
"I've never seen a psychiatrist."
"No contraindications that I know of."

Do NOT convert these into positive findings.

Do NOT attach positive risk/safeguarding flags to negative statements.

============================================================
UNCERTAINTY
============================================================

The following indicate uncertainty:

"I'm not sure."
"I don't know."
"I can't remember."
"I'd need to think about it."
"I'd need to check."
"I'm not certain."
"I can't say for certain."
"I don't remember whether..."
"Perhaps."
"Maybe."

If uncertainty is the entire answer, do NOT extract a definite
clinical fact.

Example:

Therapist:
"Have you ever had thoughts of harming yourself?"

Client:
"I'm not sure whether I've had thoughts like that."

Return:

{
  "evidence": []
}

Do NOT convert the uncertainty into risk evidence.

============================================================
BEHAVIOURAL INFORMATION
============================================================

If the client says:

"I don't really do much to relax."

That is an established behavioural statement.

If the client says:

"I'm not sure what I do to relax."

That does NOT establish a specific relaxation activity.

Do not invent an activity.

============================================================
DOMAINS
============================================================

Allowed evidence domains:

presenting_problem
history
symptoms
triggers
maintaining_factors
functional_impact
coping_strategies
previous_hypnosis
medical_history
psychological_care
psychiatric_care
medication
healthcare_professionals
referral_permission
why_now
readiness
goals
risk
contraindications
safeguarding
professional_boundaries
modality
treatment_reasoning

============================================================
EVIDENCE STATUS
============================================================

Allowed statuses:

mentioned
clarified
understood
applied
integrated

============================================================
OUTPUT
============================================================

Return valid JSON using exactly:

{
  "evidence": [
    {
      "domain": "domain_name",
      "value": "structured or concise evidence",
      "status": "mentioned",
      "confidence": 0.0,
      "evidence_text": "short supporting evidence",
      "clinical_significance": null,
      "applied_to_reasoning": false,
      "flags": []
    }
  ]
}

If no meaningful evidence has been established:

{
  "evidence": []
}

Never create evidence merely because the therapist asked a question.
"""


# ============================================================
# HISTORY NORMALISATION
# ============================================================

def _normalise_history(
    history: List[Dict[str, Any]]
) -> List[Dict[str, str]]:

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
                "text": text
            })

        elif role == "client":

            cleaned.append({
                "speaker": "client",
                "text": text
            })

    return cleaned


# ============================================================
# TEXT HELPERS
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
]


NEGATIVE_PHRASES = [

    "no history of self-harm",
    "no history of self harm",

    "no self-harm history",
    "no self harm history",

    "never harmed myself",
    "never harmed themselves",

    "have never harmed myself",
    "have never harmed themselves",

    "never attempted suicide",
    "no suicide attempts",

    "no history of suicide attempts",

    "no suicidal thoughts",
    "no history of suicidal thoughts",

    "no thoughts of harming myself",
    "no thoughts of harming themselves",

    "no thoughts of harming anyone",
    "no thoughts of harming someone",

    "no safeguarding concerns",
    "no safeguarding issues",

    "no safety concerns",
    "no known risk factors",
    "no risk factors",

    "no contraindications",
]


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

    "harming someone else",
    "harm someone else",
    "harmed someone else",

    "harming another person",
    "harm another person",
]


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
# NORMALISE TEXT
# ============================================================

def _normalise_text(
    text: Any
) -> str:

    return re.sub(
        r"\s+",
        " ",
        str(text or "").lower().strip()
    )


# ============================================================
# UNCERTAINTY CHECK
# ============================================================

def _is_uncertain_text(
    text: str
) -> bool:

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
# SAFETY DOMAIN DETECTION
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
# DETERMINISTIC SAFETY DOMAIN CORRECTION
# ============================================================
#
# This is the critical fix.
#
# The LLM may return:
#
# {
#   "domain": "safeguarding",
#   "value": "No history of self-harm."
# }
#
# We correct it to:
#
# {
#   "domain": "risk",
#   "value": "No history of self-harm."
# }
#
# because self-harm is a risk domain.
#
# ============================================================

def _correct_safety_domain(
    item: Dict[str, Any]
) -> Dict[str, Any]:

    domain = item.get(
        "domain"
    )

    value = item.get(
        "value"
    )

    evidence_text = item.get(
        "evidence_text"
    )

    combined_text = (
        f"{value or ''} "
        f"{evidence_text or ''}"
    ).strip()

    # --------------------------------------------------------
    # Self-harm / suicide always belongs to risk.
    # --------------------------------------------------------

    if _contains_self_harm_information(
        combined_text
    ):

        item["domain"] = "risk"

        # Negative self-harm information must never carry
        # positive safety flags.
        if _is_negative_text(
            combined_text
        ):

            item["flags"] = []

        return item

    # --------------------------------------------------------
    # Genuine safeguarding remains safeguarding.
    # --------------------------------------------------------

    if _contains_safeguarding_information(
        combined_text
    ):

        item["domain"] = "safeguarding"

        return item

    return item


# ============================================================
# REMOVE POSITIVE FLAGS FROM NEGATIVE SAFETY EVIDENCE
# ============================================================

def _remove_positive_safety_flags(
    item: Dict[str, Any]
) -> Dict[str, Any]:

    domain = item.get(
        "domain"
    )

    value = item.get(
        "value"
    )

    evidence_text = item.get(
        "evidence_text"
    )

    combined_text = (
        f"{value or ''} "
        f"{evidence_text or ''}"
    ).strip()

    if domain not in {
        "risk",
        "safeguarding",
        "contraindications",
    }:

        return item

    if not _is_negative_text(
        combined_text
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
        "safety_concern",
        "safeguarding",
        "contraindication",
        "risk_positive",
        "safeguarding_positive",
        "safety_risk",
    }

    cleaned_flags = []

    for flag in flags:

        flag_text = str(
            flag
        ).strip().lower()

        if flag_text in blocked_flags:
            continue

        if flag not in cleaned_flags:
            cleaned_flags.append(flag)

    item["flags"] = cleaned_flags

    return item


# ============================================================
# LOCAL SAFETY VALIDATION
# ============================================================

def _validate_extracted_evidence(
    evidence: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    validated = []

    for item in evidence:

        if not isinstance(
            item,
            dict
        ):

            continue

        domain = item.get(
            "domain"
        )

        if domain not in EVIDENCE_DOMAINS:

            continue

        value = item.get(
            "value"
        )

        evidence_text = str(
            item.get(
                "evidence_text",
                ""
            )
        )

        combined_text = (
            f"{value or ''} "
            f"{evidence_text}"
        ).strip()

        # ----------------------------------------------------
        # FIRST:
        # Correct safety domain.
        # ----------------------------------------------------

        item = _correct_safety_domain(
            item
        )

        domain = item.get(
            "domain"
        )

        # ----------------------------------------------------
        # If domain changed, make sure it remains valid.
        # ----------------------------------------------------

        if domain not in EVIDENCE_DOMAINS:
            continue

        # ----------------------------------------------------
        # UNKNOWN / UNCERTAIN SAFETY ANSWERS
        # ----------------------------------------------------

        if _is_uncertain_text(
            combined_text
        ):

            if domain in {

                "risk",
                "safeguarding",
                "contraindications",
                "medical_history",
                "medication",
                "psychological_care",
                "psychiatric_care",
                "healthcare_professionals",
                "referral_permission",

            }:

                continue

        # ----------------------------------------------------
        # NEGATIVE SAFETY EVIDENCE
        # ----------------------------------------------------

        item = _remove_positive_safety_flags(
            item
        )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

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

        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )

        item["confidence"] = confidence

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status = item.get(
            "status",
            "mentioned"
        )

        if status not in {

            "mentioned",
            "clarified",
            "understood",
            "applied",
            "integrated",

        }:

            status = "mentioned"

        item["status"] = status

        # ----------------------------------------------------
        # Flags
        # ----------------------------------------------------

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

        validated.append(
            item
        )

    return validated


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_clinical_evidence(
    client: OpenAI,
    history: List[Dict[str, Any]],
    latest_student_text: str,
    latest_client_reply: str,
) -> List[Dict[str, Any]]:
    """
    Extract clinical evidence from the conversation.

    The LLM performs semantic extraction.

    Deterministic validation then protects safety-critical
    classification and polarity.
    """

    conversation = _normalise_history(
        history
    )

    # --------------------------------------------------------
    # Add current therapist question
    # --------------------------------------------------------

    if latest_student_text:

        conversation.append({

            "speaker":
                "therapist",

            "text":
                latest_student_text.strip()

        })

    # --------------------------------------------------------
    # Add current client response
    # --------------------------------------------------------

    if latest_client_reply:

        conversation.append({

            "speaker":
                "client",

            "text":
                latest_client_reply.strip()

        })

    # --------------------------------------------------------
    # Nothing to analyse
    # --------------------------------------------------------

    if not conversation:

        return []

    payload = {

        "conversation":
            conversation

    }

    # ========================================================
    # OPENAI EXTRACTION
    # ========================================================

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {

                    "role":
                        "system",

                    "content":
                        EXTRACTION_SYSTEM_PROMPT

                },

                {

                    "role":
                        "user",

                    "content":
                        json.dumps(
                            payload,
                            ensure_ascii=False
                        )

                }

            ],

            response_format={
                "type":
                    "json_object"
            },

            temperature=0,

            timeout=15
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:

            return []

        parsed = json.loads(
            content
        )

        print(
    "\n========== RAW EVIDENCE EXTRACTION JSON =========="
)

print(
    json.dumps(
        parsed,
        ensure_ascii=False,
        indent=2
    )
)

print(
    "==================================================\n"
)

        extracted = parsed.get(
            "evidence",
            []
        )

        if not isinstance(
            extracted,
            list
        ):

            return []

        valid_evidence = []

        # ====================================================
        # NORMALISE LLM OUTPUT
        # ====================================================

        for item in extracted:

            if not isinstance(
                item,
                dict
            ):

                continue

            domain = item.get(
                "domain"
            )

            if domain not in EVIDENCE_DOMAINS:

                continue

            status = item.get(
                "status",
                "mentioned"
            )

            if status not in {

                "mentioned",
                "clarified",
                "understood",
                "applied",
                "integrated",

            }:

                status = "mentioned"

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

            confidence = max(
                0.0,
                min(
                    confidence,
                    1.0
                )
            )

            flags = item.get(
                "flags",
                []
            )

            if not isinstance(
                flags,
                list
            ):

                flags = []

            valid_evidence.append({

                "domain":
                    domain,

                "value":
                    item.get(
                        "value"
                    ),

                "status":
                    status,

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

                "applied_to_reasoning":
                    bool(
                        item.get(
                            "applied_to_reasoning",
                            False
                        )
                    ),

                "flags":
                    flags

            })

        # ====================================================
        # FINAL DETERMINISTIC VALIDATION
        # ====================================================

        valid_evidence = (
            _validate_extracted_evidence(
                valid_evidence
            )
        )

        # ====================================================
        # DEBUG
        # ====================================================

        print(
            "\n========== EVIDENCE VALIDATION =========="
        )

        print(
            "RAW EXTRACTED:"
        )

        print(
            extracted
        )

        print(
            "VALIDATED:"
        )

        print(
            valid_evidence
        )

        print(
            "==========================================\n"
        )

        return valid_evidence

    except Exception as exc:

        print(
            "[Clinical Evidence Extraction Error]",
            type(exc).__name__,
            str(exc)
        )

        # Evidence extraction must NEVER break
        # the actual client conversation.

        return []