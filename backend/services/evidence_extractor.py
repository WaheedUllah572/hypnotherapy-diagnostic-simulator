import json
from typing import Any, Dict, List

from openai import OpenAI

from services.clinical_evidence_engine import EVIDENCE_DOMAINS


EXTRACTION_SYSTEM_PROMPT = """
You are the Clinical Evidence Extraction component of an educational
hypnotherapy consultation simulator.

Your task is NOT to diagnose the client, recommend treatment, score the
student, or provide medical advice.

Your task is only to identify clinical evidence that has actually been
established in the supplied therapist/client conversation.

IMPORTANT RULES

1. Use only information supported by the conversation.
2. Never invent missing clinical information.
3. Do not interpret "not discussed" as "no".
4. Distinguish a therapist asking about something from the client actually
   providing evidence about it.
5. Different valid question wording must be treated equivalently.
6. Return only domains for which meaningful evidence has been established.
7. If information is ambiguous, use a lower confidence.
8. Safety-related information must be captured accurately without making
   diagnostic conclusions.

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

Evidence maturity statuses:

mentioned
clarified
understood
applied
integrated

Return valid JSON using this exact structure:

{
  "evidence": [
    {
      "domain": "domain_name",
      "value": "structured or concise evidence",
      "status": "mentioned",
      "confidence": 0.0,
      "evidence_text": "short supporting evidence from the conversation",
      "clinical_significance": null,
      "applied_to_reasoning": false,
      "flags": []
    }
  ]
}

If no meaningful evidence has been established, return:

{
  "evidence": []
}
"""


def _normalise_history(history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Convert frontend chat history into a clean representation for
    evidence extraction.
    """

    cleaned = []

    for message in history or []:
        role = message.get("role")
        text = str(message.get("text", "")).strip()

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


def extract_clinical_evidence(
    client: OpenAI,
    history: List[Dict[str, Any]],
    latest_student_text: str,
    latest_client_reply: str,
) -> List[Dict[str, Any]]:
    """
    Analyse the consultation and return evidence that has actually
    been established.

    This function does not update session state itself.
    """

    conversation = _normalise_history(history)

    if latest_student_text:
        conversation.append({
            "speaker": "therapist",
            "text": latest_student_text.strip()
        })

    if latest_client_reply:
        conversation.append({
            "speaker": "client",
            "text": latest_client_reply.strip()
        })

    payload = {
        "conversation": conversation
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": EXTRACTION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        payload,
                        ensure_ascii=False
                    )
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            timeout=15
        )

        content = response.choices[0].message.content

        if not content:
            return []

        parsed = json.loads(content)

        extracted = parsed.get("evidence", [])

        if not isinstance(extracted, list):
            return []

        valid_evidence = []

        for item in extracted:

            if not isinstance(item, dict):
                continue

            domain = item.get("domain")

            if domain not in EVIDENCE_DOMAINS:
                continue

            status = item.get("status", "mentioned")

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
                    item.get("confidence", 0.5)
                )
            except (TypeError, ValueError):
                confidence = 0.5

            confidence = max(
                0.0,
                min(confidence, 1.0)
            )

            flags = item.get("flags", [])

            if not isinstance(flags, list):
                flags = []

            valid_evidence.append({
                "domain": domain,
                "value": item.get("value"),
                "status": status,
                "confidence": confidence,
                "evidence_text": item.get(
                    "evidence_text"
                ),
                "clinical_significance": item.get(
                    "clinical_significance"
                ),
                "applied_to_reasoning": bool(
                    item.get(
                        "applied_to_reasoning",
                        False
                    )
                ),
                "flags": flags
            })

        return valid_evidence

    except Exception as exc:

        print(
            f"[Clinical Evidence Extraction Error] {exc}"
        )

        # Evidence extraction must never break the actual
        # client conversation.
        return []