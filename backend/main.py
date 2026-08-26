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
# SESSION EVIDENCE
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
# CHAT
# ============================================================

@app.post("/chat")
async def chat(msg: Message):

    # ========================================================
    # CLIENT / SESSION
    # ========================================================

    client_type = (
        msg.clientType
        or "Daniel"
    )


    session_id = (
        msg.sessionId
        or f"{client_type}_session"
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
    # CONVERSATION STATE
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
    # DYNAMIC BEHAVIOUR
    #
    # Still calculated for normal conversation.
    #
    # Protected questions are deliberately handled before
    # behaviour can make the client refuse/rephrase.
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
    # PROTECTED CLINICAL QUESTION
    # ========================================================

    protected = process_protected_question(

        question=msg.text,

        persona=case_data
    )


    print(
        "\n========== PROTECTED QUESTION CHECK =========="
    )

    print(
        "CLIENT:",
        client_type
    )

    print(
        "QUESTION:",
        msg.text
    )

    print(
        "DOMAIN:",
        protected.get("domain")
    )

    print(
        "HANDLED:",
        protected.get("handled")
    )

    print(
        "==============================================\n"
    )


    # ========================================================
    # CRITICAL:
    #
    # IF PROTECTED QUESTION IS HANDLED,
    # RETURN IMMEDIATELY.
    #
    # DO NOT CALL:
    #
    # - get_persona_response()
    # - build_prompt()
    # - OpenAI normal chat
    # - difficult persona behaviour
    #
    # This prevents:
    #
    # "Could you rephrase that?"
    #
    # from overriding safety/clinical questions.
    # ========================================================

    if protected.get("handled"):

        reply = protected.get(
            "response"
        )


        print(
            "\n========== PROTECTED RESPONSE =========="
        )

        print(
            "CLIENT:",
            client_type
        )

        print(
            "DOMAIN:",
            protected.get("domain")
        )

        print(
            "REPLY:",
            reply
        )

        print(
            "========================================\n"
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # We do not send the protected question through the
        # normal evidence-generation path here.
        #
        # The authoritative status remains unestablished unless
        # the authored case explicitly establishes the exact
        # requested fact.
        # ----------------------------------------------------

        return {

            "reply": reply,

            "stage": stage,

            "state": state,

            "clinicalEvidence": [],

            "safetyState": {

                "level":
                    "unestablished",

                "requires_attention":
                    False,

                "requires_referral_review":
                    False,

                "requires_safeguarding_review":
                    False,

                "evidence":
                    [],

                "flags":
                    [],

                "established_domains":
                    []
            }
        }


    # ========================================================
    # NORMAL PERSONA GENERATION
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

            "role":
                "system",

            "content":
                system_prompt
        }

    ]


    # ========================================================
    # RECENT CLIENT RESPONSES
    # ========================================================

    recent_client_messages = [

        m.get(
            "text",
            ""
        )

        for m in msg.history

        if m.get(
            "role"
        ) == "client"
    ]


    # ========================================================
    # UNDEFINED CLINICAL GUIDANCE
    #
    # This is still available for non-protected fields that
    # require natural uncertainty.
    #
    # Protected fields never reach this section because they
    # already returned above.
    # ========================================================

    unknown_guidance = build_unknown_response_guidance(

        student_text=msg.text,

        persona=case_data,

        behaviour=behaviour,

        recent_client_messages=recent_client_messages
    )


    if unknown_guidance:

        system_prompt += (
            "\n\n"
            + unknown_guidance["instruction"]
        )


        messages[0]["content"] = (
            system_prompt
        )


    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "\n========== NORMAL PROMPT DEBUG =========="
    )

    print(
        "CLIENT:",
        client_type
    )

    print(
        "STAGE:",
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

{json.dumps(
    case_data,
    ensure_ascii=False,
    indent=2
)}

The case above is authoritative.

Never introduce facts that are not supported by it.
"""


    messages.append({

        "role":
            "system",

        "content":
            grounding
    })


    # ========================================================
    # HISTORY
    # ========================================================

    for m in msg.history:

        if m.get(
            "role"
        ) == "therapist":

            messages.append({

                "role":
                    "user",

                "content":
                    m.get(
                        "text",
                        ""
                    )
            })


        elif m.get(
            "role"
        ) == "client":

            messages.append({

                "role":
                    "assistant",

                "content":
                    m.get(
                        "text",
                        ""
                    )
            })


    # ========================================================
    # CURRENT STUDENT QUESTION
    # ========================================================

    messages.append({

        "role":
            "user",

        "content":
            msg.text
    })


    # ========================================================
    # OPENAI
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
    # PHASE 2B — EVIDENCE EXTRACTION
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


    # ========================================================
    # UPDATE EVIDENCE
    # ========================================================

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
    # RISK & SAFETY
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


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "reply":
            reply,

        "stage":
            stage,

        "state":
            state,

        "clinicalEvidence":
            get_evidence_for_tutor(
                evidence_state
            ),

        "safetyState":
            safety_state
    }


# ============================================================
# TUTOR Q4
# ============================================================

def evaluate_q4(
    text
):

    t = (
        text or ""
    ).lower()


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

        "safety":
            safety,

        "reassurance":
            reassurance,

        "readiness":
            readiness
    }


# ============================================================
# TUTOR REVIEW
# ============================================================

@app.post("/tutor-review")
async def tutor_review(
    req: TutorRequest
):

    s = req.submission

    chat = req.chatHistory


    q1_text = (
        s.get(
            "chosenApproach",
            ""
        )
        .lower()
    )


    q2_text = (
        s.get(
            "clientModality",
            ""
        )
        .lower()
    )


    q3_text = (
        s.get(
            "clientObjective",
            ""
        )
        .lower()
    )


    q4_text = (
        s.get(
            "clientReassurance",
            ""
        )
        .lower()
    )


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
    # STRESS
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
    # SAFETY
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