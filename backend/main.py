from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

import os
import json
from typing import Any, Dict, List, Optional

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

app = FastAPI(
    title="Level 2 Clinical Hypnotherapy Simulator",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
) if OPENAI_API_KEY else None


# ============================================================
# SESSION EVIDENCE
# ============================================================

session_evidence: Dict[str, Dict[str, Any]] = {}


def get_session_key(
    session_id: str,
    client_name: str
) -> str:
    """
    Prevent evidence from different clients accidentally sharing
    the same session state.
    """

    return f"{session_id}:{client_name}"


def get_session_evidence(
    session_id: str,
    client_name: str
):
    key = get_session_key(
        session_id,
        client_name
    )

    if key not in session_evidence:

        session_evidence[key] = create_evidence_state(
            client_name=client_name
        )

    return session_evidence[key]


# ============================================================
# REQUEST MODELS
# ============================================================

class Message(BaseModel):

    text: str

    clientType: str

    history: list = Field(
        default_factory=list
    )

    sessionId: Optional[str] = None

    treatmentApproach: Optional[str] = None


class TutorRequest(BaseModel):

    submission: dict

    chatHistory: list

    clientName: str


# ============================================================
# CASE HELPERS
# ============================================================

def get_client_case(
    client_name: str
) -> Dict[str, Any]:

    case = case_histories.get(
        client_name
    )

    if isinstance(case, dict):
        return case

    return {}


def normalise_approach(
    value: Any
) -> Optional[str]:

    if value is None:
        return None

    text = str(value).strip().lower()

    if not text:
        return None

    aliases = {

        "cbh":
            "cbh",

        "cognitive behavioural":
            "cbh",

        "cognitive behavioral":
            "cbh",

        "cognitive behavioural hypnotherapy":
            "cbh",

        "cognitive behavioral hypnotherapy":
            "cbh",

        "solution-focused":
            "solution_focused",

        "solution focused":
            "solution_focused",

        "solution-focused hypnotherapy":
            "solution_focused",

        "solution focused hypnotherapy":
            "solution_focused",

        "sh":
            "solution_focused",

        "regression":
            "regression",

        "regression hypnotherapy":
            "regression",

        "ericksonian":
            "ericksonian",

        "ericksonian hypnotherapy":
            "ericksonian",

        "indirect":
            "ericksonian",
    }

    return aliases.get(
        text,
        text
    )


def get_authoritative_treatment_approach(
    client_name: str,
    requested_approach: Optional[str],
    case_data: Dict[str, Any]
) -> str:
    """
    Determine the treatment approach used by the simulation.

    Priority:

    1. Explicit authored case assignment.
    2. Explicit frontend assignment if the case does not contain
       an assignment.

    This prevents the frontend/default value from silently
    overriding an authoritative case assignment.
    """

    identity = case_data.get(
        "identity",
        {}
    )

    treatment_reasoning = case_data.get(
        "treatment_reasoning",
        {}
    )

    authored_values = [

        identity.get(
            "therapeutic_profile"
        ),

        treatment_reasoning.get(
            "preferred_approach"
        ),
    ]

    for value in authored_values:

        approach = normalise_approach(
            value
        )

        if approach:
            return approach

    requested = normalise_approach(
        requested_approach
    )

    if requested:
        return requested

    # No treatment assignment exists in the case.
    # Keep the system deterministic without silently selecting
    # CBH as a clinical conclusion.
    return "cbh"


# ============================================================
# BEHAVIOURAL QUESTION DETECTION
# ============================================================

def detect_behavioural_question(
    question: str
) -> bool:

    text = (
        question or ""
    ).lower().strip()

    behavioural_patterns = [

        "what do you do to relax",
        "what do you usually do to relax",
        "what helps you relax",
        "how do you relax",
        "how do you unwind",
        "what helps you unwind",
        "what do you do to unwind",

        "what are your hobbies",
        "what do you enjoy",
        "what do you enjoy doing",
        "what do you like to do",
        "what do you do for fun",
        "what do you do for enjoyment",
        "what activities do you enjoy",

        "what do you do in your free time",
        "what do you usually do in your free time",
        "how do you spend your free time",

        "what do you do outside work",
        "what do you usually do outside work",
        "what do you do when you're not working",
        "what do you usually do when you're not working",

        "what do you do during your downtime",
        "how do you spend your downtime",
        "what do you do in your downtime",

        "what do you do in your spare time",
        "what do you usually do in your spare time",

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
    case_data: Dict[str, Any]
) -> bool:

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

    def meaningful(value: Any) -> bool:

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(
            value,
            (list, tuple, set, dict)
        ):
            return len(value) > 0

        return True

    for field in possible_fields:

        if meaningful(
            case_data.get(field)
        ):
            return True

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

            if meaningful(
                section.get(field)
            ):
                return True

    return False


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
# EVIDENCE MERGING
# ============================================================

def _evidence_identity(
    item: Dict[str, Any]
):
    return (
        item.get("domain"),
        str(
            item.get("value")
        ).strip().lower(),
        str(
            item.get("evidence_text")
        ).strip().lower()
    )


def merge_evidence_for_safety(
    evidence_state
) -> List[Dict[str, Any]]:
    """
    Convert the accumulated tutor evidence into a list suitable
    for safety evaluation.

    The complete session evidence is used rather than only the
    latest extracted message.
    """

    evidence = []

    if not isinstance(
        evidence_state,
        dict
    ):
        return evidence

    domains = evidence_state.get(
        "domains",
        {}
    )

    if isinstance(
        domains,
        dict
    ):

        for domain, item in domains.items():

            if not isinstance(
                item,
                dict
            ):
                continue

            if not item.get(
                "value"
            ):
                continue

            evidence.append({

                "domain":
                    domain,

                "value":
                    item.get("value"),

                "status":
                    item.get(
                        "status",
                        "mentioned"
                    ),

                "confidence":
                    item.get(
                        "confidence",
                        0
                    ),

                "evidence_text":
                    item.get(
                        "evidence_text"
                    ),

                "clinical_significance":
                    item.get(
                        "clinical_significance"
                    ),

                "applied_to_reasoning":
                    item.get(
                        "applied_to_reasoning",
                        False
                    ),

                "flags":
                    item.get(
                        "flags",
                        []
                    )
            })

    return evidence


# ============================================================
# PROTECTED QUESTION HANDLER
# ============================================================

def build_protected_response(
    protected: Dict[str, Any]
):
    return {

        "reply":
            protected.get(
                "response",
                "I'm not sure how to answer that."
            ),

        "domain":
            protected.get(
                "domain"
            )
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
    # AUTHORITATIVE CASE
    # ========================================================

    case_data = get_client_case(
        client_type
    )

    # ========================================================
    # AUTHORITATIVE TREATMENT APPROACH
    # ========================================================

    treatment_approach = (
        get_authoritative_treatment_approach(
            client_name=client_type,
            requested_approach=msg.treatmentApproach,
            case_data=case_data
        )
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

    except Exception as exc:

        print(
            "Conversation state update error:",
            exc
        )

        state = get_state(
            session_id
        )

    # ========================================================
    # DYNAMIC BEHAVIOUR
    # ========================================================

    behaviour = get_dynamic_behaviour(

        client_name=client_type,

        trust=state.get(
            "trust",
            50
        ),

        distress=state.get(
            "distress",
            30
        ),

        resistance=state.get(
            "resistance",
            20
        ),

        risk=state.get(
            "risk_flag",
            "none"
        ),

        treatment_approach=treatment_approach
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

    if protected.get("handled"):

        protected_response = build_protected_response(
            protected
        )

        return {

            "reply":
                protected_response["reply"],

            "stage":
                stage,

            "state":
                state,

            "clinicalEvidence":
                get_evidence_for_tutor(
                    get_session_evidence(
                        session_id,
                        client_type
                    )
                ),

            "safetyState":
                get_unestablished_safety_state(),

            "treatmentApproach":
                treatment_approach
        }

    # ========================================================
    # PERSONA
    # ========================================================

    persona_style = get_persona_response(

        client_type,

        stage,

        state,

        treatment_approach,

        behaviour
    )

    # ========================================================
    # PROMPT
    # ========================================================

    system_prompt = build_prompt(

        stage,

        persona_style,

        treatment_approach,

        behaviour
    )

    system_prompt += "\n\n"

    system_prompt += get_treatment_prompt(
        treatment_approach
    )

    # ========================================================
    # BEHAVIOURAL QUESTION GUIDANCE
    #
    # Added ONCE only.
    # ========================================================

    if detect_behavioural_question(
        msg.text
    ):

        behavioural_information_exists = (
            has_behavioural_information(
                case_data
            )
        )

        system_prompt += f"""

BEHAVIOURAL QUESTION STATE

The therapist has asked a clear behavioural question.

Examples include questions about:

- relaxation
- hobbies
- enjoyment
- free time
- downtime
- spare time
- switching off
- activities outside work

The question itself is understandable.

Relevant authored behavioural information exists:
{str(behavioural_information_exists).lower()}

If relevant information exists:
- answer using that information
- do not invent additional activities

If relevant information does not exist:
- understand the question
- answer naturally as a client who does not have a specific
  established answer
- preserve uncertainty
- do not invent a hobby, coping strategy, relaxation activity,
  interest, or leisure activity
- do not ask the therapist to rephrase the question
- do not pretend not to understand

Keep the answer natural and appropriately concise.

The fact that the information is undefined does NOT mean the
client has explicitly said "no".

Do not manufacture a definite yes/no answer.
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

The following is the complete authored case for {client_type}.

Every populated field is authoritative.

If a field contains a definite value:
- preserve it
- answer consistently with it
- do not replace it with a different fact

If a field is null or an empty list:
- the case does not establish that information
- do not turn the absence of information into a definite yes/no
- do not invent a clinical history

Do not invent:

- hobbies
- relaxation activities
- coping strategies
- modality
- previous hypnosis experiences
- treatment history
- medical history
- medication
- healthcare professionals
- referrals
- safeguarding information
- risk information
- traumatic experiences
- new personality traits

IMPORTANT:

The treatment approach controls communication style only.

It does NOT change the authoritative clinical facts.

The client's personality controls communication style only.

Conversation state controls openness and emotional expression only.

COMPLETE CASE:

{json.dumps(
    case_data,
    ensure_ascii=False,
    indent=2
)}

AUTHORITATIVE TREATMENT APPROACH:

{treatment_approach}

Never introduce unsupported facts.
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

    for item in msg.history:

        if not isinstance(
            item,
            dict
        ):
            continue

        role = item.get(
            "role"
        )

        text = str(
            item.get(
                "text",
                ""
            )
        ).strip()

        if not text:
            continue

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

    if client is None:

        return {

            "reply":
                "The OpenAI API key is not configured.",

            "stage":
                stage,

            "state":
                state,

            "clinicalEvidence":
                [],

            "safetyState":
                get_unestablished_safety_state(),

            "treatmentApproach":
                treatment_approach
        }

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=messages,

            temperature=0.7,

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

    except Exception as exc:

        print(
            "========== OPENAI ERROR =========="
        )

        print(
            type(exc).__name__
        )

        print(
            str(exc)
        )

        print(
            "=================================="
        )

        reply = (
            "I'm not sure how to answer that properly right now."
        )

    # ========================================================
    # PHASE 2B — ACCUMULATED EVIDENCE
    # ========================================================

    evidence_state = get_session_evidence(

        session_id,

        client_type
    )

    try:

        extracted_evidence = extract_clinical_evidence(

            client=client,

            history=msg.history,

            latest_student_text=msg.text,

            latest_client_reply=reply
        )

    except Exception as exc:

        print(
            "Evidence extraction error:",
            exc
        )

        extracted_evidence = []

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
        "TREATMENT APPROACH:",
        treatment_approach
    )

    print(
        "EXTRACTED EVIDENCE:",
        extracted_evidence
    )

    print(
        "==============================================\n"
    )

    # ========================================================
    # UPDATE ACCUMULATED EVIDENCE
    # ========================================================

    for item in extracted_evidence:

        if not isinstance(
            item,
            dict
        ):
            continue

        domain = item.get(
            "domain"
        )

        if not domain:
            continue

        try:

            update_evidence(

                evidence_state=evidence_state,

                domain=domain,

                value=item.get(
                    "value"
                ),

                status=item.get(
                    "status",
                    "mentioned"
                ),

                confidence=item.get(
                    "confidence",
                    0
                ),

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

        except Exception as exc:

            print(
                f"Evidence update error for {domain}:",
                exc
            )

    # ========================================================
    # SAFETY — USE ACCUMULATED SESSION EVIDENCE
    # ========================================================

    accumulated_evidence = (
        merge_evidence_for_safety(
            evidence_state
        )
    )

    try:

        safety_state = evaluate_safety(
            accumulated_evidence
        )

    except Exception as exc:

        print(
            "Safety evaluation error:",
            exc
        )

        safety_state = (
            get_unestablished_safety_state()
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
        "SAFETY STATE:",
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
            safety_state,

        "treatmentApproach":
            treatment_approach
    }


# ============================================================
# TUTOR HELPERS
# ============================================================

def _normalise_text(
    value: Any
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip().lower()


def _contains_any(
    text: str,
    terms: List[str]
) -> bool:

    return any(
        term in text
        for term in terms
    )


def get_expected_approach_for_client(
    client_name: str
) -> Optional[str]:

    case_data = get_client_case(
        client_name
    )

    return get_authoritative_treatment_approach(
        client_name=client_name,
        requested_approach=None,
        case_data=case_data
    )


def detect_modality_from_text(
    text: str
) -> Optional[str]:

    t = _normalise_text(
        text
    )

    visual_terms = [
        "see",
        "seeing",
        "picture",
        "image",
        "visual",
        "look",
        "looks",
        "colour",
        "color",
        "scene",
        "picture in my mind",
    ]

    auditory_terms = [
        "hear",
        "hearing",
        "sound",
        "sounds",
        "voice",
        "voices",
        "noise",
        "auditory",
        "listen",
    ]

    kinaesthetic_terms = [
        "feel",
        "feeling",
        "felt",
        "sensation",
        "body",
        "chest",
        "hands",
        "heart",
        "tight",
        "heavy",
        "restless",
        "physical",
        "kinaesthetic",
        "kinesthetic",
    ]

    scores = {

        "Visual":
            sum(
                1
                for term in visual_terms
                if term in t
            ),

        "Auditory":
            sum(
                1
                for term in auditory_terms
                if term in t
            ),

        "Kinaesthetic":
            sum(
                1
                for term in kinaesthetic_terms
                if term in t
            )
    }

    best = max(
        scores,
        key=scores.get
    )

    if scores[best] == 0:
        return None

    # Do not manufacture a modality from a weak tie.
    highest = scores[best]

    tied = [
        modality
        for modality, score in scores.items()
        if score == highest
    ]

    if len(tied) > 1:
        return None

    return best


def evaluate_q4(
    text: str
) -> Dict[str, bool]:

    t = _normalise_text(
        text
    )

    safety = _contains_any(
        t,
        [
            "risk",
            "medical",
            "history",
            "screen",
            "contraindication",
            "safe",
            "safety",
            "health",
            "medication",
            "self-harm",
            "self harm",
            "safeguarding",
            "referral",
        ]
    )

    reassurance = _contains_any(
        t,
        [
            "reassure",
            "safe",
            "comfortable",
            "support",
            "supported",
            "ease",
            "okay",
            "you're safe",
            "you are safe",
        ]
    )

    readiness = _contains_any(
        t,
        [
            "ready",
            "ready to proceed",
            "comfortable to proceed",
            "proceed",
            "continue",
            "begin",
            "move forward",
            "we can start",
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

    submission = (
        req.submission
        if isinstance(
            req.submission,
            dict
        )
        else {}
    )

    chat = (
        req.chatHistory
        if isinstance(
            req.chatHistory,
            list
        )
        else []
    )

    # ========================================================
    # SUBMISSION TEXT
    # ========================================================

    q1_text = _normalise_text(
        submission.get(
            "chosenApproach",
            ""
        )
    )

    q2_text = _normalise_text(
        submission.get(
            "clientModality",
            ""
        )
    )

    q3_text = _normalise_text(
        submission.get(
            "clientObjective",
            ""
        )
    )

    q4_text = _normalise_text(
        submission.get(
            "clientReassurance",
            ""
        )
    )

    # ========================================================
    # AUTHORITATIVE APPROACH
    # ========================================================

    expected_approach = (
        get_expected_approach_for_client(
            req.clientName
        )
    )

    selected_approach = normalise_approach(
        q1_text
    )

    q1 = (
        expected_approach is not None
        and selected_approach == expected_approach
    )

    # ========================================================
    # CHAT TEXT
    # ========================================================

    therapist_messages = [

        str(
            item.get(
                "text",
                ""
            )
        )

        for item in chat

        if isinstance(
            item,
            dict
        )
        and item.get(
            "role"
        ) == "therapist"
    ]

    client_messages = [

        str(
            item.get(
                "text",
                ""
            )
        )

        for item in chat

        if isinstance(
            item,
            dict
        )
        and item.get(
            "role"
        ) == "client"
    ]

    therapist_text = " ".join(
        therapist_messages
    )

    client_text = " ".join(
        client_messages
    )

    # ========================================================
    # MODALITY
    # ========================================================

    asked_behaviour = detect_behavioural_question(
        therapist_text
    )

    detected_modalities = []

    for message in client_messages:

        modality = detect_modality_from_text(
            message
        )

        if modality:
            detected_modalities.append(
                modality
            )

    submitted_modality = None

    modality_text = _normalise_text(
        q2_text
    )

    if "visual" in modality_text:
        submitted_modality = "Visual"

    elif "auditory" in modality_text:
        submitted_modality = "Auditory"

    elif (
        "kinaesthetic" in modality_text
        or "kinesthetic" in modality_text
    ):
        submitted_modality = "Kinaesthetic"

    actual_modality = None

    if detected_modalities:

        counts = {}

        for modality in detected_modalities:

            counts[modality] = (
                counts.get(
                    modality,
                    0
                )
                + 1
            )

        highest = max(
            counts.values()
        )

        winners = [
            modality
            for modality, count in counts.items()
            if count == highest
        ]

        if len(winners) == 1:
            actual_modality = winners[0]

    # A behavioural question alone does not establish a modality.
    q2 = (
        asked_behaviour
        and submitted_modality is not None
        and actual_modality is not None
        and submitted_modality == actual_modality
    )

    # ========================================================
    # OBJECTIVE
    # ========================================================

    q3 = _contains_any(
        q3_text,
        [
            "goal",
            "reduce",
            "manage",
            "control",
            "confidence",
            "calm",
            "sleep",
            "relax",
            "feel safe",
            "feel calmer",
            "switch off",
        ]
    )

    # ========================================================
    # SAFETY / REASSURANCE / READINESS
    # ========================================================

    q4_data = evaluate_q4(
        q4_text
    )

    q4 = all(
        q4_data.values()
    )

    # ========================================================
    # STRESS INDICATOR
    # ========================================================

    stress_present = _contains_any(
        client_text.lower(),
        [
            "i used to",
            "used to enjoy",
            "don't do that anymore",
            "haven't done that in a long time",
            "don't really make time",
            "don't make time anymore",
            "not doing it anymore",
            "used to but",
        ]
    )

    handled_stress = (

        _contains_any(
            q4_text,
            [
                "used to",
                "not doing",
                "stopped",
                "no longer",
                "activities",
                "hobbies",
                "pleasurable",
                "enjoyable",
            ]
        )

        and

        _contains_any(
            q4_text,
            [
                "stress",
                "overwhelm",
                "sign",
                "affect",
                "impact",
                "difficult",
            ]
        )
    )

    stress_score = (
        not stress_present
        or handled_stress
    )

    # ========================================================
    # FEEDBACK
    # ========================================================

    expected_name = (
        expected_approach
        or "not established"
    )

    feedback = f"""
QUESTION 1 — Treatment Approach
{"✔ Appropriate model selected." if q1 else f"✘ The selected approach does not match the authored client assignment. Expected: {expected_name}."}

QUESTION 2 — Client Modality
{"✔ Modality selection is supported by the conversation." if q2 else "✘ The selected modality is not sufficiently supported by the conversation."}

QUESTION 3 — Client Objective
{"✔ Objective is clear." if q3 else "✘ Objective needs clearer connection to the client's stated goal."}

QUESTION 4 — Safety & Reassurance
{"✔ Safety, reassurance and readiness were addressed." if q4 else "✘ Safety, reassurance and/or readiness needs further attention."}
"""

    if stress_present:

        if handled_stress:

            feedback += (
                "\nSTRESS INDICATOR\n"
                "✔ The client's change in pleasurable/activity behaviour was addressed."
            )

        else:

            feedback += (
                "\nSTRESS INDICATOR\n"
                "✘ The client's change in pleasurable/activity behaviour was not clearly addressed."
            )

    # ========================================================
    # SCORE
    # ========================================================

    total = sum([
        bool(q1),
        bool(q2),
        bool(q3),
        bool(q4)
    ])

    save_session(
        req.clientName,
        total
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "feedback":
            feedback.strip(),

        "score": {

            "total":
                total
        },

        "detected_modality":
            actual_modality,

        "expectedTreatmentApproach":
            expected_approach,

        "treatmentApproachCorrect":
            q1,

        "modalitySupported":
            q2,

        "objectiveClear":
            q3,

        "safetyReassuranceReadiness":
            q4,

        "stressIndicatorPresent":
            stress_present,

        "stressIndicatorHandled":
            handled_stress
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

    valid_scores = [

        s.get(
            "score",
            0
        )

        for s in sessions

        if isinstance(
            s,
            dict
        )
    ]

    avg_score = (

        sum(valid_scores)
        / len(valid_scores)

        if valid_scores

        else 0
    )

    personas = list(
        dict.fromkeys(

            s.get(
                "client"
            )

            for s in sessions

            if isinstance(
                s,
                dict
            )
            and s.get(
                "client"
            )
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