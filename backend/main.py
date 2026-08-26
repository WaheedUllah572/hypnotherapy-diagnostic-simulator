from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

from services.unknown_response_engine import (
    build_unknown_response_guidance
)

load_dotenv()

from services.protected_domain_engine import (
    process_protected_question
)

from services.treatment_approach_engine import (
    get_treatment_prompt
)

from services.session_tracker import (
    save_session,
    get_sessions
)

from services.progress_engine import (
    calculate_progress
)

from services.conversation_engine import (
    get_stage,
    set_stage,
    detect_stage_from_question,
    update_state,
    get_state
)

from services.persona_engine import (
    get_persona_response,
    case_histories
)

from services.prompt_builder import (
    build_prompt
)

from services.dynamic_behaviour_controller import (
    get_dynamic_behaviour
)

from services.clinical_evidence_engine import (
    create_evidence_state,
    update_evidence,
    get_evidence_for_tutor
)

from services.risk_safety_engine import (
    evaluate_safety
)

from services.evidence_extractor import (
    extract_clinical_evidence
)


# ============================================================
# APP
# ============================================================

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ============================================================
# PHASE 2B CLINICAL EVIDENCE
# ============================================================

session_evidence = {}


def get_session_evidence(
    session_id,
    client_name
):

    if session_id not in session_evidence:

        session_evidence[session_id] = create_evidence_state(
            client_name=client_name
        )

    return session_evidence[session_id]


# ============================================================
# REQUEST MODELS
# ============================================================

class Message(BaseModel):

    text: str
    clientType: str
    history: list = []
    sessionId: str | None = None
    treatmentApproach: str = "cbh"


class TutorRequest(BaseModel):

    submission: dict
    chatHistory: list
    clientName: str


# ============================================================
# PROTECTED RESPONSE FALLBACKS
# ============================================================

def get_protected_fallback(
    domain: str,
    question: str
):

    """
    Safe fallback responses for undefined protected fields.

    These responses must remain topic-specific.

    IMPORTANT:
    Risk questions are handled according to the exact question
    rather than using "No self-harm history" as a universal
    negative answer.
    """

    question_lower = (question or "").lower()


    # --------------------------------------------------------
    # RISK — SELF-HARM / SUICIDAL IDEATION
    # --------------------------------------------------------

    if domain == "risk":

        if any(x in question_lower for x in [
            "thoughts of harming yourself",
            "thoughts of hurting yourself",
            "thoughts of self harm",
            "thoughts of self-harm",
            "suicidal thoughts",
            "thoughts about suicide",
            "thoughts of suicide",
        ]):

            return (
                "I'm not sure whether I've had thoughts like that. "
                "I'd need to think about it."
            )


        # ----------------------------------------------------
        # RISK — SUICIDE ATTEMPT
        # ----------------------------------------------------

        if any(x in question_lower for x in [
            "attempted suicide",
            "suicide attempt",
            "tried to kill yourself",
            "tried to end your life",
        ]):

            return (
                "I'm not certain whether I've ever attempted suicide. "
                "I'd need to think about that carefully."
            )


        # ----------------------------------------------------
        # RISK — HARM TO OTHERS
        # ----------------------------------------------------

        if any(x in question_lower for x in [
            "thoughts of harming someone",
            "thoughts of hurting someone",
            "harm anyone else",
            "hurt anyone else",
            "harm someone else",
            "hurt someone else",
        ]):

            return (
                "I'm not sure whether I've had thoughts like that "
                "about harming someone else."
            )


        # ----------------------------------------------------
        # RISK — SELF-HARM HISTORY
        #
        # This is the one situation where Claire's authored
        # "No self-harm history" fact may be used.
        # ----------------------------------------------------

        if any(x in question_lower for x in [
            "history of self harm",
            "history of self-harm",
            "history of harming yourself",
            "ever harmed yourself",
            "ever hurt yourself",
            "self harm before",
            "self-harm before",
        ]):

            return (
                "No, I don't have a history of self-harm. "
                "My main difficulty has been the anxiety around "
                "driving on motorways."
            )


        # ----------------------------------------------------
        # GENERAL RISK
        # ----------------------------------------------------

        return (
            "I'm not sure how to answer that properly. "
            "I'd need to think about it."
        )


    # --------------------------------------------------------
    # MEDICATION
    # --------------------------------------------------------

    if domain == "medication":

        return (
            "I'm not certain what medication I'm currently taking, "
            "if any. I'd need to check that."
        )


    # --------------------------------------------------------
    # PSYCHOLOGICAL CARE
    # --------------------------------------------------------

    if domain == "psychological_care":

        return (
            "I'm not sure whether I've had psychological treatment "
            "or support before. I'd need to think back."
        )


    # --------------------------------------------------------
    # PSYCHIATRIC CARE
    # --------------------------------------------------------

    if domain == "psychiatric_care":

        return (
            "I'm not sure whether I've ever seen a psychiatrist. "
            "I'd need to think back."
        )


    # --------------------------------------------------------
    # PREVIOUS HYPNOSIS
    # --------------------------------------------------------

    if domain == "previous_hypnosis":

        return (
            "I can't remember whether I've had hypnotherapy or "
            "hypnosis before."
        )


    # --------------------------------------------------------
    # MEDICAL HISTORY
    # --------------------------------------------------------

    if domain == "medical_history":

        return (
            "I'm not completely sure about my medical history. "
            "I'd need to think about it more."
        )


    # --------------------------------------------------------
    # HEALTHCARE PROFESSIONALS
    # --------------------------------------------------------

    if domain == "healthcare_professionals":

        return (
            "I'm not sure which healthcare professionals, if any, "
            "are currently involved in my care."
        )


    # --------------------------------------------------------
    # REFERRAL / PERMISSION
    # --------------------------------------------------------

    if domain == "referral_permission":

        return (
            "I'm not sure whether I need a referral or medical "
            "clearance for this."
        )


    # --------------------------------------------------------
    # CONTRAINDICATIONS
    # --------------------------------------------------------

    if domain == "contraindications":

        return (
            "I'm not sure whether there are any medical or "
            "psychological factors that could affect my suitability."
        )


    # --------------------------------------------------------
    # SAFEGUARDING
    # --------------------------------------------------------

    if domain == "safeguarding":

        return (
            "I'm not sure how to answer the question about my "
            "personal safety without thinking about it more."
        )


    # --------------------------------------------------------
    # GENERIC FALLBACK
    # --------------------------------------------------------

    return (
        "I'm not certain about that particular part of my history."
    )


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
async def chat(msg: Message):

    client_type = msg.clientType or "Daniel"

    session_id = (
        msg.sessionId
        or (client_type + "_session")
    )


    # ========================================================
    # STAGE
    # ========================================================

    detected = detect_stage_from_question(
        msg.text
    )

    if detected:

        set_stage(
            session_id,
            detected
        )

        stage = detected

    else:

        stage = get_stage(
            session_id
        )


    # ========================================================
    # STATE
    # ========================================================

    try:

        state = update_state(
            session_id,
            msg.text
        )

    except Exception:

        state = get_state(
            session_id
        )


    # ========================================================
    # AUTHORITATIVE CASE
    # ========================================================

    case_data = case_histories.get(
        client_type,
        {}
    )


    # ========================================================
    # BEHAVIOUR
    #
    # This is still calculated because the protected response
    # should retain appropriate client tone.
    #
    # BUT protected clinical questions do NOT go through the
    # normal difficult-persona response generation.
    # ========================================================

    behaviour = get_dynamic_behaviour(

        client_name=client_type,

        trust=state["trust"],

        distress=state["distress"],

        resistance=state["resistance"],

        risk=state["risk_flag"],

        treatment_approach=msg.treatmentApproach
    )


    # ========================================================
    # PROTECTED DOMAIN CHECK
    # ========================================================

    protected = process_protected_question(

        question=msg.text,

        persona=case_data
    )


    print(
        "\n========== PROTECTED QUESTION DEBUG =========="
    )

    print(
        "Client:",
        client_type
    )

    print(
        "Question:",
        msg.text
    )

    print(
        "Protected:",
        protected
    )

    print(
        "==============================================\n"
    )


    # ========================================================
    # RECENT CLIENT RESPONSES
    # ========================================================

    recent_client_messages = [

        m.get(
            "text",
            ""
        )

        for m in msg.history

        if m.get("role") == "client"
    ]


    # ========================================================
    # UNDEFINED PROTECTED FIELD
    #
    # THIS IS THE CRITICAL FIX.
    #
    # If the exact protected field is undefined, we completely
    # bypass the normal persona generation.
    # ========================================================

    unknown_guidance = build_unknown_response_guidance(

        student_text=msg.text,

        persona=case_data,

        behaviour=behaviour,

        recent_client_messages=recent_client_messages,
    )


    if unknown_guidance:

        domain = unknown_guidance.get(
            "domain"
        )


        print(
            "\n========== PROTECTED GENERATION MODE =========="
        )

        print(
            "Client:",
            client_type
        )

        print(
            "Domain:",
            domain
        )

        print(
            "Question:",
            msg.text
        )

        print(
            "===============================================\n"
        )


        # ====================================================
        # DEDICATED PROTECTED SYSTEM PROMPT
        # ====================================================

        protected_system_prompt = f"""
You are simulating the CLIENT in a professional hypnotherapy
training simulator.

The therapist/student has asked:

"{msg.text}"

This is an UNESTABLISHED clinical question.

==================================================
ABSOLUTE RULE
==================================================

ANSWER THE QUESTION DIRECTLY.

The therapist's question is clear.

NEVER ask the therapist to rephrase it.

NEVER respond with:

"Could you say that differently?"

"Could you explain what you mean?"

"I'm not sure what you mean."

"Can you clarify?"

"I don't understand."

Do not obstruct the student.

The purpose of the simulator is to challenge the student while
still allowing them to learn and progress.

==================================================
PROTECTED DOMAIN
==================================================

{domain}

The response MUST clearly relate to this exact domain.

Do not give a generic uncertainty sentence.

==================================================
EXACT QUESTION
==================================================

{msg.text}

Answer this exact question.

Do not answer a different but related question.

==================================================
RISK RULE
==================================================

If this is a risk question, distinguish the exact risk subtype.

For example:

"Do you have a history of self-harm?"

is different from:

"Have you ever had thoughts of harming yourself?"

which is different from:

"Have you ever attempted suicide?"

which is different from:

"Have you had thoughts of harming someone else?"

Information about one does NOT automatically answer another.

In particular:

"No self-harm history"

MUST NOT be used as an answer to:

"Have you ever had thoughts of harming yourself?"

because those are different clinical questions.

If the exact information is undefined:

PRESERVE UNCERTAINTY.

Do not invent a positive answer.

Do not invent a negative answer.

==================================================
NO HALLUCINATION
==================================================

The authoritative case below is the only source of client facts.

If a field is null or empty, the information is NOT established.

Do not invent:

- medication
- medication names
- prescriptions
- therapy
- counselling
- psychiatrists
- doctors
- healthcare professionals
- hypnosis experience
- referrals
- medical clearance
- safeguarding information
- suicidal thoughts
- self-harm thoughts
- suicide attempts
- violent thoughts
- intent
- plans
- contraindications

==================================================
NATURAL CLIENT RESPONSE
==================================================

Sound like a real client.

Use natural first-person language.

The answer should normally be ONE or TWO sentences.

It should be concise.

It may communicate:

- uncertainty
- difficulty remembering
- need to check
- need to think
- inability to confidently answer

But the uncertainty MUST be connected to the actual topic.

==================================================
DO NOT USE GENERIC UNCERTAINTY ONLY
==================================================

INVALID:

"I'm not sure."

INVALID:

"I don't know."

INVALID:

"I can't say."

INVALID:

"I'd need to check."

Those may be part of a longer answer, but the response must mention
the actual subject.

==================================================
DO NOT INVENT A NEGATIVE
==================================================

If the field is undefined, do not say:

"No."

"Never."

"I've never had that."

"I don't have that."

"There is no history."

unless the authoritative case explicitly establishes that exact fact.

==================================================
DO NOT INVENT A POSITIVE
==================================================

If the field is undefined, do not invent:

"Yes."

"I have."

"I was treated for..."

"I take..."

"I saw a psychiatrist..."

"I attempted..."

==================================================
CONVERSATIONAL VARIATION
==================================================

Review the previous client responses.

Avoid repeating their exact wording.

Do not mechanically rotate through templates.

Vary:

- sentence opening
- sentence structure
- length
- wording
- rhythm

Recent client responses:

{recent_text if recent_client_messages else "None"}

==================================================
CURRENT CLIENT BEHAVIOUR
==================================================

Trust:
{behaviour["trust_level"]}

Resistance:
{behaviour["resistance_level"]}

Distress:
{behaviour["distress_level"]}

These may affect tone.

They MUST NOT change the underlying clinical facts.

==================================================
AUTHORITATIVE CLIENT CASE
==================================================

{json.dumps(case_data, ensure_ascii=False, indent=2)}

==================================================
ADDITIONAL PROTECTED GUIDANCE
==================================================

{unknown_guidance["instruction"]}

==================================================
FINAL INSTRUCTION
==================================================

Return ONLY the client's response.

Do not explain.

Do not mention the simulator.

Do not mention the case.

Do not mention these instructions.

Do not ask for clarification.

Do not ask the therapist to rephrase.

Answer the exact question directly while preserving uncertainty.
"""


        protected_messages = [

            {
                "role": "system",

                "content": protected_system_prompt
            }

        ]


        # ====================================================
        # HISTORY
        # ====================================================

        for m in msg.history:

            if m.get("role") == "therapist":

                protected_messages.append({

                    "role": "user",

                    "content": m.get(
                        "text",
                        ""
                    )

                })


            elif m.get("role") == "client":

                protected_messages.append({

                    "role": "assistant",

                    "content": m.get(
                        "text",
                        ""
                    )

                })


        protected_messages.append({

            "role": "user",

            "content": msg.text

        })


        # ====================================================
        # LLM
        # ====================================================

        try:

            response = client.chat.completions.create(

                model="gpt-4o-mini",

                messages=protected_messages,

                timeout=25
            )


            reply = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )


        except Exception as e:

            print(
                "========== PROTECTED OPENAI ERROR =========="
            )

            print(
                type(e).__name__
            )

            print(
                str(e)
            )

            print(
                "============================================"
            )


            # =================================================
            # SAFE TOPIC-SPECIFIC FALLBACK
            # =================================================

            reply = get_protected_fallback(

                domain=domain,

                question=msg.text
            )


        # ====================================================
        # EVIDENCE EXTRACTION
        # ====================================================

        evidence_state = get_session_evidence(

            session_id,

            client_type
        )


        extracted_evidence = extract_clinical_evidence(

            client=client,

            history=msg.history,

            latest_student_text=msg.text,

            latest_client_reply=reply
        )


        print(
            "\n========== PROTECTED EVIDENCE DEBUG =========="
        )

        print(
            "SESSION:",
            session_id
        )

        print(
            "CLIENT:",
            client_type
        )

        print(
            "DOMAIN:",
            domain
        )

        print(
            "REPLY:",
            reply
        )

        print(
            "EXTRACTED:",
            extracted_evidence
        )

        print(
            "==============================================\n"
        )


        for item in extracted_evidence:

            update_evidence(

                evidence_state=evidence_state,

                domain=item["domain"],

                value=item["value"],

                status=item["status"],

                confidence=item["confidence"],

                evidence_text=item.get(
                    "evidence_text"
                ),

                clinical_significance=item.get(
                    "clinical_significance"
                ),

                applied_to_reasoning=item.get(
                    "applied_to_reasoning",
                    False
                ),

                flags=item.get(
                    "flags",
                    []
                )
            )


        # ====================================================
        # SAFETY
        # ====================================================

        safety_state = evaluate_safety(

            extracted_evidence
        )


        return {

            "reply": reply,

            "stage": stage,

            "state": state,

            "clinicalEvidence":
                get_evidence_for_tutor(
                    evidence_state
                ),

            "safetyState":
                safety_state
        }


    # ========================================================
    # NORMAL PERSONA GENERATION
    #
    # Only questions that are NOT undefined protected fields
    # reach this section.
    # ========================================================

    persona_style = get_persona_response(

        client_type,

        stage,

        state,

        msg.treatmentApproach,

        behaviour
    )


    system_prompt = build_prompt(

        stage,

        persona_style,

        msg.treatmentApproach,

        behaviour
    )


    system_prompt += "\n\n"


    system_prompt += get_treatment_prompt(

        msg.treatmentApproach
    )


    messages = [

        {

            "role": "system",

            "content": system_prompt

        }

    ]


    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "\n========== NORMAL PROMPT DEBUG =========="
    )

    print(
        "Client:",
        client_type
    )

    print(
        "Stage:",
        stage
    )

    print(
        "=========================================\n"
    )


    # ========================================================
    # COMPLETE AUTHORITATIVE CASE
    # ========================================================

    grounding = f"""
AUTHORITATIVE CLIENT CASE — COMPLETE SOURCE OF TRUTH

The following is the complete authored case for this client.

Every field in this case is authoritative.

If a field contains a definite value, preserve it.

If a field is null, empty, or an empty list, that means the case
does NOT establish that information.

IMPORTANT:

Do NOT convert missing or empty information into a definite
Yes or No.

Do NOT invent:

- hobbies
- relaxation activities
- coping strategies
- modality
- previous experiences
- treatment history
- medical history
- medication
- healthcare professionals
- referrals
- safeguarding information
- risk information
- traumatic experiences
- personality traits

In particular, if:

- coping_strategies is []
- modality is null
- communication_style is null
- disclosure_style is null

you MUST NOT invent information for those fields.

The student may ask about these areas.

Respond naturally as a real client, but preserve uncertainty
rather than creating new facts.

COMPLETE CASE:

{json.dumps(case_data, ensure_ascii=False, indent=2)}

The case above is authoritative.

Never introduce facts that are not supported by it.
"""


    messages.append({

        "role": "system",

        "content": grounding
    })


    # ========================================================
    # NORMAL CONVERSATION HISTORY
    # ========================================================

    for m in msg.history:

        if m.get("role") == "therapist":

            messages.append({

                "role": "user",

                "content": m.get(
                    "text",
                    ""
                )

            })


        elif m.get("role") == "client":

            messages.append({

                "role": "assistant",

                "content": m.get(
                    "text",
                    ""
                )

            })


    messages.append({

        "role": "user",

        "content": msg.text
    })


    # ========================================================
    # NORMAL LLM
    # ========================================================

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=messages,

            timeout=25
        )


        reply = (
            response
            .choices[0]
            .message
            .content
        )


    except Exception as e:

        print(
            "========== OPENAI ERROR =========="
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        print(
            "=================================="
        )


        reply = (
            "I'm not sure how to explain that… "
            "could you ask me in a different way?"
        )


    # ========================================================
    # PHASE 2B EVIDENCE EXTRACTION
    # ========================================================

    evidence_state = get_session_evidence(

        session_id,

        client_type
    )


    extracted_evidence = extract_clinical_evidence(

        client=client,

        history=msg.history,

        latest_student_text=msg.text,

        latest_client_reply=reply
    )


    print(
        "\n========== PHASE 2B EVIDENCE DEBUG =========="
    )

    print(
        "SESSION:",
        session_id
    )

    print(
        "CLIENT:",
        client_type
    )

    print(
        "EXTRACTED EVIDENCE:"
    )

    print(
        extracted_evidence
    )

    print(
        "==============================================\n"
    )


    for item in extracted_evidence:

        update_evidence(

            evidence_state=evidence_state,

            domain=item["domain"],

            value=item["value"],

            status=item["status"],

            confidence=item["confidence"],

            evidence_text=item.get(
                "evidence_text"
            ),

            clinical_significance=item.get(
                "clinical_significance"
            ),

            applied_to_reasoning=item.get(
                "applied_to_reasoning",
                False
            ),

            flags=item.get(
                "flags",
                []
            )
        )


    # ========================================================
    # PHASE 2B RISK & SAFETY
    # ========================================================

    safety_state = evaluate_safety(

        extracted_evidence
    )


    print(
        "\n========== PHASE 2B SAFETY DEBUG =========="
    )

    print(
        "SESSION:",
        session_id
    )

    print(
        "CLIENT:",
        client_type
    )

    print(
        "SAFETY STATE:"
    )

    print(
        safety_state
    )

    print(
        "============================================\n"
    )


    return {

        "reply": reply,

        "stage": stage,

        "state": state,

        "clinicalEvidence":
            get_evidence_for_tutor(
                evidence_state
            ),

        "safetyState":
            safety_state
    }


# ============================================================
# TUTOR EVALUATION
# ============================================================

def evaluate_q4(text):

    t = text.lower()


    safety = any(
        x in t
        for x in [
            "risk",
            "medical",
            "history",
            "screen",
            "contraindication",
            "safe",
            "safety",
            "no risk",
            "not at risk"
        ]
    )


    reassurance = any(
        x in t
        for x in [
            "reassure",
            "safe",
            "comfortable",
            "support",
            "supported",
            "ease",
            "okay",
            "you're safe"
        ]
    )


    readiness = any(
        x in t
        for x in [
            "ready",
            "ready to proceed",
            "comfortable to proceed",
            "proceed",
            "continue",
            "begin",
            "move forward",
            "we can start"
        ]
    )


    return {

        "safety": safety,

        "reassurance": reassurance,

        "readiness": readiness
    }


# ============================================================
# TUTOR REVIEW
# ============================================================

@app.post("/tutor-review")
async def tutor_review(req: TutorRequest):

    s = req.submission

    chat = req.chatHistory


    q1_text = s.get(
        "chosenApproach",
        ""
    ).lower()


    q2_text = s.get(
        "clientModality",
        ""
    ).lower()


    q3_text = s.get(
        "clientObjective",
        ""
    ).lower()


    q4_text = s.get(
        "clientReassurance",
        ""
    ).lower()


    # ========================================================
    # TREATMENT APPROACH
    # ========================================================

    if req.clientName == "Claire":

        q1 = any(
            x in q1_text
            for x in [
                "cbh",
                "cognitive",
                "cognitive behavioural",
                "cognitive behavioral"
            ]
        )


    elif req.clientName == "Daniel":

        q1 = any(
            x in q1_text
            for x in [
                "solution",
                "solution-focused",
                "solution focused"
            ]
        )


    elif req.clientName == "Sophie":

        q1 = any(
            x in q1_text
            for x in [
                "ericksonian",
                "indirect"
            ]
        )


    elif req.clientName == "Mark":

        q1 = (
            "regression"
            in q1_text
        )


    else:

        q1 = False


    # ========================================================
    # MODALITY
    # ========================================================

    asked_behaviour = any(

        any(
            x in m["text"].lower()
            for x in [
                "relax",
                "hobbies",
                "fun",
                "downtime",
                "what do you enjoy",
                "what do you like to do",
                "how do you switch off",
                "what helps you relax"
            ]
        )

        for m in chat

        if m["role"] == "therapist"
    )


    q2 = (

        asked_behaviour

        and any(
            x in q2_text
            for x in [
                "visual",
                "auditory",
                "kinaesthetic"
            ]
        )
    )


    # ========================================================
    # OBJECTIVE
    # ========================================================

    q3 = any(

        x in q3_text

        for x in [
            "goal",
            "reduce",
            "manage",
            "control",
            "confidence",
            "calm",
            "sleep",
            "relax"
        ]
    )


    # ========================================================
    # STRESS DETECTION
    # ========================================================

    stress_present = any(

        any(
            x in m["text"].lower()
            for x in [
                "i used to",
                "used to enjoy",
                "don't do that anymore",
                "haven't done that in a long time",
                "don't really make time",
                "don't make time anymore",
                "not doing it anymore",
                "used to but"
            ]
        )

        for m in chat

        if m["role"] == "client"
    )


    handled_stress = (

        any(
            x in q4_text
            for x in [
                "used to",
                "not doing",
                "stopped",
                "no longer",
                "activities",
                "hobbies",
                "pleasurable",
                "enjoyable"
            ]
        )

        and

        any(
            x in q4_text
            for x in [
                "stress",
                "overwhelm",
                "sign",
                "affect",
                "impact",
                "difficult"
            ]
        )

        and

        any(
            x in q4_text
            for x in [
                "will",
                "again",
                "you'll",
                "you will",
                "begin",
                "return",
                "able",
                "start"
            ]
        )
    )


    stress_score = (

        True

        if (
            not stress_present
            or handled_stress
        )

        else False
    )


    # ========================================================
    # SAFETY / REASSURANCE
    # ========================================================

    q4_data = evaluate_q4(
        q4_text
    )


    q4 = (

        all(
            q4_data.values()
        )

        and stress_score
    )


    # ========================================================
    # FEEDBACK
    # ========================================================

    stress_feedback = ""


    if stress_present:

        if handled_stress:

            stress_feedback = (
                "✔ You correctly identified the reduction in "
                "pleasurable activity as a stress indicator."
            )

        else:

            stress_feedback = (
                "✘ You missed the client's "
                "‘I used to…’ stress indicator."
            )


    feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Appropriate model selected." if q1 else "✘ Approach unclear."}

QUESTION 2 — Client Modality
{"✔ Correct (behaviour explored)." if q2 else "✘ Modality must be based on behavioural questioning."}

QUESTION 3 — Client Objective
{"✔ Objective clear." if q3 else "✘ Objective unclear."}

QUESTION 4 — Safety & Reassurance
{"✔ Appropriate." if q4 else "✘ Needs improvement."}

STRESS INDICATOR
{stress_feedback}
"""


    total = sum([
        q1,
        q2,
        q3,
        q4
    ])


    save_session(
        req.clientName,
        total
    )


    return {

        "feedback":
            feedback.strip(),

        "score": {

            "total":
                total
        },

        "detected_modality":
            "Kinaesthetic"
    }


# ============================================================
# PROGRESS
# ============================================================

@app.get("/progress")
def progress():

    sessions = get_sessions()


    if not sessions:

        return {

            "sessionsCompleted":
                0,

            "averageScore":
                0,

            "personasCompleted":
                []
        }


    total_sessions = len(
        sessions
    )


    avg_score = (
        sum(
            s["score"]
            for s in sessions
        )
        / total_sessions
    )


    personas = list(
        set(
            s["client"]
            for s in sessions
        )
    )


    return {

        "sessionsCompleted":
            total_sessions,

        "averageScore":
            round(
                avg_score,
                2
            ),

        "personasCompleted":
            personas
    }