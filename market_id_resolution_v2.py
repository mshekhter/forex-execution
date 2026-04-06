# =========================
# MARKET ID RESOLUTION
# =========================

def get_market_id_v2(session_value, client_account_id, market_name):
    print(f"Resolving market id for '{market_name}'...")

    status, data, text = request_json(
        "GET",
        "https://ciapi.cityindex.com/TradingAPI/market/search",
        params={
            "searchByMarketName": "TRUE",
            "query": market_name,
            "maxResults": 10,
            "includeOptions": "False",
            "ClientAccountId": client_account_id,
            "UserName": USERNAME,
            "Session": session_value,
        },
        headers={"Accept": "application/json"},
        timeout=15,
    )

    print("Market search HTTP status:", status)

    if _is_auth_error(status, data, text):
        print("Auth error during market search")
        raise PermissionError("AUTH")

    if status != 200:
        raise RuntimeError(f"Market search failed: {status} {text}")

    if not isinstance(data, dict):
        raise RuntimeError(f"Market search returned unexpected payload: {data}")

    markets = data.get("Markets")
    if not markets:
        raise RuntimeError(f"No markets returned for '{market_name}': {data}")

    market_id = markets[0]["MarketId"]
    print("MarketId resolved:", market_id)

    return market_id


market_id = get_market_id_v2(session_value, client_account_id, MARKET_NAME)
