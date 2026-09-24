from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


# ============================================================
# SESSION TRACKER
# ============================================================
#
# Lightweight in-memory session tracking for the current
# simulator.
#
# IMPORTANT:
#
# This is NOT a persistent database.
#
# Data will be lost when the backend process restarts.
#
# The existing public API is preserved:
#
#     save_session(client, score)
#     get_sessions()
#
# Additional metadata can be supplied when available without
# breaking existing callers.
# ============================================================


# ============================================================
# IN-MEMORY SESSION STORE
# ============================================================

sessions_db: List[Dict[str, Any]] = []


# ============================================================
# TIMESTAMP
# ============================================================

def _utc_timestamp() -> str:
    """
    Return a timezone-aware UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# SAVE SESSION
# ============================================================

def save_session(
    client: str,
    score: Any,
    session_id: Optional[str] = None,
    condition: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Save a completed session summary.

    Existing callers can continue using:

        save_session(client, score)

    Optional metadata:

        save_session(
            client,
            score,
            session_id="...",
            condition="..."
        )

    Returns the saved session record.
    """

    record = {
        "session_id": (
            session_id
            or str(uuid4())
        ),

        "client": client,

        "condition": condition,

        "score": score,

        "created_at": _utc_timestamp(),
    }

    sessions_db.append(
        record
    )

    return deepcopy(
        record
    )


# ============================================================
# GET SESSIONS
# ============================================================

def get_sessions() -> List[Dict[str, Any]]:
    """
    Return a copy of all stored sessions.

    Returning a copy prevents callers from accidentally modifying
    the internal session store directly.
    """

    return deepcopy(
        sessions_db
    )


# ============================================================
# GET ONE SESSION
# ============================================================

def get_session(
    session_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Return one session by ID.

    Returns None when no matching session exists.
    """

    for session in sessions_db:

        if session.get(
            "session_id"
        ) == session_id:

            return deepcopy(
                session
            )

    return None


# ============================================================
# CLEAR SESSIONS
# ============================================================

def clear_sessions() -> None:
    """
    Clear the in-memory session store.

    Useful for local development/testing.

    This does not affect any persistent database because this
    tracker does not use one.
    """

    sessions_db.clear()