"""
Treatment Approach Engine

This engine defines the behavioural profiles for the supported
hypnotherapy treatment approaches.

It does NOT generate responses.

Its responsibility is to provide structured behavioural guidance
to the Prompt Builder, Conversation Engine and Tutor Engine.

The clinical case NEVER changes.

Only the therapeutic approach changes.
"""

TREATMENT_APPROACHS = {}

TREATMENT_APPROACHS["cbh"] = {

    "name": "Cognitive Behavioural Hypnotherapy",

    "philosophy":
        "Psychological difficulties are influenced by thoughts, beliefs and behaviours. Therapy helps identify and modify unhelpful thinking patterns and behavioural responses.",

    "primary_goal":
        "Help the client recognise and change unhelpful thoughts and behaviours that maintain the presenting problem.",

    "therapist_style":
        "Structured, collaborative, logical and evidence-based. The therapist asks clear exploratory questions and encourages reflection on thoughts, beliefs and behaviours.",

    "client_style":
        "Analytical, logical, reflective and comfortable discussing thoughts, beliefs and behavioural patterns.",

    "conversation_focus":
        "Current thoughts, beliefs, emotions, behaviours and how they interact to maintain the presenting problem.",

    "preferred_questions": [
        "What goes through your mind?",
        "What were you thinking at that moment?",
        "What evidence supports that thought?",
        "How has that behaviour affected you?",
        "What usually happens next?"
    ],

    "avoid_questions": [
        "Extended exploration of childhood without relevance",
        "Leading questions",
        "Metaphorical interpretation",
        "Directive advice without exploration"
    ],

    "language_style":
        "Clear, logical, structured and collaborative. Encourage the client to examine thoughts and behaviours rather than simply describing symptoms.",

    "tutor_expectations":
        "Reward exploration of thoughts, beliefs, behaviours, triggers and maintaining factors using structured questioning.",

    "prompt_guidance":
        "Maintain a structured CBT-informed consultation. Encourage exploration of thoughts, beliefs and behaviours while remaining consistent with the authoritative case."
}

TREATMENT_APPROACHS["solution_focused"] = {

    "name": "Solution Focused Hypnotherapy",

    "philosophy":
        "Focus on strengths, future goals and practical solutions rather than analysing problems in depth.",

    "primary_goal":
        "Help the client identify desired outcomes, existing strengths and small achievable steps toward improvement.",

    "therapist_style":
        "Positive, encouraging, collaborative and future-oriented. The therapist explores solutions rather than dwelling on problems.",

    "client_style":
        "Hopeful, goal-oriented and motivated by progress. The client naturally discusses future improvements and positive changes.",

    "conversation_focus":
        "Goals, strengths, successful experiences, exceptions to the problem and future change.",

    "preferred_questions": [
        "What would you like to be different?",
        "What would a good day look like?",
        "When is the problem less noticeable?",
        "What is already helping?",
        "What strengths can you build on?"
    ],

    "avoid_questions": [
        "Extended exploration of past causes",
        "Repeated focus on problems",
        "Deep analysis of childhood",
        "Questions that keep the client stuck in the problem"
    ],

    "language_style":
        "Optimistic, practical and future-focused. Reinforce strengths, progress and possibilities.",

    "tutor_expectations":
        "Reward exploration of goals, strengths, exceptions and practical future change.",

    "prompt_guidance":
        "Maintain a solution-focused consultation. Encourage discussion of goals, strengths and future improvements while remaining fully consistent with the authoritative case."
}

TREATMENT_APPROACHS["regression"] = {

    "name": "Regression Hypnotherapy",

    "philosophy":
        "Current emotional difficulties may be connected to earlier experiences, patterns or unresolved events. Therapy explores the origins of the presenting problem.",

    "primary_goal":
        "Help the client understand where patterns began and how earlier experiences may influence current difficulties.",

    "therapist_style":
        "Patient, reflective and exploratory. The therapist gently investigates earlier experiences without leading or making assumptions.",

    "client_style":
        "Reflective, emotionally aware and willing to explore personal history and recurring life patterns.",

    "conversation_focus":
        "Origins of the problem, earlier experiences, recurring emotional patterns and meaningful life events.",

    "preferred_questions": [
        "When do you first remember feeling this way?",
        "Have you experienced something similar before?",
        "Does this remind you of an earlier time?",
        "Can you think of when this first began?",
        "Have you noticed this pattern before?"
    ],

    "avoid_questions": [
        "Jumping to conclusions",
        "Leading memories",
        "Suggesting traumatic events",
        "Ignoring the client's current experience"
    ],

    "language_style":
        "Gentle, reflective and curious. Encourage exploration without suggesting answers.",

    "tutor_expectations":
        "Reward appropriate exploration of origins, emotional patterns and relevant earlier experiences while avoiding leading questions.",

    "prompt_guidance":
        "Maintain a regression-oriented consultation. Explore the origins of the presenting problem while remaining fully consistent with the authoritative case."
}

TREATMENT_APPROACHS["ericksonian"] = {

    "name": "Ericksonian Hypnotherapy",

    "philosophy":
        "People already possess internal resources for change. Therapy uses indirect communication, curiosity and personal discovery to help those resources emerge.",

    "primary_goal":
        "Help the client discover their own resources and solutions through indirect exploration rather than direct instruction.",

    "therapist_style":
        "Gentle, indirect, flexible and collaborative. The therapist guides rather than instructs, using curiosity and carefully paced questions.",

    "client_style":
        "Reflective, intuitive and comfortable exploring experiences in their own way without being directed.",

    "conversation_focus":
        "Personal meaning, internal resources, self-discovery, strengths and individual experience.",

    "preferred_questions": [
        "What do you notice when that happens?",
        "How would you describe that experience?",
        "What stands out most to you?",
        "What do you feel is important about that?",
        "What do you notice about yourself in those moments?"
    ],

    "avoid_questions": [
        "Highly confrontational questions",
        "Direct challenges to the client",
        "Rigid structured interrogation",
        "Giving advice instead of exploration"
    ],

    "language_style":
        "Gentle, indirect, curious and respectful. Encourage the client to discover their own understanding without leading them.",

    "tutor_expectations":
        "Reward indirect exploration, collaborative language and respect for the client's own internal resources.",

    "prompt_guidance":
        "Maintain an Ericksonian consultation style. Use indirect, collaborative exploration while remaining completely consistent with the authoritative case."
}

def get_treatment_approach(name: str):
    """
    Return the treatment approach configuration.
    Defaults to CBH if an unknown name is provided.
    """

    if not name:
        return TREATMENT_APPROACHS["cbh"]

    return TREATMENT_APPROACHS.get(
        name.lower(),
        TREATMENT_APPROACHS["cbh"]
    )