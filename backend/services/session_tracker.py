sessions_db = []

def save_session(client, score):

    sessions_db.append({
        "client": client,
        "score": score,
    })

def get_sessions():
    return sessions_db