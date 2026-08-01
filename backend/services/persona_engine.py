from services.treatment_approach_engine import get_treatment_approach
import json
import os


DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data/case_histories.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    case_histories = json.load(f)


def get_persona_response(
    client_name,
    stage,
    state,
    treatment_approach="cbh"
):

    trust = state["trust"]
    distress = state["distress"]
    resistance = state["resistance"]
    risk = state["risk_flag"]

    behaviour_explored = state.get(
        "behaviour_explored",
        False
    )

    persona = case_histories.get(client_name, {})

    approach = get_treatment_approach(
    treatment_approach
)

    # ============================
    # AUTHORITATIVE CASE DATA
    # ============================

    # Phase 2B nested case structure
    identity = persona.get("identity", {})
    presentation = persona.get("presentation", {})
    clinical_features = persona.get("clinical_features", {})
    simulation = persona.get("simulation", {})

    healthcare = persona.get("healthcare", {})
    hypnosis_history = persona.get("hypnosis_history", {})
    safety = persona.get("safety", {})
    motivation = persona.get("motivation", {})

    medication = healthcare.get("medication", {})

    condition = identity.get("condition")

    presenting_problem = presentation.get("presenting_problem")
    timeline = presentation.get("timeline")
    thoughts = presentation.get("thoughts")
    feelings = presentation.get("feelings")
    body = presentation.get("physical")
    past = presentation.get("past")
    goal = presentation.get("goal")

    symptoms = clinical_features.get("symptoms", [])

    hypnosis_question = simulation.get("hypnosis_question")
    medical_history = healthcare.get("medical_history")
    psychological_care = healthcare.get("psychological_care")
    psychiatric_care = healthcare.get("psychiatric_care")
    medication_current = medication.get("current")
    professionals_involved = healthcare.get("professionals_involved", [])
    referral_required = healthcare.get("referral_or_permission_required")

    previous_hypnosis = hypnosis_history.get("previous_experience")

    risk_factors = safety.get("risk_factors", [])
    contraindications = safety.get("contraindications", [])
    safeguarding_concerns = safety.get("safeguarding_concerns", [])

    why_now = motivation.get("why_now")
    readiness = motivation.get("readiness")

        # ============================
    # CASE VALUE FORMATTER
    # ============================

    def case_value(value):
        if value is None:
            return "UNKNOWN — NOT SPECIFIED BY CASE"

        if value == []:
            return "NO SPECIFIC ITEM ESTABLISHED"

        return value

    tone = "neutral"

    if trust > 70:
        tone = "open"

    elif resistance > 60:
        tone = "resistant"

    elif distress > 60:
        tone = "distressed"

    response_style = f"""
CLIENT STATE

Trust: {trust}
Distress: {distress}
Resistance: {resistance}
Tone: {tone}

AUTHORITATIVE CLIENT CASE

Client:
{client_name}

Condition:
{condition}

Presenting problem:
{presenting_problem}

Timeline:
{timeline}

Thoughts:
{thoughts}

Feelings:
{feelings}

Physical/body experience:
{body}

Relevant past:
{past}

Goal:
{goal}

Symptoms:
{", ".join(symptoms)}

Hypnosis question/concern:
{hypnosis_question}

HEALTHCARE SUMMARY

Medical history:
{case_value(medical_history)}

Psychological care:
{case_value(psychological_care)}

Psychiatric care:
{case_value(psychiatric_care)}

Medication:
{case_value(medication_current)}

Previous hypnosis:
{case_value(previous_hypnosis)}

CASE GROUNDING RULES

The information above is the authoritative case record.

You may express these facts naturally and conversationally,
but you must preserve their meaning.

Do NOT contradict the case record.

Do NOT invent new:
- diagnoses
- medication
- medical history
- psychological treatment
- psychiatric treatment
- healthcare professionals
- previous hypnosis experience
- traumatic events
- safeguarding history
- risk history
- referrals
- treatment history

If the student asks about clinical information that is not
established in the case record, do not create a definite fact.

Respond naturally with uncertainty or limited knowledge where
appropriate rather than inventing clinical history.

Do not replace an established timeline, symptom, thought,
feeling, past experience or goal with a different one.

====================================
FACT PRESERVATION
====================================

The AUTHORITATIVE CLIENT CASE is the single source of truth.

If the case contains a definite fact, you MUST preserve it exactly.

Do NOT weaken, strengthen, shorten or approximate established facts.

Examples:

If the case says:

"It has been gradually building over the past couple of years."

You MUST NOT say:

- "a few months"
- "recently"
- "for a while"
- "over time"

If the case states a specific thought, symptom, feeling or goal,
preserve its meaning faithfully.

Natural wording is encouraged, but the underlying fact must remain
identical.

When unsure, prefer repeating the authored fact rather than
creating a new variation.
"""

    # ============================
    # EMOTIONAL BEHAVIOUR
    # ============================

    response_style += """
CLIENT BEHAVIOUR

- Remain realistic and conversational.
- If trust is high, open up somewhat more naturally.
- If resistance is high, responses may become shorter or hesitant.
- If distress is high, emotional difficulty may become more apparent.
- Do not exaggerate the emotional state.
"""

    # ============================
    # MODALITY / BEHAVIOUR
    # ============================

    if not behaviour_explored:

        response_style += """
MODALITY DISCLOSURE

Do not volunteer hobbies, relaxation methods, downtime
activities or behavioural coping strategies before the
student meaningfully explores them.

Do not reveal modality merely by deliberately inserting
visual, auditory or kinaesthetic vocabulary.
"""

    else:

        response_style += """
MODALITY DISCLOSURE

The student has begun exploring behaviour.

You may discuss hobbies, relaxation behaviour, downtime
activities or coping habits when relevant.

Any modality evidence should emerge naturally through
behaviour rather than being explicitly labelled.
"""

        response_style += """
STRESS INDICATOR

Where genuinely relevant to discussion of enjoyable or
restorative activities, the client may describe reduced
engagement in something previously enjoyed.

Do not force this into unrelated responses.
"""

    # ============================
    # RISK STATE
    # ============================

    if risk != "none":

        response_style += """
CURRENT STATE NOTE

The session state contains a risk/overwhelm indicator.
Respond consistently with the established conversation.

Do not invent suicidal intent, self-harm, diagnosis or other
serious risk information that has not actually been
established.
"""
    response_style += f"""

============================
CLIENT COMMUNICATION STYLE
============================

Current treatment approach:

{approach["name"]}

Speak naturally in a way that reflects this treatment approach.

The clinical facts MUST remain identical.

Do NOT change:

- presenting problem
- symptoms
- history
- timeline
- goals
- safety information

Only change:

- communication style
- emotional emphasis
- conversational focus
- natural wording

Conversation focus:

{approach["conversation_focus"]}

Client communication style:

{approach["client_style"]}

Language style:

{approach["language_style"]}

Natural behavioural guidance:

{approach["prompt_guidance"]}

Never mention the treatment approach by name.
"""

    return response_style