# =========================
# SESSION RESILIENCE
# =========================

def ensure_session_v2(session_value):
    if not session_value:
        session_value = logon_v2()

    try:
        ok = validate_session_v2(session_value)
    except Exception:
        ok = False

    if ok:
        return session_value

    session_value = logon_v2()
    ok2 = validate_session_v2(session_value)
    if not ok2:
        raise RuntimeError("ValidateSession returned IsAuthenticated=false after re-logon")

    return session_value


# normalize session handle
session_value = ensure_session_v2(session_value)
print("Session ensured")
