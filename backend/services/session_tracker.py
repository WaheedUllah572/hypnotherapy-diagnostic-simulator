# backend/services/session_tracker.py

sessions_db = []

def save_session(client, score):
    # Prevent duplicate session saves for same client and same score
    for session in sessions_db:
        if session["client"] == client and session["score"] == score:
            return  # Session already saved, do not add again

    sessions_db.append({
        "client": client,
        "score": score,
    })

def get_sessions():
    return sessions_db