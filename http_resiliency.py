# =========================
# HTTP RESILIENCY + REQUESTS
# =========================

HTTP_TIMEOUT_SECONDS = 15
HTTP_MAX_RETRIES = 4
HTTP_BACKOFF_BASE_SECONDS = 0.6
HTTP_BACKOFF_MAX_SECONDS = 6.0

def _sleep_backoff(attempt):
    t = min(HTTP_BACKOFF_MAX_SECONDS, HTTP_BACKOFF_BASE_SECONDS * (2 ** attempt))
    t = t * (0.75 + random.random() * 0.5)
    time.sleep(t)

def _is_auth_error(status_code, json_data, text):
    if status_code in (401, 403):
        return True
    try:
        s = ""
        if isinstance(json_data, dict):
            s = json.dumps(json_data).lower()
        else:
            s = (text or "").lower()
        if "not authenticated" in s or "unauthorized" in s or "notauthorized" in s:
            return True
    except Exception:
        pass
    return False

def request_json(method, url, *, params=None, json_body=None, headers=None, timeout=HTTP_TIMEOUT_SECONDS):
    last_status = None
    last_text = None
    last_json = None
    last_exc = None

    for attempt in range(HTTP_MAX_RETRIES):
        try:
            r = requests.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=timeout,
            )
            last_status = r.status_code
            last_text = r.text

            try:
                last_json = r.json()
            except Exception:
                last_json = None

            if last_status in (408, 429, 500, 502, 503, 504):
                _sleep_backoff(attempt)
                continue

            return last_status, last_json, last_text

        except requests.RequestException as e:
            last_exc = e
            _sleep_backoff(attempt)

    if last_exc is not None:
        raise RuntimeError(f"HTTP failed after retries: {method} {url} error={last_exc}")
    raise RuntimeError(f"HTTP failed after retries: {method} {url} status={last_status} body={(last_text or '')[:300]}")

print("HTTP layer loaded")
