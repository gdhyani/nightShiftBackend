from datetime import datetime, timezone


def get_session_info() -> dict:
    now = datetime.now(timezone.utc)
    hour = now.hour
    if 0 <= hour < 7:
        session = "asia"
        killzone = 0 <= hour < 4
    elif 7 <= hour < 15:
        session = "london"
        killzone = 7 <= hour < 10
    elif 15 <= hour < 21:
        session = "new_york"
        killzone = 13 <= hour < 16
    else:
        session = "off_hours"
        killzone = False
    sessions_order = ["asia", "london", "new_york"]
    try:
        idx = sessions_order.index(session)
        next_session = sessions_order[(idx + 1) % 3]
    except ValueError:
        next_session = "asia"
    return {
        "current_session": session, "killzone_active": killzone,
        "utc_hour": hour, "utc_time": now.isoformat(), "next_session": next_session,
    }
