# =========================
# SESSION LOGIN (v2)
# =========================


def logon_v2():
    status, data, text = request_json(
        "POST",
        f"{BASE_V2}/Session",
        json_body={
            "UserName": USERNAME,
            "Password": PASSWORD,
            "AppKey": APP_KEY,
            "AppVersion": "1",
            "AppComments": "",
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=15,
    )

    if status != 200:
        raise RuntimeError(f"LogOn v2 failed: {status} {text}")

    if not isinstance(data, dict) or "session" not in data:
        raise RuntimeError(f"LogOn v2 returned no session: {data}")

    return data["session"]

session_value = logon_v2()
print("Session:", session_value)
