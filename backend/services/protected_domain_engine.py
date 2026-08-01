PROTECTED_DOMAINS = {
    "medication": [
        "medication",
        "medicine",
        "tablets",
        "prescription",
        "drug"
    ],

    "psychological_care": [
        "psychologist",
        "psychological care",
        "therapy",
        "therapist"
    ],

    "psychiatric_care": [
        "psychiatrist",
        "psychiatric"
    ],

    "previous_hypnosis": [
        "hypnotherapy",
        "hypnosis"
    ],

    "risk": [
        "harm yourself",
        "hurt yourself",
        "suicide",
        "self harm"
    ],

    "healthcare_professionals": [
        "healthcare professional",
        "doctor",
        "supporting you"
    ]
}


def detect_domain(question: str):

    question = question.lower()

    for domain, keywords in PROTECTED_DOMAINS.items():
        for keyword in keywords:
            if keyword in question:
                return domain

    return None


def is_defined(persona: dict, domain: str):

    healthcare = persona.get("healthcare", {})
    hypnosis = persona.get("hypnosis_history", {})
    safety = persona.get("safety", {})

    if domain == "medication":
        return healthcare.get("medication", {}).get("current") is not None

    if domain == "psychological_care":
        return healthcare.get("psychological_care") is not None

    if domain == "psychiatric_care":
        return healthcare.get("psychiatric_care") is not None

    if domain == "previous_hypnosis":
        return hypnosis.get("previous_experience") is not None

    if domain == "healthcare_professionals":
        return healthcare.get("professionals_involved") not in (None, [])

    if domain == "risk":
        return safety.get("risk_factors") not in (None, [])

    return True


def should_bypass_llm(question: str, persona: dict):

    domain = detect_domain(question)

    if domain is None:
        return False

    return not is_defined(persona, domain)

def process_protected_question(question: str, persona: dict):

    domain = detect_domain(question)

    if domain is None:
        return {
            "handled": False
        }

    if is_defined(persona, domain):
        return {
            "handled": False
        }

    return {
        "handled": True,
        "domain": domain,
        "instruction": f"""
The student's question concerns the protected domain '{domain}'.

The AUTHORITATIVE CLIENT CASE does NOT establish this information.

Do NOT answer Yes.
Do NOT answer No.
Do NOT invent absence of treatment.
Do NOT invent presence of treatment.
Do NOT infer the most likely situation.

Respond naturally with uncertainty while remaining conversational.
"""
    }