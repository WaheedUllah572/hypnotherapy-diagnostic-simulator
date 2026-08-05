sessions_db = []

def save_session(
    client,
    score,
    state,
    stage,
    treatment_approach
):
    sessions_db.append({

    "client": client,

    "score": score,

    "trust": state["trust"],

    "distress": state["distress"],

    "engagement": state["engagement"],

    "resistance": state["resistance"],

    "risk": state["risk_flag"],

    "stage": stage,

    "treatment_approach": treatment_approach
})

def get_sessions():
    return sessions_db