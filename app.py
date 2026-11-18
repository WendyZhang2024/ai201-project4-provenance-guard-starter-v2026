#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import os
import time
import uuid

from flask import Flask, jsonify, request

import audit
import config
import detector
import observe
import scoring
import stylometry

app = Flask(__name__)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# ON. Milestone 1's three steps are done:
#
#   1. RATE_LIMITING_ENABLED = True in config.py
#   2. the numbers chosen there (10/minute, 200/day)
#   3. the @limiter.limit(...) line on /submit below is uncommented
#
# Both limits are enforced at once; whichever is breached first answers 429 and
# says which one it was. While limiting is off, _LimiterOff keeps that decorator
# a harmless no-op — that is why uncommenting it early never crashed anything.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

def _creator_of(payload) -> str:
    """The name to log an attempt under, before we know whether it is valid."""
    creator = payload.get("creator_id") if isinstance(payload, dict) else None
    return creator if isinstance(creator, str) and creator.strip() else "unknown"


def _text_of(payload) -> str:
    """Whatever was sent as text, even if it is not usable."""
    text = payload.get("text") if isinstance(payload, dict) else None
    return text if isinstance(text, str) else ""


def _validate(payload):
    """
    The four rules, in one place, with no Flask in them.

    Either (text, creator_id) on success, or (None, (status, error, reason,
    message)) on rejection. Pulled out of the route so the rules read as four
    lines and so the route has room for the record this unit adds.

    `error` is what the caller sees, `reason` is what the audit log keeps. They
    differ on the two 400s on purpose: the log says which rule fired, the caller
    gets the one word unit 8's contract already used.
    """
    if not isinstance(payload, dict):
        return None, (400, "bad_request", "invalid_json",
                      "Send a JSON object with text and creator_id.")

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return None, (400, "bad_request", "missing_or_empty_text",
                      "text is required and must be a non-empty string.")

    if len(text) > config.MAX_TEXT_CHARS:
        return None, (413, "text_too_large", "text_too_large",
                      f"text must be at most {config.MAX_TEXT_CHARS:,} characters.")

    creator_id = payload.get("creator_id")
    if not isinstance(creator_id, str) or not creator_id.strip():
        return None, (400, "bad_request", "missing_creator_id",
                      "creator_id is required and must be a non-empty string.")

    return text, creator_id


def _log(event, status, t0, c0, **fields):
    """
    One line in logs/requests.jsonl, whatever the outcome.

    The timestamp and the duration are computed here so no exit has to remember
    to do it, and the failures come through the same function as the successes:
    an outcome that only exists when nothing went wrong is the absence unit 8
    spent a whole milestone learning to see.
    """
    observe.record(
        request_id=fields.pop("request_id", None),
        creator_id=fields.pop("creator_id", "unknown"),
        event=event,
        status=status,
        t_total_ms=(time.perf_counter() - t0) * 1000,
        cpu_ms=(time.process_time() - c0) * 1000,
        **fields,
    )


@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """Validate, score, record, answer — four steps, in that order."""
    t0, c0 = time.perf_counter(), time.process_time()
    payload = request.get_json(silent=True)
    text, detail = _validate(payload)

    if text is None:
        status, error, reason, message = detail
        extra = ({"text_length": len(_text_of(payload))}
                 if reason == "text_too_large" else {})
        audit.log_rejection(creator_id=_creator_of(payload), reason=reason, **extra)
        _log("rejected", status, t0, c0, creator_id=_creator_of(payload),
             text=_text_of(payload), reason=reason)
        return jsonify({"error": error, "message": message}), status

    creator_id = detail
    content_id = str(uuid.uuid4())
    was_cold = detector._model is None
    t_model_ms = 0.0

    try:
        t = time.perf_counter()
        model_score = detector.model_signal(text)
        t_model_ms = (time.perf_counter() - t) * 1000
    except detector.DetectorUnavailable as exc:
        _log("error", 500, t0, c0, request_id=content_id, creator_id=creator_id,
             text=text, reason="detector_unavailable", t_model_ms=t_model_ms)
        audit.log_rejection(creator_id=creator_id, reason="detector_unavailable")
        return jsonify({"error": "internal", "message": str(exc)}), 500
    except ValueError as exc:
        _log("rejected", 400, t0, c0, request_id=content_id, creator_id=creator_id,
             text=text, reason="text_too_short", t_model_ms=t_model_ms)
        audit.log_rejection(creator_id=creator_id, reason="text_too_short")
        return jsonify({"error": "bad_request", "message": str(exc)}), 400

    t = time.perf_counter()
    style_score = stylometry.style_signal(text)
    t_style_ms = (time.perf_counter() - t) * 1000

    confidence = scoring.combine_signals(model_score, style_score)
    guess, label = scoring.score_to_label(confidence)

    audit.log_decision(
        content_id=content_id, creator_id=creator_id, guess=guess,
        model_score=model_score, style_score=style_score,
        combined_score=confidence, label=label, status="decided",
    )
    _log("decided", 200, t0, c0, request_id=content_id, creator_id=creator_id,
         text=text, guess=guess, confidence=confidence,
         model_score=model_score, style_score=style_score,
         t_model_ms=t_model_ms, t_style_ms=t_style_ms,
         t_load_ms=(detector._load_ms if was_cold else 0.0))

    return jsonify({
        "content_id": content_id,
        "guess": guess,
        "confidence": confidence,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
    })

@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong. Milestone 5.

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}

    Should:
      1. Check the content_id actually exists — `audit.entries_for(id)` tells
         you. A typo here fails silently and looks like a broken endpoint,
         which is the single most common way this milestone eats an hour.
      2. Record the appeal with `audit.log_appeal(...)`, which moves the item
         to `under_review`.
      3. Confirm to the writer. No automatic re-checking needed.

    This is the smallest endpoint in the project and the one that matters most
    to the person on the other end. It's the only thing standing between a
    wrong accusation and nothing at all.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "error": "bad_request",
            "message": "Send a JSON object with content_id and reasoning.",
        }), 400

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")
    creator_id = payload.get("creator_id")

    if not isinstance(content_id, str) or not content_id.strip():
        return jsonify({
            "error": "bad_request",
            "message": "content_id is required.",
        }), 400

    if not isinstance(reasoning, str) or not reasoning.strip():
        return jsonify({
            "error": "bad_request",
            "message": "reasoning is required and must be a non-empty string.",
        }), 400

    if creator_id is not None and (
        not isinstance(creator_id, str) or not creator_id.strip()
    ):
        return jsonify({
            "error": "bad_request",
            "message": "creator_id must be a non-empty string when provided.",
        }), 400

    entries = audit.entries_for(content_id)
    decision = next((e for e in entries if e.get("event") != "appeal"), None)
    if decision is None or not decision.get("creator_id"):
        return jsonify({
            "error": "not_found",
            "message": "No matching submission.",
        }), 404

    original_creator_id = decision["creator_id"]
    if creator_id is not None and creator_id != original_creator_id:
        return jsonify({
            "error": "not_found",
            "message": "No matching submission.",
        }), 404

    audit.log_appeal(
        content_id=content_id,
        creator_id=creator_id or original_creator_id,
        reasoning=reasoning,
    )

    appeal_count = sum(
        1 for e in audit.entries_for(content_id) if e.get("event") == "appeal"
    )

    return jsonify({
        "ok": True,
        "content_id": content_id,
        "status": "under_review",
        "appeal_count": appeal_count,
        "message": "Thanks — a human will review this.",
    })


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


@app.get("/stats")
def stats():
    """The aggregate over the request log: count, p50, p95, cost."""
    return jsonify(observe.summary())


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


# ── UNIT 9 — the run path ─────────────────────────────────────────────────────

# Load the model when this module is imported rather than inside the first
# request. `python app.py` and `gunicorn app:app` both import before serving, so
# the cost moves from the first user's request to the process start — where a
# deploy can wait and a user cannot, and where a model that refuses to load
# fails the start instead of the first request.
#
# AI201_WARM_ON_IMPORT=0 turns it off. That switch is how the before and after
# numbers come from one code path instead of two commits.
if os.getenv("AI201_WARM_ON_IMPORT", "1") == "1":
    detector.warm_up()


if __name__ == "__main__":
    main()
