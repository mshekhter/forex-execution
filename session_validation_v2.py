# =========================
# SESSION VALIDATION (v2)
# =========================

def validate_session_v2(session_value):
    status, data, text = request_json(
        "POST",
        f"{BASE_V2}/Session/validate",
        json_body={
            "UserName": USERNAME,
            "Session": session_value,
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=15,
    )

    if status != 200:
        raise RuntimeError(f"ValidateSession v2 failed: {status} {text}")

    if not isinstance(data, dict):
        return False

    return bool(data.get("IsAuthenticated", data.get("isAuthenticated", False)))


is_auth = validate_session_v2(session_value)
print("IsAuthenticated:", is_auth)
