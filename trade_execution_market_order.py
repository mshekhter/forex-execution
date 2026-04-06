# =========================
# TRADE EXECUTION — MARKET ORDER (LIVE)
# =========================
# Places a live market trade with fixed 10-pip stop loss.
# Stop is anchored to actual entry price (spread-safe).
# Uses Lightstreamer audit_id and bid/ask for execution.
# Prints full request payload and raw response.

PIP = 0.0001
STOP_LOSS_PIPS = 10
MIN_QUANTITY = 1000

def place_market_trade_v1(
    *,
    session_trade,
    trading_account_id,
    market_id,
    market_name,
    direction,              # "buy" or "sell"
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

    if direction not in ("buy", "sell"):
        raise ValueError("direction must be 'buy' or 'sell'")

    # Entry-anchored stop (authoritative)
    if direction == "buy":
        entry_price = ask
        stop_price = entry_price - STOP_LOSS_PIPS * PIP
    else:
        entry_price = bid
        stop_price = entry_price + STOP_LOSS_PIPS * PIP

    payload = {
        "isTrade": True,
        "MarketId": market_id,
        "MarketName": market_name,
        "Direction": direction,
        "Quantity": quantity,
        "BidPrice": bid,
        "OfferPrice": ask,
        "AuditId": audit_id,
        "TradingAccountId": trading_account_id,
        "PositionMethodId": 1,
        "AutoRollover": False,
        "PriceTolerance": price_tolerance,
        "IfDone": [
            {
                "Stop": {
                    "TriggerPrice": round(stop_price, 5),
                    "Guaranteed": False,
                    "Applicability": "GTC",
                }
            }
        ],
    }

    print("\n===== TRADE REQUEST PAYLOAD =====")
    print(json.dumps(payload, indent=2))
    print("=================================\n")

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
        raise RuntimeError(f"Trade failed: {status}")

    return data
