# =========================
# CELL: TICK LOGGER (CSV, ASYNC, AUTO-START, TOGGLE, SATURATION WARNING)
# FULL DROP-IN REPLACEMENT
# =========================

import os
import csv
import time
import threading
import queue
from datetime import datetime, timezone

TICK_LOG_DIR = "logs"
TICK_LOG_PREFIX = "ticks_"

TICK_LOG_BUFFER_MAX = 100_000
TICK_LOG_FLUSH_SECONDS = 1.0

# TOGGLE ONLY AFFECTS ENQUEUE, NOT BOOT
TICK_LOG_ENABLED = True

_tick_q = queue.Queue(maxsize=TICK_LOG_BUFFER_MAX)
_tick_drop_flag = False
_tick_warned = False
_tick_lock = threading.Lock()


def _tick_log_path(ts_utc: datetime) -> str:
    return os.path.join(
        TICK_LOG_DIR,
        f"{TICK_LOG_PREFIX}{ts_utc.strftime('%Y%m%d')}.csv"
    )


def reset_tick_saturation_warning():
    global _tick_drop_flag, _tick_warned
    with _tick_lock:
        _tick_drop_flag = False
        _tick_warned = False


def _tick_writer():
    os.makedirs(TICK_LOG_DIR, exist_ok=True)

    current_path = None
    f = None
    w = None
    last_flush = time.time()

    try:
        while True:
            item = _tick_q.get()
            if item is None:
                break

            ts_utc = item["ts_utc"]
            if ts_utc.tzinfo is None:
                ts_utc = ts_utc.replace(tzinfo=timezone.utc)

            path = _tick_log_path(ts_utc)

            if path != current_path:
                if f is not None:
                    try:
                        f.flush()
                        f.close()
                    except Exception:
                        pass

                current_path = path
                is_new = not os.path.exists(path)

                f = open(path, "a", newline="", encoding="utf-8")
                w = csv.writer(f)

                if is_new:
                    w.writerow(["timestamp_utc", "bid", "ask", "audit_id"])

            w.writerow([
                ts_utc.strftime("%Y-%m-%d %H:%M:%S.%f"),
                item["bid"],
                item["ask"],
                item["audit_id"],
            ])

            now = time.time()
            if (now - last_flush) >= TICK_LOG_FLUSH_SECONDS:
                try:
                    f.flush()
                except Exception:
                    pass
                last_flush = now

            with _tick_lock:
                if _tick_drop_flag and not _tick_warned:
                    print(
                        "[TICK_LOG] buffer saturated, ticks are being dropped. "
                        "call reset_tick_saturation_warning() after review."
                    )
                    _tick_warned = True

            _tick_q.task_done()

    finally:
        if f is not None:
            try:
                f.flush()
                f.close()
            except Exception:
                pass


# AUTO-START WRITER THREAD AT IMPORT TIME
_tick_thread = threading.Thread(
    target=_tick_writer,
    name="tick_csv_writer",
    daemon=True,
)
_tick_thread.start()


def enqueue_tick_for_logging(*, bid: float, ask: float, audit_id, ts_utc: datetime):
    global _tick_drop_flag

    if not TICK_LOG_ENABLED:
        return

    try:
        _tick_q.put_nowait({
            "bid": float(bid),
            "ask": float(ask),
            "audit_id": "" if audit_id is None else str(audit_id),
            "ts_utc": ts_utc,
        })
    except queue.Full:
        with _tick_lock:
            _tick_drop_flag = True


def tick_logger_status():
    with _tick_lock:
        return {
            "enabled": bool(TICK_LOG_ENABLED),
            "buffer_max": int(TICK_LOG_BUFFER_MAX),
            "buffer_size": int(_tick_q.qsize()),
            "saturated": bool(_tick_drop_flag),
            "warned": bool(_tick_warned),
        }
