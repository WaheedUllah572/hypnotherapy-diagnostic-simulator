from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

import os
import json

from dotenv import load_dotenv

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
# ENVIRONMENT
# ============================================================

load_dotenv()


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

    history: list = Field(
        default_factory=list
    )

    sessionId: str | None = None

    treatmentApproach: str = "cbh"


class TutorRequest(BaseModel):

    submission: dict

    chatHistory: list

    clientName: str


# ============================================================
# BEHAVIOURAL QUESTION DETECTION
# ============================================================

def detect_behavioural_question(
    question: str
) -> bool:
    """
    Detect clear questions about:

    - relaxation
    - hobbies
    - enjoyment
    - free time
    - downtime
    - spare time
    - activities outside work
    - switching off

    These are clear questions even when the authored case contains
    no answer.

    The client should answer the topic rather than pretending not
    to understand the question.
    """

    text = (
        question or ""
    ).lower().strip()

    behavioural_patterns = [

        # ----------------------------------------------------
        # RELAXATION
        # ----------------------------------------------------

        "what do you do to relax",
        "what do you usually do to relax",
        "what helps you relax",
        "how do you relax",
        "how do you unwind",
        "what helps you unwind",
        "what do you do to unwind",

        # ----------------------------------------------------
        # HOBBIES / ENJOYMENT
        # ----------------------------------------------------

        "what are your hobbies",
        "what do you enjoy",
        "what do you enjoy doing",
        "what do you like to do",
        "what do you do for fun",
        "what do you do for enjoyment",
        "what activities do you enjoy",

        # ----------------------------------------------------
        # FREE TIME
        # ----------------------------------------------------

        "what do you do in your free time",
        "what do you usually do in your free time",
        "how do you spend your free time",
        "what do you do outside work",
        "what do you usually do outside work",
        "what do you do when you're not working",
        "what do you usually do when you're not working",

        # ----------------------------------------------------
        # DOWNTIME
        # ----------------------------------------------------

        "what do you do during your downtime",
        "how do you spend your downtime",
        "what do you do in your downtime",

        # ----------------------------------------------------
        # SPARE TIME
        # ----------------------------------------------------

        "what do you do in your spare time",
        "what do you usually do in your spare time",

        # ----------------------------------------------------
        # SWITCHING OFF
        # ----------------------------------------------------

        "how do you switch off",
        "what helps you switch off",
        "what do you do to switch off",
    ]

    return any(
        pattern in text
        for pattern in behavioural_patterns
    )


# ============================================================
# CHECK BEHAVIOURAL INFORMATION IN CASE
# ============================================================

def has_behavioural_information(
    case_data: dict
) -> bool:
    """
    Determine whether the authored case actually contains
    behavioural information relevant to the student's question.

    Empty values are treated as undefined.

    This function deliberately checks several possible locations
    because different case structures may store behavioural data
    in different sections.
    """

    possible_fields = [

        "coping_strategies",

        "relaxation_activities",

        "relaxation_activity",

        "hobbies",

        "hobby",

        "enjoyable_activities",

        "enjoyable_activity",

        "leisure_activities",

        "leisure_activity",

        "free_time_activities",

        "free_time_activity",

        "downtime_activities",

        "downtime_activity",

    ]

    # --------------------------------------------------------
    # ROOT LEVEL
    # --------------------------------------------------------

    for field in possible_fields:

        value = case_data.get(
            field
        )

        if value not in (
            None,
            "",
            [],
            {}
        ):

            return True

    # --------------------------------------------------------
    # COMMON NESTED SECTIONS
    # --------------------------------------------------------

    sections = [

        "behaviour",
        "behavior",
        "behavioural",
        "behavioral",
        "lifestyle",
        "presentation",
        "clinical_features",
        "motivation",
        "simulation",
    ]

    for section_name in sections:

        section = case_data.get(
            section_name
        )

        if not isinstance(
            section,
            dict
        ):

            continue

        for field in possible_fields:

            value = section.get(
                field
            )

            if value not in (
                None,
                "",
                [],
                {}
            ):

                return True

    return False


# ============================================================
# UNDEFINED BEHAVIOURAL RESPONSE
# ============================================================

def get_undefined_behaviour_response(
    question: str,
    recent_client_messages=None
) -> str:
    """
    Deterministic response when the student asks a clear
    behavioural question but the authored case contains no
    corresponding behavioural information.

    IMPORTANT:

    This function:

    - understands the question
    - does not ask for rephrasing
    - does not invent a hobby
    - does not invent a coping strategy
    - does not invent a relaxation activity
    - varies wording
    """

    recent_client_messages = (
        recent_client_messages or []
    )

    previous_text = " ".join(
        str(message).lower()
        for message in recent_client_messages[-8:]
        if message
    )

    responses = [

        "I haven't really thought about what I do to relax lately.",

        "These days, I can't really think of anything specific that I do just to relax.",

        "I haven't been doing much specifically for relaxation recently.",

        "It's difficult to think of anything particular that I do in my free time lately.",

        "I don't really have a specific activity that I use to unwind these days.",

        "Lately, I haven't really focused on doing things just for enjoyment.",

        "I suppose I haven't really been making much time for relaxation lately.",

        "I can't think of anything specific that I regularly do when I'm not working.",

        "There isn't really anything specific that comes to mind when I think about relaxing.",

        "Recently, most of my attention has been taken up by managing the anxiety, rather than doing things for myself.",
    ]

    # --------------------------------------------------------
    # Prefer wording not recently used
    # --------------------------------------------------------

    for response in responses:

        if response.lower() not in previous_text:

            return response

    # --------------------------------------------------------
    # Final fallback
    # --------------------------------------------------------

    return (
        "I haven't really been doing much for relaxation lately."
    )


# ============================================================
# STANDARD EMPTY SAFETY STATE
# ============================================================

def get_unestablished_safety_state():

    return {

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


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
async def chat(
    msg: Message
):

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
    # PROTECTED QUESTION HANDLED
    #
    # NEVER SEND THESE QUESTIONS THROUGH THE LLM.
    #
    # This prevents:
    #
    # "Could you rephrase that?"
    #
    # from replacing a deterministic clinical answer.
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

        return {

            "reply":
                reply,

            "stage":
                stage,

            "state":
                state,

            "clinicalEvidence":
                [],

            "safetyState":
                get_unestablished_safety_state()
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

    # ========================================================
    # BEHAVIOURAL QUESTION GUIDANCE
    # ========================================================

    if detect_behavioural_question(msg.text):

        system_prompt += """

BEHAVIOURAL QUESTION GUIDANCE

The therapist has asked a clear question about relaxation,
hobbies, enjoyment, free time, downtime, spare time,
switching off, or activities outside work.

Understand the question directly.

DO NOT ask the therapist to rephrase the question.

If the authoritative client case contains a relevant
behavioural fact, use that fact naturally.

If the authoritative client case does NOT contain a relevant
behavioural fact, DO NOT invent one.

Instead, respond naturally as the client would when they do
not have a specific established answer.

The response must be generated naturally by the client persona.
It must NOT sound like a predefined response or template.

RESPONSE STYLE:

- Answer the therapist's question directly.
- Sound spontaneous and conversational.
- Vary the wording naturally between questions.
- Do not repeat a fixed sentence.
- Do not invent hobbies.
- Do not invent relaxation activities.
- Do not invent coping strategies.
- Do not invent interests or leisure activities.
- Do not turn missing information into a definite Yes or No.
- Preserve uncertainty when the case does not establish the answer.
- Never say "Could you rephrase that?" merely because the case
  does not contain the requested information.
- Never pretend not to understand a clear behavioural question.
- Do not mention the case, simulation, prompts, or system instructions.

The question is understandable. The only uncertainty is whether
the client has an established answer to it.
"""

    system_prompt += """

BEHAVIOURAL QUESTION GUIDANCE

The therapist has asked a clear question about relaxation,
hobbies, enjoyment, free time, downtime, spare time,
switching off, or activities outside work.

Understand the question directly.

DO NOT ask the therapist to rephrase the question.

If the authoritative client case contains a relevant
behavioural fact, use that fact naturally.

If the authoritative client case does NOT contain a relevant
behavioural fact, DO NOT invent one.

Instead, respond naturally as the client would when they do
not have a specific established answer.

The response must be generated naturally by the client persona.
It must NOT sound like a predefined response or template.

RESPONSE STYLE:

- Answer the therapist's question directly.
- Sound spontaneous and conversational.
- Vary the wording naturally between questions.
- Do not repeat a fixed sentence.
- Do not invent hobbies.
- Do not invent relaxation activities.
- Do not invent coping strategies.
- Do not invent interests or leisure activities.
- Do not turn missing information into a definite Yes or No.
- Preserve uncertainty when the case does not establish the answer.
- Never say "Could you rephrase that?" merely because the case
  does not contain the requested information.
- Never pretend not to understand a clear behavioural question.
- Do not mention the case, simulation, prompts, or system instructions.

The question is understandable. The only uncertainty is whether
the client has an established answer to it.
"""

    # ========================================================
    # SYSTEM MESSAGE
    # ========================================================

    messages = [

        {

            "role":
                "system",

            "content":
                system_prompt
        }

    ]

    # ========================================================
    # AUTHORITATIVE CASE GROUNDING
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
    # CONVERSATION HISTORY
    # ========================================================

    for m in msg.history:

        role = m.get(
            "role"
        )

        text = m.get(
            "text",
            ""
        )

        if role == "therapist":

            messages.append({

                "role":
                    "user",

                "content":
                    text
            })

        elif role == "client":

            messages.append({

                "role":
                    "assistant",

                "content":
                    text
            })

    # ========================================================
    # CURRENT QUESTION
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

        if not reply:

            reply = (
                "I'm not sure how to answer that."
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
            "I'm not sure how to answer that properly right now."
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

            x in m.get(
                "text",
                ""
            ).lower()

            for x in [

                "relax",
                "hobbies",
                "fun",
                "downtime",
                "what do you enjoy",
                "what do you like to do",
                "how do you switch off",
                "what helps you relax",
                "what do you do in your free time",
                "what do you do when you're not working"
            ]
        )

        for m in chat

        if m.get(
            "role"
        ) == "therapist"
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

            x in m.get(
                "text",
                ""
            ).lower()

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

        if m.get(
            "role"
        ) == "client"
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