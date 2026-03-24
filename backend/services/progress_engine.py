# backend/services/progress_engine.py

def calculate_progress(sessions):

    total_sessions = len(sessions)

    if total_sessions == 0:
        return {
            "sessionsCompleted": 0,
            "averageScore": 0,
            "personasCompleted": []
        }

    total_score = sum([s["score"] for s in sessions])
    average_score = round(total_score / total_sessions, 2)

    personas = list(set([s["client"] for s in sessions]))

    return {
        "sessionsCompleted": total_sessions,
        "averageScore": average_score,
        "personasCompleted": personas
    }