# =========================
# SESSION LOGIN (TradingAPI v1)
# =========================

def logon_trade():
    status, data, text = request_json(
        "POST",
        f"{API_BASE_URL}/session",
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
        raise RuntimeError(f"Trade LogOn failed: {status} {text}")

    if not isinstance(data, dict) or "Session" not in data:
        raise RuntimeError(f"Trade LogOn returned no Session: {data}")

    return data["Session"]


session_trade = logon_trade()
print("TradingAPI session:", session_trade)
