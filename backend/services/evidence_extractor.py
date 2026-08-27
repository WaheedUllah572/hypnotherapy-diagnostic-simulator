import json
from typing import Any, Dict, List

from openai import OpenAI

from services.clinical_evidence_engine import (
    EVIDENCE_DOMAINS
)


# ============================================================
# CLINICAL EVIDENCE EXTRACTION PROMPT
# ============================================================

EXTRACTION_SYSTEM_PROMPT = """
You are the Clinical Evidence Extraction component of an educational
hypnotherapy consultation simulator.

Your task is NOT to diagnose the client.

Your task is NOT to recommend treatment.

Your task is NOT to score the student.

Your task is ONLY to identify clinical evidence that has actually
been established in the supplied therapist/client conversation.

============================================================
CORE RULE
============================================================

Only extract information actually stated or clearly established
by the CLIENT.

A therapist question is NOT evidence.

A client's uncertainty is NOT evidence of the thing being asked.

A client's lack of memory is NOT evidence of the thing being asked.

============================================================
POLARITY
============================================================

You MUST distinguish three different situations.

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

Do NOT return positive risk evidence for this response.

If the only client response is uncertainty, return no evidence for
that domain unless another part of the conversation establishes an
actual fact.

============================================================
SAFETY QUESTIONS
============================================================

Safety-related questions require especially careful polarity.

These are NOT equivalent:

"No history of self-harm."

"I have harmed myself."

"I'm not sure whether I've harmed myself."

They mean:

negative established

positive established

unknown

respectively.

Likewise:

"No, I have never attempted suicide."

is NOT positive suicide evidence.

And:

"I'm not sure whether I've had suicidal thoughts."

is NOT positive suicidal-thought evidence.

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

Do not convert these into positive findings.

============================================================
UNCERTAINTY
============================================================

The following indicate uncertainty and must NOT become clinical
evidence by themselves:

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

"I'd have to think."

If uncertainty is the entire answer, do NOT extract a definite
clinical fact.

============================================================
BEHAVIOURAL INFORMATION
============================================================

If the client says:

"I don't really do much to relax."

that is an established behavioural statement.

If the client says:

"I'm not sure what I do to relax."

that is NOT a specific relaxation activity.

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
IMPORTANT SAFETY RULE
============================================================

Do NOT attach positive safety flags to negative statements.

For example:

Client:
"No, I don't have a history of self-harm."

MUST NOT produce:

{
  "domain": "safeguarding",
  "flags": ["safeguarding"]
}

unless the conversation contains separate positive safeguarding
information.

A negative statement may still be returned as evidence if useful,
but its value must preserve the negative meaning.

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

        role = message.get(
            "role"
        )

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
    "never attempted suicide",
    "no suicide attempts",
    "no history of suicide attempts",
    "no safeguarding concerns",
    "no safeguarding issues",
    "no safety concerns",
    "no known risk factors",
    "no risk factors",
    "no contraindications",
]


def _is_uncertain_text(
    text: str
) -> bool:

    value = (
        text or ""
    ).lower().strip()


    return any(
        phrase in value
        for phrase in UNCERTAINTY_PHRASES
    )


def _is_negative_text(
    text: str
) -> bool:

    value = (
        text or ""
    ).lower().strip()


    return any(
        phrase in value
        for phrase in NEGATIVE_PHRASES
    )


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
        # If the evidence is entirely uncertain, do not let
        # the extractor manufacture a clinical finding.
        # ----------------------------------------------------

        if _is_uncertain_text(
            combined_text
        ):

            # Allow uncertainty only for non-safety domains
            # where the evidence may contain an actual fact
            # elsewhere in the item.
            #
            # For safety domains, reject it entirely.
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
        # Negative safety evidence is allowed, but remove
        # accidental positive flags.
        # ----------------------------------------------------

        if (
            domain in {
                "risk",
                "safeguarding",
                "contraindications",
            }
            and _is_negative_text(
                combined_text
            )
        ):

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
            }


            flags = [
                flag
                for flag in flags
                if str(flag).lower()
                not in blocked_flags
            ]


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

    conversation = _normalise_history(
        history
    )


    if latest_student_text:

        conversation.append({

            "speaker":
                "therapist",

            "text":
                latest_student_text.strip()
        })


    if latest_client_reply:

        conversation.append({

            "speaker":
                "client",

            "text":
                latest_client_reply.strip()
        })


    payload = {
        "conversation":
            conversation
    }


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
                "integrated"

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
        # FINAL LOCAL VALIDATION
        # ====================================================

        valid_evidence = (
            _validate_extracted_evidence(
                valid_evidence
            )
        )


        return valid_evidence


    except Exception as exc:

        print(
            "[Clinical Evidence Extraction Error]",
            exc
        )

        # Evidence extraction must NEVER break
        # the actual client conversation.

        return []