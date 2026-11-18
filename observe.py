"""
The operational layer — UNIT 9.

One JSON line per request: what came in, what came out, and how long each stage
took. Not a print(): a file you can read back, aggregate, and paste into the
README as text.

    from observe import record, summary
"""

import hashlib
import json
import threading
from datetime import datetime, timezone

import config

REQUESTS_LOG = config.LOG_DIR / "requests.jsonl"
_lock = threading.Lock()

# A reference price, not a measurement: a small cloud instance costs about
# USD 0.0416/hour for 2 vCPU, so one CPU-second is 0.0416 / 3600 / 2. Your
# laptop is not that instance; this is what the same work would cost if rented.
USD_PER_CPU_SECOND = 0.0416 / 3600 / 2


def record(
    request_id,
    creator_id,
    event,
    status,
    t_total_ms,
    text="",
    guess=None,
    confidence=None,
    model_score=None,
    style_score=None,
    t_model_ms=0.0,
    t_style_ms=0.0,
    t_load_ms=0.0,
    cpu_ms=0.0,
    reason=None,
) -> dict:
    """One line. `event` is decided, rejected or error; `status` is the HTTP code."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "request_id": request_id,
        "creator_id": creator_id,
        "event": event,
        "status": status,
        "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else None,
        "input_chars": len(text) if text else 0,
        "input_preview": text[:80] if text else None,
        "output_guess": guess,
        "output_confidence": confidence,
        "model_score": model_score,
        "style_score": style_score,
        "t_total_ms": round(t_total_ms, 1),
        "t_model_ms": round(t_model_ms, 1),
        "t_style_ms": round(t_style_ms, 1),
        "t_load_ms": round(t_load_ms, 1),
        "cpu_ms": round(cpu_ms, 1),
        "reason": reason,
    }
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    with _lock, REQUESTS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read(limit=None) -> list:
    """Read the record back, oldest first. A bad line is skipped, not fatal."""
    if not REQUESTS_LOG.exists():
        return []
    rows = []
    for line in REQUESTS_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:] if limit else rows


def summary(limit=None) -> dict:
    """The aggregate, recomputed from the rows every time. O(n) is fine here."""
    rows = read(limit)
    totals = sorted(
        float(r["t_total_ms"])
        for r in rows
        if r.get("event") == "decided" and r.get("t_total_ms") is not None
    )

    def pct(p):
        if not totals:
            return None
        return round(totals[min(len(totals) - 1, int(p * len(totals)))], 1)

    cpu_s = sum(float(r.get("cpu_ms") or 0.0) for r in rows) / 1000.0
    per = (cpu_s / len(rows)) if rows else 0.0

    return {
        "n": len(rows),
        "decided": len(totals),
        "rejected": sum(1 for r in rows if r.get("event") == "rejected"),
        "p50_ms": pct(0.50),
        "p95_ms": pct(0.95),
        "cpu_s_total": round(cpu_s, 2),
        "usd_per_request": round(per * USD_PER_CPU_SECOND, 9),
        "usd_per_hundred": round(per * 100 * USD_PER_CPU_SECOND, 7),
    }
