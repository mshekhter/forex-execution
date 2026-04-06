# =========================
# PAPER EXECUTION — SHADOW MODE (FAULTS: tick validity, staleness, spread)
# =========================

import uuid
from datetime import datetime, timezone

PIP = 0.0001

# Fault gates (feed health, not strategy behavior)
MAX_TICK_AGE_SECONDS = 10.0
MAX_SPREAD_PIPS = 3.0

_paper_seq = 0  # internal sequential audit counter

def paper_execute_trade(
    *,
    signal_idx: int,
    signal_ts_utc: datetime,
    signal_price: float,
    direction: int,              # 1 = long, -1 = short
    emission_ts_utc: datetime,   # loop_now_utc at admission time
    exec_snapshot: dict,         # latched tick dict
):
    global _paper_seq
    _paper_seq += 1

    # Normalize emission time
    if emission_ts_utc.tzinfo is None:
        emission_ts_utc = emission_ts_utc.replace(tzinfo=timezone.utc)

    # Tick must be valid
    if not is_valid_tick(exec_snapshot):
        record = {
            "external_order_id": f"SHADOW-{uuid.uuid4().hex[:10].upper()}",
            "internal_audit_id": f"S{_paper_seq:06d}",
            "signal_idx": int(signal_idx),
            "signal_ts_utc": signal_ts_utc,
            "signal_price": float(signal_price),
            "direction": "LONG" if int(direction) == 1 else "SHORT",
            "emission_ts_utc": emission_ts_utc,
            "exec_ts_utc": None,
            "exec_bid": None,
            "exec_ask": None,
            "exec_price": None,
            "spread_pips": None,
            "tick_age_seconds": None,
            "aborted": True,
            "abort_reason": "invalid_tick",
        }
        try:
            log_execution_event(record, "PAPER_EXEC_ABORT")
        except Exception:
            pass
        return record

    bid = float(exec_snapshot["bid"])
    ask = float(exec_snapshot["ask"])
    exec_ts_utc = exec_snapshot["ts_utc"]
    if exec_ts_utc.tzinfo is None:
        exec_ts_utc = exec_ts_utc.replace(tzinfo=timezone.utc)

    spread_pips = (ask - bid) / PIP
    tick_age_seconds = (emission_ts_utc - exec_ts_utc).total_seconds()

    aborted = False
    abort_reason = None

    # Stale tick means the feed is not healthy at admission time
    if tick_age_seconds > float(MAX_TICK_AGE_SECONDS):
        aborted = True
        abort_reason = "stale_tick"

    # Spread gate protects against pathological execution cost
    if (not aborted) and (spread_pips > float(MAX_SPREAD_PIPS)):
        aborted = True
        abort_reason = "wide_spread"

    if int(direction) == 1:
        exec_price = ask
        dir_str = "LONG"
    else:
        exec_price = bid
        dir_str = "SHORT"

    external_order_id = f"SHADOW-{uuid.uuid4().hex[:10].upper()}"
    internal_audit_id = f"S{_paper_seq:06d}"

    record = {
        "external_order_id": external_order_id,
        "internal_audit_id": internal_audit_id,
        "signal_idx": int(signal_idx),
        "signal_ts_utc": signal_ts_utc,
        "signal_price": float(signal_price),
        "direction": dir_str,
        "emission_ts_utc": emission_ts_utc,
        "exec_ts_utc": exec_ts_utc,
        "exec_bid": bid,
        "exec_ask": ask,
        "exec_price": float(exec_price),
        "spread_pips": float(spread_pips),
        "tick_age_seconds": float(tick_age_seconds),
        "aborted": bool(aborted),
        "abort_reason": abort_reason,
    }

    # One timestamp in the message: the moment of logging (execution decision time)
    msg = (
        f"UTC={emission_ts_utc.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"ET={emission_ts_utc.astimezone(ET).strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"PAPER_EXEC | {dir_str}\n"
        f"EXEC_PRICE={exec_price:.5f} | SPREAD_PIPS={spread_pips:.2f} | "
        f"TICK_AGE_S={tick_age_seconds:.2f} | "
        f"{'ABORTED' if aborted else 'OK'}\n"
        f"OID={external_order_id}"
    )

    notify("PAPER_EXEC", msg)

    try:
        log_execution_event(record, "PAPER_EXEC_ABORT" if aborted else "PAPER_EXEC")
    except Exception:
        pass

    return record
