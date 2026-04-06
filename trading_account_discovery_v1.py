# =========================
# TRADINGAPI v1 — ACCOUNT DISCOVERY 
# =========================

def get_trading_account_id_v1(session_trade):
    status, data, text = request_json(
        "GET",
        "https://ciapi.cityindex.com/TradingAPI/useraccount/ClientAndTradingAccount",
        params={
            "UserName": USERNAME,
            "Session": session_trade,
        },
        headers={
            "Accept": "application/json",
        },
        timeout=15,
    )

    if status != 200:
        raise RuntimeError(f"TradingAPI account lookup failed: {status} {text}")

    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected account payload: {data}")

    accounts = data.get("TradingAccounts")
    if not accounts or not isinstance(accounts, list):
        raise RuntimeError(f"No TradingAccounts found: {data}")

    if len(accounts) != 1:
        raise RuntimeError(f"Multiple TradingAccounts found (FIFO ambiguous): {accounts}")

    trading_account_id = accounts[0].get("TradingAccountId")
    if trading_account_id is None:
        raise RuntimeError(f"TradingAccountId missing: {accounts[0]}")

    return trading_account_id


trading_account_id = get_trading_account_id_v1(session_trade)
print("TradingAccountId (v1):", trading_account_id)
