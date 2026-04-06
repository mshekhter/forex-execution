def fetch_mid_price_v2(session_value, client_account_id, market_id):
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

    # Authoritative open/closed gate
    if prices.get("marketState") != 0:
        return None

    bid = prices.get("bidPrice")
    offer = prices.get("offerPrice")
    if bid is None or offer is None:
        return None

    mid = (float(bid) + float(offer)) / 2.0
    return mid
