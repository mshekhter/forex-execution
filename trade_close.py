# =========================
# TRADE CLOSE — EXISTING POSITION (LIVE)
# =========================
# Closes an existing open trade by OrderId.
# Uses Lightstreamer audit_id and current bid/ask.
# Prints full request payload and raw response.

def close_market_trade_v1(
    *,
    session_trade,
    trading_account_id,
    market_id,
    market_name,
    close_order_id,          # OrderId of the opening trade
    quantity=MIN_QUANTITY,
    price_tolerance=1,
):
    if latest_tick["bid"] is None or latest_tick["ask"] is None:
        raise RuntimeError("No Lightstreamer prices available")

    if latest_tick["audit_id"] is None:
        raise RuntimeError("No Lightstreamer audit_id available")

    bid = latest_tick["bid"]
    ask = latest_tick["ask"]
    audit_id = latest_tick["audit_id"]

    payload = {
        "isTrade": True,
        "MarketId": market_id,
        "MarketName": market_name,
        "Quantity": quantity,
        "BidPrice": bid,
        "OfferPrice": ask,
        "AuditId": audit_id,
        "TradingAccountId": trading_account_id,
        "PositionMethodId": 1,
        "AutoRollover": False,
        "PriceTolerance": price_tolerance,
        "Close": [int(close_order_id)],
    }

    print("\n===== CLOSE TRADE REQUEST PAYLOAD =====")
    print(json.dumps(payload, indent=2))
    print("======================================\n")

    status, data, text = request_json(
        "POST",
        "https://ciapi.cityindex.com/TradingAPI/order/newtradeorder",
        params={
            "UserName": USERNAME,
            "Session": session_trade,
        },
        json_body=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=15,
    )

    print("HTTP STATUS:", status)
    print("RAW RESPONSE JSON:", data)
    print("RAW RESPONSE TEXT:", text)

    if status != 200:
        raise RuntimeError(f"Close trade failed: {status}")

    return data
