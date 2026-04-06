# =========================
# EXECUTION PRICE SNAPSHOT (BID / ASK)
# =========================
# Purpose:
# - Intrabar polling for execution
# - Entry execution price
# - Exit execution price
# - Stop loss evaluation
# - Shadow or live mode compatible
#
# Source:
# - GetMarketInformation v2
# - Same endpoint as mid-price fetch
# - Read-only, no side effects

def fetch_exec_prices_v2(session_value, client_account_id, market_id):
    url = f"https://ciapi.cityindex.com/v2/market/{market_id}/information"

    status, data, text = request_json(
        "GET",
        url,
        params={
            "clientAccountId": client_account_id,
            "UserName": USERNAME,
            "Session": session_value,
        },
        headers={"Accept": "application/json"},
        timeout=15,
    )

    if _is_auth_error(status, data, text):
        raise PermissionError("AUTH")

    if status != 200:
        raise RuntimeError(f"Market information failed: {status} {text}")

    if not isinstance(data, dict):
        raise RuntimeError(f"Market information returned unexpected payload: {data}")

    market_info = data.get("marketInformation", {})
    prices = market_info.get("prices", {})

    market_state = prices.get("marketState")
    if market_state != 0:
        return None

    bid = prices.get("bidPrice")
    ask = prices.get("offerPrice")

    if bid is None or ask is None:
        return None

    return {
        "bid_exec": float(bid),
        "ask_exec": float(ask),
        "ts_utc": utcnow(),
    }
