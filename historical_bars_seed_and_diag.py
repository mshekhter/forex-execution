# =========================
# HISTORICAL PRICE BARS SEED (1m, MID) + DIAGNOSTICS
# =========================
# Goal:
# - Seed a 1-minute candle buffer for the live loop.
# - Walk backward if needed.
# - PRINT CONTENTS BEFORE HANDOFF TO CELL 14.

       
def _parse_wcf_date(s):
    if not isinstance(s, str):
        return None
    try:
        ms = int(s.replace("/Date(", "").replace(")/", ""))
        return (
            datetime
            .utcfromtimestamp(ms / 1000.0)
            .replace(second=0, microsecond=0, tzinfo=timezone.utc)
        )
    except Exception:
        return None

def fetch_price_bars_between(
    session_value,
    client_account_id,
    market_id,
    from_ts_utc,
    to_ts_utc,
    interval="MINUTE",
    span=1,
    price_type="MID",
    max_results=1000,
):
    status, data, text = request_json(
        "GET",
        f"https://ciapi.cityindex.com/TradingAPI/market/{market_id}/barhistorybetween",
        params={
            "interval": interval,
            "span": span,
            "fromTimestampUTC": int(from_ts_utc),
            "toTimestampUTC": int(to_ts_utc),
            "priceType": price_type,
            "maxResults": max_results,
            "UserName": USERNAME,
            "Session": session_value,
            "ClientAccountId": client_account_id,
        },
        headers={"Accept": "application/json"},
        timeout=30,
    )

    if _is_auth_error(status, data, text):
        raise PermissionError("AUTH")

    if status != 200:
        raise RuntimeError(f"Historical bar fetch failed: {status} {text}")

    bars = (data or {}).get("PriceBars", []) if isinstance(data, dict) else []
    if not bars:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    rows = []
    for b in bars:
        ts = _parse_wcf_date(b.get("BarDate"))
        if ts is None:
            continue
        rows.append(
            {
                "timestamp": ts,
                "open": float(b["Open"]),
                "high": float(b["High"]),
                "low": float(b["Low"]),
                "close": float(b["Close"]),
                "volume": 0,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    return df.sort_values("timestamp").reset_index(drop=True)


def seed_recent_open_bars(
    *,
    session_value,
    client_account_id,
    market_id,
    desired_minutes,
    interval="MINUTE",
    span=1,
    price_type="MID",
    max_results=1000,
    initial_lookback_minutes=12 * 60,
    search_step_minutes=6 * 60,
    max_search_back_minutes=7 * 24 * 60,
):
    now_ts = int(datetime.utcnow().timestamp())
    shift_back = 0

    while True:
        to_ts = now_ts - (shift_back * 60)
        from_ts = to_ts - (initial_lookback_minutes * 60)

        df = fetch_price_bars_between(
            session_value=session_value,
            client_account_id=client_account_id,
            market_id=market_id,
            from_ts_utc=from_ts,
            to_ts_utc=to_ts,
            interval=interval,
            span=span,
            price_type=price_type,
            max_results=max_results,
        )

        if not df.empty:
            if len(df) > desired_minutes:
                df = df.tail(desired_minutes).reset_index(drop=True)
            return df

        shift_back += search_step_minutes
        if shift_back > max_search_back_minutes:
            raise RuntimeError("Seed failed: no bars found in search window.")


# =========================
# SEED RANGE + LOAD
# =========================

LOOKBACK_MINUTES = 24 * 60
desired = max(CANDLE_WINDOW, LOOKBACK_MINUTES)

hist_df = seed_recent_open_bars(
    session_value=session_value,
    client_account_id=client_account_id,
    market_id=market_id,
    desired_minutes=desired,
    interval="MINUTE",
    span=1,
    price_type="MID",
    max_results=1000,
    initial_lookback_minutes=LOOKBACK_MINUTES,
    search_step_minutes=6 * 60,
    max_search_back_minutes=7 * 24 * 60,
)

candles = hist_df.tail(CANDLE_WINDOW).copy().reset_index(drop=True)
candles_1m = candles.copy()

# =========================
# DIRECTION OBSERVATION (INITIALIZE FROM HISTORY)
# =========================
# Purpose:
# - Initialize live direction from last two completed 1m candles
# - Direction is sign only (+1 / -1)
# - Observational

direction_live = None

if len(candles_1m) >= 2:
    c1 = candles_1m.iloc[-2]["close"]
    c2 = candles_1m.iloc[-1]["close"]
    if c2 > c1:
        direction_live = 1
    elif c2 < c1:
        direction_live = -1

#print("Initial direction_live:", direction_live)

# =========================
# DIRECTION UPDATE (1m, LIVE)
# =========================
# Purpose:
# - Continuously update realized direction from 1-minute candles
# - Direction is sign only (+1 / -1)
# - Observational, non-predictive
# - No latching here

def update_direction_live(candles_1m, prev_direction):
    if candles_1m is None or len(candles_1m) < 2:
        return prev_direction

    c1 = candles_1m.iloc[-2]["close"]
    c2 = candles_1m.iloc[-1]["close"]

    if c2 > c1:
        return 1
    elif c2 < c1:
        return -1
    else:
        return prev_direction

# ---------- DIAGNOSTICS: FULL VISIBILITY ----------
print("\n===== CELL 13: SEEDED 1m HISTORY =====")
print("Total rows:", len(candles))
if len(candles):
    print("First ts:", candles.iloc[0]["timestamp"])
    print("Last  ts:", candles.iloc[-1]["timestamp"])
    print("\nHEAD:")
    print(candles.head(5))
    print("\nTAIL:")
    print(candles.tail(5))
print("=====================================\n")
