# =========================
# CLIENT ACCOUNT ID
# =========================

def get_client_account_id_v2(session_value):
    print("Resolving client account id...")

    status, data, text = request_json(
        "GET",
        "https://ciapi.cityindex.com/v2/userAccount/ClientAndTradingAccount",
        params={
            "UserName": USERNAME,
            "Session": session_value,
        },
        headers={"Accept": "application/json"},
        timeout=15,
    )

    print("Account lookup HTTP status:", status)

    if _is_auth_error(status, data, text):
        print("Auth error during account lookup")
        raise PermissionError("AUTH")

    if status != 200:
        raise RuntimeError(f"Account lookup failed: {status} {text}")

    if not isinstance(data, dict) or "tradingAccounts" not in data or not data["tradingAccounts"]:
        raise RuntimeError(f"Account lookup returned unexpected payload: {data}")

    client_account_id = data["tradingAccounts"][0]["clientAccountId"]
    print("ClientAccountId resolved:", client_account_id)

    return client_account_id


client_account_id = get_client_account_id_v2(session_value)
