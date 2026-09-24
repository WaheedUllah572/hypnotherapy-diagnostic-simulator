"""
Treatment Approach Engine

This engine defines the behavioural profiles for the supported
hypnotherapy treatment approaches.

It does NOT generate responses.

Its responsibility is to provide structured behavioural guidance
to the Prompt Builder, Conversation Engine and Tutor Engine.

IMPORTANT:

The treatment approach must NEVER override the authoritative
clinical case.

The case remains the source of truth for:

- symptoms
- history
- triggers
- maintaining factors
- goals
- healthcare information
- medication
- psychological / psychiatric care
- safety information
- previous hypnosis
- client personality
- client experiences

The treatment approach only influences:

- therapist communication style
- exploration style
- conversational focus
- questioning style
- language style

It must never cause the client to invent facts.
"""

from typing import Any, Dict


# ============================================================
# SUPPORTED TREATMENT APPROACHES
# ============================================================

TREATMENT_APPROACHS: Dict[str, Dict[str, Any]] = {}


# ============================================================
# COGNITIVE BEHAVIOURAL HYPNOTHERAPY
# ============================================================

TREATMENT_APPROACHS["cbh"] = {

    "key": "cbh",

    "name": "Cognitive Behavioural Hypnotherapy",

    "philosophy": (
        "Psychological difficulties are influenced by thoughts, "
        "beliefs and behaviours. Therapy helps identify and modify "
        "unhelpful thinking patterns and behavioural responses."
    ),

    "primary_goal": (
        "Help the client recognise and change unhelpful thoughts "
        "and behaviours that maintain the presenting problem."
    ),

    "therapist_style": (
        "Structured, collaborative, logical and evidence-based. "
        "The therapist asks clear exploratory questions and "
        "encourages reflection on thoughts, beliefs and behaviours."
    ),

    "client_style": (
        "Analytical, logical, reflective and comfortable discussing "
        "thoughts, beliefs and behavioural patterns."
    ),

    "conversation_focus": (
        "Current thoughts, beliefs, emotions, behaviours and how "
        "they interact to maintain the presenting problem."
    ),

    "preferred_questions": [
        "What goes through your mind?",
        "What were you thinking at that moment?",
        "What evidence supports that thought?",
        "How has that behaviour affected you?",
        "What usually happens next?",
    ],

    "avoid_questions": [
        "Extended exploration of childhood without relevance",
        "Leading questions",
        "Metaphorical interpretation",
        "Directive advice without exploration",
    ],

    "language_style": (
        "Clear, logical, structured and collaborative. Encourage "
        "the client to examine thoughts and behaviours rather than "
        "simply describing symptoms."
    ),

    "tutor_expectations": (
        "Reward exploration of thoughts, beliefs, behaviours, "
        "triggers and maintaining factors using structured "
        "questioning."
    ),

    "prompt_guidance": (
        "Maintain a structured CBT-informed consultation. "
        "Encourage exploration of thoughts, beliefs and behaviours "
        "while remaining consistent with the authoritative case."
    ),
}


# ============================================================
# SOLUTION FOCUSED HYPNOTHERAPY
# ============================================================

TREATMENT_APPROACHS["solution_focused"] = {

    "key": "solution_focused",

    "name": "Solution Focused Hypnotherapy",

    "philosophy": (
        "Focus on strengths, future goals and practical solutions "
        "rather than analysing problems in depth."
    ),

    "primary_goal": (
        "Help the client identify desired outcomes, existing "
        "strengths and small achievable steps toward improvement."
    ),

    "therapist_style": (
        "Positive, encouraging, collaborative and future-oriented. "
        "The therapist explores solutions rather than dwelling on "
        "problems."
    ),

    "client_style": (
        "Hopeful, goal-oriented and motivated by progress. "
        "The client naturally discusses future improvements and "
        "positive changes."
    ),

    "conversation_focus": (
        "Goals, strengths, successful experiences, exceptions to "
        "the problem and future change."
    ),

    "preferred_questions": [
        "What would you like to be different?",
        "What would a good day look like?",
        "When is the problem less noticeable?",
        "What is already helping?",
        "What strengths can you build on?",
    ],

    "avoid_questions": [
        "Extended exploration of past causes",
        "Repeated focus on problems",
        "Deep analysis of childhood",
        "Questions that keep the client stuck in the problem",
    ],

    "language_style": (
        "Optimistic, practical and future-focused. Reinforce "
        "strengths, progress and possibilities."
    ),

    "tutor_expectations": (
        "Reward exploration of goals, strengths, exceptions and "
        "practical future change."
    ),

    "prompt_guidance": (
        "Maintain a solution-focused consultation. Encourage "
        "discussion of goals, strengths and future improvements "
        "while remaining fully consistent with the authoritative "
        "case. Do not force optimism or deny distress when the "
        "case supports genuine distress."
    ),
}


# ============================================================
# REGRESSION HYPNOTHERAPY
# ============================================================

TREATMENT_APPROACHS["regression"] = {

    "key": "regression",

    "name": "Regression Hypnotherapy",

    "philosophy": (
        "Current emotional difficulties may be connected to earlier "
        "experiences, patterns or unresolved events. Therapy explores "
        "the origins of the presenting problem."
    ),

    "primary_goal": (
        "Help the client understand where patterns began and how "
        "earlier experiences may influence current difficulties."
    ),

    "therapist_style": (
        "Patient, reflective and exploratory. The therapist gently "
        "investigates earlier experiences without leading or making "
        "assumptions."
    ),

    "client_style": (
        "Reflective, emotionally aware and willing to explore "
        "personal history and recurring life patterns."
    ),

    "conversation_focus": (
        "Origins of the problem, earlier experiences, recurring "
        "emotional patterns and meaningful life events."
    ),

    "preferred_questions": [
        "When do you first remember feeling this way?",
        "Have you experienced something similar before?",
        "Does this remind you of an earlier time?",
        "Can you think of when this first began?",
        "Have you noticed this pattern before?",
    ],

    "avoid_questions": [
        "Jumping to conclusions",
        "Leading memories",
        "Suggesting traumatic events",
        "Ignoring the client's current experience",
    ],

    "language_style": (
        "Gentle, reflective and curious. Encourage exploration "
        "without suggesting answers."
    ),

    "tutor_expectations": (
        "Reward appropriate exploration of origins, emotional "
        "patterns and relevant earlier experiences while avoiding "
        "leading questions."
    ),

    "prompt_guidance": (
        "Maintain a regression-oriented consultation. Explore "
        "the origins of the presenting problem while remaining "
        "fully consistent with the authoritative case. Never "
        "suggest, implant, manufacture or assume a memory, trauma, "
        "cause or past event that the client has not independently "
        "provided."
    ),
}


# ============================================================
# ERICKSONIAN HYPNOTHERAPY
# ============================================================

TREATMENT_APPROACHS["ericksonian"] = {

    "key": "ericksonian",

    "name": "Ericksonian Hypnotherapy",

    "philosophy": (
        "People already possess internal resources for change. "
        "Therapy uses indirect communication, curiosity and "
        "personal discovery to help those resources emerge."
    ),

    "primary_goal": (
        "Help the client discover their own resources and "
        "solutions through indirect exploration rather than "
        "direct instruction."
    ),

    "therapist_style": (
        "Gentle, indirect, flexible and collaborative. The therapist "
        "guides rather than instructs, using curiosity and carefully "
        "paced questions."
    ),

    "client_style": (
        "Reflective, intuitive and comfortable exploring experiences "
        "in their own way without being directed."
    ),

    "conversation_focus": (
        "Personal meaning, internal resources, self-discovery, "
        "strengths and individual experience."
    ),

    "preferred_questions": [
        "What do you notice when that happens?",
        "How would you describe that experience?",
        "What stands out most to you?",
        "What do you feel is important about that?",
        "What do you notice about yourself in those moments?",
    ],

    "avoid_questions": [
        "Highly confrontational questions",
        "Direct challenges to the client",
        "Rigid structured interrogation",
        "Giving advice instead of exploration",
    ],

    "language_style": (
        "Gentle, indirect, curious and respectful. Encourage the "
        "client to discover their own understanding without leading them."
    ),

    "tutor_expectations": (
        "Reward indirect exploration, collaborative language and "
        "respect for the client's own internal resources."
    ),

    "prompt_guidance": (
        "Maintain an Ericksonian consultation style. Use indirect, "
        "collaborative exploration while remaining completely "
        "consistent with the authoritative case."
    ),
}


# ============================================================
# NORMALISE APPROACH NAME
# ============================================================

def normalise_treatment_approach(name: Any) -> str:
    """
    Convert a treatment approach name into its canonical key.

    Examples:

        "CBH"                    -> "cbh"
        "Cognitive Behavioural Hypnotherapy" -> "cbh"
        "SH"                     -> "solution_focused"
        "Solution Focused Hypnotherapy" -> "solution_focused"
        "Regression"             -> "regression"
        "Ericksonian"             -> "ericksonian"

    Unknown values return an empty string rather than silently
    pretending they are CBH.
    """

    if not isinstance(name, str):
        return ""

    value = name.strip().lower()

    if not value:
        return ""

    aliases = {
        "cbh": "cbh",
        "cognitive behavioural hypnotherapy": "cbh",
        "cognitive behavioral hypnotherapy": "cbh",
        "cognitive behavioural": "cbh",
        "cognitive behavioral": "cbh",

        "sh": "solution_focused",
        "solution focused": "solution_focused",
        "solution-focused": "solution_focused",
        "solution focused hypnotherapy": "solution_focused",
        "solution-focused hypnotherapy": "solution_focused",

        "regression": "regression",
        "regression hypnotherapy": "regression",

        "ericksonian": "ericksonian",
        "ericksonian hypnotherapy": "ericksonian",
    }

    return aliases.get(
        value,
        value if value in TREATMENT_APPROACHS else "",
    )


# ============================================================
# GET TREATMENT APPROACH
# ============================================================

def get_treatment_approach(
    name: str,
) -> Dict[str, Any]:
    """
    Return the treatment approach configuration.

    Backward compatibility:
    Unknown or missing values still fall back to CBH, matching
    the original public behaviour of this module.

    The canonical key can be obtained separately with
    normalise_treatment_approach().
    """

    key = normalise_treatment_approach(
        name
    )

    if not key:
        return TREATMENT_APPROACHS["cbh"]

    return TREATMENT_APPROACHS.get(
        key,
        TREATMENT_APPROACHS["cbh"],
    )


# ============================================================
# GET TREATMENT APPROACH KEY
# ============================================================

def get_treatment_approach_key(
    name: str,
) -> str:
    """
    Return the canonical treatment approach key.

    Unknown or missing values fall back to CBH for compatibility.
    """

    key = normalise_treatment_approach(
        name
    )

    return key or "cbh"


# ============================================================
# GET TREATMENT PROMPT
# ============================================================

def get_treatment_prompt(
    name: str,
) -> str:
    """
    Build a structured treatment-approach prompt.

    The prompt explicitly states that the approach is behavioural
    guidance and cannot override case facts.
    """

    approach = get_treatment_approach(
        name
    )

    preferred_questions = "\n".join(
        f"- {question}"
        for question in approach.get(
            "preferred_questions",
            [],
        )
    )

    avoid_questions = "\n".join(
        f"- {question}"
        for question in approach.get(
            "avoid_questions",
            [],
        )
    )

    return f"""
TREATMENT APPROACH
{approach["name"]}

ROLE OF THIS APPROACH

The treatment approach controls communication style,
exploration style and therapeutic questioning.

It does NOT change the authoritative clinical case.

CASE AUTHORITY RULE

The authoritative case remains the source of truth for:

- symptoms
- history
- triggers
- maintaining factors
- goals
- healthcare information
- medication
- psychological care
- psychiatric care
- previous hypnosis
- safety information
- client experiences

Never invent or alter case facts because of the treatment approach.

PHILOSOPHY
{approach["philosophy"]}

PRIMARY GOAL
{approach["primary_goal"]}

THERAPIST STYLE
{approach["therapist_style"]}

CLIENT STYLE
{approach["client_style"]}

CONVERSATION FOCUS
{approach["conversation_focus"]}

LANGUAGE STYLE
{approach["language_style"]}

PREFERRED QUESTIONING STYLE
{preferred_questions}

QUESTIONING TO AVOID
{avoid_questions}

TUTOR EXPECTATIONS
{approach["tutor_expectations"]}

APPROACH GUIDANCE
{approach["prompt_guidance"]}

NON-NEGOTIABLE BEHAVIOURAL RULES

1. Never invent information to make the treatment approach fit.

2. Never contradict the authoritative case.

3. Never reveal the hidden treatment approach to the client.

4. Never force the client to respond in the style described by
   CLIENT STYLE if the authored case supports a different emotional
   presentation.

5. Never convert an unanswered question into a factual "no".

6. Never treat a therapist question as evidence that the client
   possesses the information being asked about.

7. Do not manufacture memories, trauma, causes or experiences.

8. Safety information must remain grounded in explicit client
   evidence or authoritative case data.

9. The approach changes HOW the consultation is conducted,
   not WHAT happened to the client.

10. Keep responses natural, concise and consistent with the
    established client persona.
""".strip()