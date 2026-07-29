import json
import os


DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data/case_histories.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    case_histories = json.load(f)


def get_persona_response(client_name, stage, state):

    trust = state["trust"]
    distress = state["distress"]
    resistance = state["resistance"]
    risk = state["risk_flag"]

    behaviour_explored = state.get(
        "behaviour_explored",
        False
    )

    persona = case_histories.get(client_name, {})

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

HEALTHCARE / SAFETY CASE STATUS

Medical history:
{case_value(medical_history)}

Psychological care:
{case_value(psychological_care)}

Psychiatric care:
{case_value(psychiatric_care)}

Current medication:
{case_value(medication_current)}

Healthcare professionals involved:
{case_value(professionals_involved)}

Referral/permission required:
{case_value(referral_required)}

Previous hypnosis experience:
{case_value(previous_hypnosis)}

Risk factors:
{case_value(risk_factors)}

Contraindications:
{case_value(contraindications)}

Safeguarding concerns:
{case_value(safeguarding_concerns)}

Why seeking help now:
{case_value(why_now)}

Readiness:
{case_value(readiness)}

IMPORTANT UNKNOWN-FIELD SIMULATION RULE

SAFETY / RISK QUESTION RULE

When Risk factors, Contraindications or Safeguarding concerns are
"NO SPECIFIC ITEM ESTABLISHED", this means the case author has not
provided a definite positive OR negative safety history.

If the student directly asks whether the client has experienced
self-harm thoughts, suicidal thoughts, thoughts of harming others,
specific safeguarding concerns, or a particular contraindication,
do NOT convert the empty case field into "No", "Never" or "I haven't".

Instead, remain in character while indicating that this specific
information has not yet been established by the supplied case.

Do not invent a positive risk disclosure either.

The student's question alone does not establish the answer.

Some clinical facts are intentionally undefined because the training
case has not specified them.

"UNKNOWN — NOT SPECIFIED BY CASE" means the case author has not
provided a definite value.

It MUST NOT be interpreted as:
- No
- None
- Never
- Not currently
- Not taking medication
- Not receiving treatment

When the student directly asks about an undefined healthcare,
treatment, medication, hypnosis-history, referral or clinical-history
field, do NOT invent either a positive or negative clinical fact.

The response must remain genuinely non-committal about the unknown
fact, but it should still sound like a real client participating in
the consultation.

IMPORTANT CONVERSATIONAL RULE

Do not repeatedly use generic phrases such as:
- "I'm not sure that's something I can give you a definite answer about."
- "That would need to be clarified as part of my history."

Instead, respond specifically to the subject the student asked about.

For an undefined field:
- acknowledge the particular topic naturally
- do not imply yes or no
- do not manufacture details
- vary wording from earlier responses in the conversation
- avoid repeating the same uncertainty phrase across different questions
- where appropriate, allow the response to give the therapist a natural
  opportunity to clarify or continue exploring the topic
- remain concise and in character

The response should reflect the actual subject being discussed.
Medication, previous hypnosis, healthcare involvement, medical history,
psychological care and other unknown fields should not all produce the
same generic response.

Do NOT answer "No", "Never", "None", "I haven't", or another definite
negative merely because the field is unknown.

Do NOT turn uncertainty itself into a clinical fact.

For sensitive risk, self-harm, safeguarding or contraindication
questions, remain especially neutral. Do not invent reassurance,
denial, disclosure or risk information merely to make the conversation
flow.

Preserving clinical uncertainty takes priority over conversational
convenience, but uncertainty should still be expressed naturally and
contextually.

NEVER EXPOSE INTERNAL CASE-STATE LANGUAGE

The client must never say phrases such as:
- "not established"
- "not specified"
- "in my case"
- "in my situation"
- "according to my background"
- "the information isn't available"
- "it hasn't been established yet"

These phrases describe the simulator's internal data state and are
not natural client speech.

When a clinical fact is undefined, translate the internal uncertainty
into natural first-person conversation without implying either a
positive or negative clinical fact.

Where appropriate, move the conversation forward by:
- acknowledging uncertainty naturally
- inviting the therapist to clarify the question
- allowing the topic to be explored in more detail
- responding specifically to the subject being asked about

Do not use one reusable uncertainty template across different domains.
Do not closely repeat an earlier unknown response from the same
consultation.

"NO SPECIFIC ITEM ESTABLISHED" means the case record does not currently
specify an item in that category. It does not prove that a complete
clinical assessment has ruled everything out.

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

    return response_style