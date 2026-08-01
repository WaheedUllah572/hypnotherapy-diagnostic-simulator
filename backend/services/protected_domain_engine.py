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

    UNCERTAIN_RESPONSES = {

    "medication":
        "I'm not really sure about that right now. I'd need to check.",

    "psychological_care":
        "I'm not completely sure about that at the moment.",

    "psychiatric_care":
        "I can't honestly say for certain right now.",

    "previous_hypnosis":
        "I'm not really sure. I can't clearly remember.",

    "healthcare_professionals":
        "I'm not certain about that at the moment.",

    "risk":
        "I'm not sure how to answer that right now."
}

    return {
    "handled": True,
    "instruction": f"""
The student's question concerns '{domain}'.

The client case does not establish this information.

Do NOT answer Yes.
Do NOT answer No.
Do NOT invent a fact.

Respond naturally with uncertainty.

Use wording similar to:

{UNCERTAIN_RESPONSES[domain]}
"""
}