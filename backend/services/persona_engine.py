# backend/services/persona_engine.py
import random

personas = {
    "CBH": {
        1: [
            "I've been struggling with a lot of anxiety lately.",
            "I've been feeling very anxious, especially about work.",
            "I've been worrying a lot and it's starting to affect me."
        ],
        2: [
            "It started a few months ago after a stressful time.",
            "I think it began earlier this year when work got difficult.",
            "It's been building up over the past few months."
        ],
        3: [
            "My mind goes straight to worst case scenarios.",
            "I start imagining things going wrong.",
            "I keep worrying about what might happen.",
            "I picture situations where I don't cope well."
        ],
        4: [
            "I feel overwhelmed and quite nervous.",
            "I feel anxious and a bit on edge.",
            "I feel like I can't relax properly."
        ],
        5: [
            "I feel tightness in my chest.",
            "My shoulders get very tense.",
            "It feels like a weight on my chest sometimes."
        ],
        6: [
            "I remember feeling like this when I was younger during exams.",
            "I've had similar feelings before during stressful times.",
            "This isn't the first time I've felt like this."
        ],
        7: [
            "I want to feel calmer and more in control.",
            "I would like to stop overthinking everything.",
            "I want to feel more confident in myself."
        ],
        8: [
            "Will I still be aware during hypnosis?",
            "Can hypnosis help me control my thoughts?",
            "What does hypnosis actually feel like?"
        ]
    }
}


def get_persona_response(client_type, stage):
    persona = personas.get(client_type)

    if not persona:
        return "I'm not really sure how to explain it, I just know I've been feeling anxious."

    responses = persona.get(stage, persona[7])
    return random.choice(responses)