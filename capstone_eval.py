#!/usr/bin/env python3
"""
The capstone run log — UNIT 9.

    python capstone_eval.py main   --label before    # criteria 1-3, three trials
    python capstone_eval.py start  --label before    # criteria 4-5, ONE trial
    python capstone_eval.py report --label before    # results/capstone_before.md

`main` drives the app in-process through Flask's test client, so it needs no port and no second
terminal. `start` measures one independent process start, so run it three times — from a fresh copy
of the repository for criterion 4 — and `report` merges whatever trials it found.

Nothing here decides whether a target was met. It records what came back; the verdicts live in
criteria.md and the README.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import config
import observe
import scenarios

STATE = config.RESULTS_DIR / "capstone_state.json"

# The texts, taken from the unit 8 calibration set so the same inputs keep being
# scored across units rather than a new set nobody can compare against.
TEXTS = [
    scenarios.MY_ASTRONOMY, scenarios.MY_MUSIC, scenarios.MY_RESEARCH,
    scenarios.MY_KNOW_THYSELF, scenarios.MY_SMELL, scenarios.MY_PERFUME_ATLAS,
    scenarios.MY_OPENING_RETURNS, scenarios.MY_COLUMBIA, scenarios.MY_TWIN_CITIES,
    scenarios.MY_PIANO_ARRANGEMENT, scenarios.AI_SHORT, scenarios.AI_LONG,
    scenarios.AI_GENERIC_1, scenarios.AI_GENERIC_2, scenarios.AI_EDITED,
    scenarios.AI_EDITED_2, scenarios.MY_WEEKEND,
]


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def pct(values, p):
    if not values:
        return None
    values = sorted(values)
    return round(values[min(len(values) - 1, int(p * len(values)))], 1)


# ── criteria 1-3 ─────────────────────────────────────────────────────────────

def trial_main(cli, label: str, trial: int) -> dict:
    """Twenty calls, ten timed calls, and one check of the aggregate."""
    tag = f"cap{label}{trial}"
    creators = [f"{tag}_a", f"{tag}_b", f"{tag}_c"]

    # Criterion 1 — 17 valid, 2 malformed, 1 oversized.
    before = len(observe.read())
    bodies = [{"text": t, "creator_id": creators[i % 3]} for i, t in enumerate(TEXTS)]
    bodies.append({"creator_id": creators[0]})                        # no text
    bodies.append({"text": "", "creator_id": creators[1]})           # empty
    bodies.append({"text": "word " * 50_000, "creator_id": creators[2]})  # 250k chars

    statuses = [cli.post("/submit", json=b).status_code for b in bodies]
    rows = observe.read()[before:]

    decided = [r for r in rows if r.get("event") == "decided"]
    c1 = {
        "lines": len(rows),
        "expected": len(bodies),
        "statuses": statuses,
        "fields_ok": all(
            r.get("ts") and r.get("status") and r.get("t_total_ms") is not None
            and r.get("input_chars") is not None
            and (r.get("input_sha256") or not r.get("input_chars"))
            for r in rows
        ),
        "decided_ok": len(decided) == len(TEXTS) and all(
            r.get("model_score") is not None
            and r.get("style_score") is not None
            and r.get("output_confidence") is not None
            for r in decided
        ),
    }

    # Criterion 2 — ten warm calls, client wall time against the record.
    pairs, passed = [], 0
    for i, text in enumerate(TEXTS[:10]):
        creator = f"{tag}_t{i % 2}"
        t0 = time.perf_counter()
        response = cli.post("/submit", json={"text": text, "creator_id": creator})
        wall = (time.perf_counter() - t0) * 1000
        cid = response.get_json().get("content_id")
        record = next((r for r in observe.read() if r.get("request_id") == cid), None)
        recorded = record["t_total_ms"] if record else None
        tolerance = max(100.0, 0.15 * wall)
        ok = recorded is not None and abs(recorded - wall) <= tolerance
        passed += bool(ok)
        pairs.append({"recorded_ms": recorded, "client_ms": round(wall, 1), "ok": ok})

    # Criterion 3 — the aggregate against the rows.
    summary = observe.summary()
    all_rows = observe.read()
    totals = [
        float(r["t_total_ms"]) for r in all_rows
        if r.get("event") == "decided" and r.get("t_total_ms") is not None
    ]
    p50, p95 = pct(totals, 0.50), pct(totals, 0.95)
    c3 = {
        "n": summary["n"], "lines": len(all_rows),
        "p50": summary["p50_ms"], "p50_recomputed": p50,
        "p95": summary["p95_ms"], "p95_recomputed": p95,
        "ok": (
            summary["n"] == len(all_rows)
            and p50 is not None and summary["p50_ms"] is not None
            and abs(summary["p50_ms"] - p50) <= 1
            and abs(summary["p95_ms"] - p95) <= 1
        ),
    }

    return {"c1": c1, "c2": {"passed": passed, "of": 10, "pairs": pairs}, "c3": c3}


# ── criteria 4-5 ─────────────────────────────────────────────────────────────

def trial_start(label: str) -> dict:
    """One independent start: how long to import, and how long the first answer takes."""
    t0 = time.perf_counter()
    import app as A                      # noqa: E402  — timed on purpose
    import_ms = (time.perf_counter() - t0) * 1000

    cli = A.app.test_client()
    health = cli.get("/health").get_json()

    t1 = time.perf_counter()
    response = cli.post("/submit", json={"text": TEXTS[0], "creator_id": f"start_{label}"})
    first_ms = (time.perf_counter() - t1) * 1000

    return {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "import_ms": round(import_ms, 1),
        "first_ms": round(first_ms, 1),
        "total_ms": round(import_ms + first_ms, 1),
        "status": response.status_code,
        "health_ok": bool(health.get("ok")),
        "lines_in_this_copy": len(A.observe.read()),
        "warm_on_import": os.getenv("AI201_WARM_ON_IMPORT", "1"),
    }


# ── the report ───────────────────────────────────────────────────────────────

def write_report(label: str, state: dict) -> None:
    main_trials = state.get(label, {}).get("main", [])
    starts = state.get(label, {}).get("start", [])
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    path = config.RESULTS_DIR / f"capstone_{label}_{stamp}.md"

    def verdict_c1(t):
        return "MET" if t["c1"]["lines"] == 20 and t["c1"]["fields_ok"] and t["c1"]["decided_ok"] else "MISSED"

    def verdict_c2(t):
        return "MET" if t["c2"]["passed"] == 10 else "MISSED"

    def verdict_c3(t):
        return "MET" if t["c3"]["ok"] else "MISSED"

    lines = [
        f"# Capstone run log — {label}",
        "",
        f"- Produced by: `capstone_eval.py::trial_main` and `::trial_start`",
        f"- Service: `app.py::submit` · record: `observe.py::record`",
        f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} · warm-on-import: "
        f"`{starts[0]['warm_on_import'] if starts else 'n/a'}`",
        "",
        "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
        "|---|---|---|---|---|---|",
    ]

    def at(seq, i):
        return seq[i] if i < len(seq) else None

    c1, c2, c3, c4, c5 = [], [], [], [], []
    for i in range(3):
        t, s = at(main_trials, i), at(starts, i)
        c1.append(f"{t['c1']['lines']}/20" if t else "—")
        c2.append(f"{t['c2']['passed']}/10" if t else "—")
        c3.append(("ok" if t["c3"]["ok"] else "mismatch") if t else "—")
        c4.append(f"200, n={s['lines_in_this_copy']}" if s and s["status"] == 200 else ("—" if not s else str(s["status"])))
        c5.append(f"{s['first_ms'] / 1000:.1f} s" if s else "—")

    verdicts = [
        "MET" if main_trials and all(verdict_c1(t) == "MET" for t in main_trials) else "MISSED",
        "MET" if main_trials and all(verdict_c2(t) == "MET" for t in main_trials) else "MISSED",
        "MET" if main_trials and all(verdict_c3(t) == "MET" for t in main_trials) else "MISSED",
        "MET" if len(starts) == 3 and all(s["status"] == 200 and s["health_ok"] for s in starts) else "MISSED",
        "MET" if len(starts) == 3 and all(s["first_ms"] < 3000 for s in starts) else "MISSED",
    ]

    for number, name, target, cells, verdict in [
        ("1", "one record per request", "20 new lines, every field present", c1, verdicts[0]),
        ("2", "the duration is the real duration", "10/10 within 15% or 100 ms", c2, verdicts[1]),
        ("3", "stats match their own rows", "n equal, p50 and p95 within 1 ms", c3, verdicts[2]),
        ("4", "a fresh copy serves with its own record", "3/3 starts, own count 1-2-3", c4, verdicts[3]),
        ("5", "the first request is not a load", "under 3 s, 3 of 3", c5, verdicts[4]),
    ]:
        lines.append(f"| {number}. {name} | {target} | " + " | ".join(cells) + f" | {verdict} |")

    lines += ["", "**Verdicts**", ""]
    for i, t in enumerate(main_trials, 1):
        lines.append(f"- Trial {i}: C1 {verdict_c1(t)} · C2 {verdict_c2(t)} · C3 {verdict_c3(t)}")
    for i, s in enumerate(starts, 1):
        lines.append(
            f"- Start {i}: C4 {'MET' if s['status'] == 200 and s['health_ok'] else 'MISSED'} · "
            f"C5 {'MET' if s['first_ms'] < 3000 else 'MISSED'} "
            f"(import {s['import_ms']:.0f} ms + first request {s['first_ms']:.0f} ms = {s['total_ms']:.0f} ms)"
        )

    lines += ["", "---", "", "## What actually came back", "",
              "### Criterion 1 — twenty calls, twenty records", ""]
    if main_trials:
        lines += ["```json", json.dumps(main_trials[0]["c1"], indent=2), "```", ""]
    lines += ["### Criterion 2 — recorded against client wall time", ""]
    if main_trials:
        rows = main_trials[0]["c2"]["pairs"]
        lines += ["| # | recorded `t_total_ms` | client wall ms | within tolerance |", "|---|---|---|---|"]
        for i, p in enumerate(rows, 1):
            lines.append(f"| {i} | {p['recorded_ms']} | {p['client_ms']} | {'yes' if p['ok'] else 'no'} |")
        lines.append("")
    lines += ["### Criterion 3 — `/stats` against the rows", ""]
    if main_trials:
        lines += ["```json", json.dumps(main_trials[0]["c3"], indent=2), "```", ""]
    lines += ["### Criteria 4 and 5 — independent starts", ""]
    if starts:
        lines += ["```json", json.dumps(starts, indent=2), "```", ""]
    lines += ["### Ten records from the log", "",
              "```text", *[json.dumps(r, ensure_ascii=False) for r in observe.read()[-10:]], "```", ""]

    path.write_text("\r\n".join(lines), encoding="utf-8")
    print(f"wrote {path.relative_to(config.ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["main", "start", "report"])
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    state = load_state()
    state.setdefault(args.label, {}).setdefault("main", [])

    if args.mode == "main":
        import app as A
        cli = A.app.test_client()
        for trial in (1, 2, 3):
            result = trial_main(cli, args.label, trial)
            state[args.label]["main"].append(result)
            save_state(state)
            print(f"trial {trial}: C1 {result['c1']['lines']}/20 "
                  f"(fields {'ok' if result['c1']['fields_ok'] else 'MISSING'}), "
                  f"C2 {result['c2']['passed']}/10, C3 {'ok' if result['c3']['ok'] else 'MISMATCH'}")
    elif args.mode == "start":
        result = trial_start(args.label)
        state[args.label].setdefault("start", []).append(result)
        save_state(state)
        print(json.dumps(result, indent=2))
    else:
        write_report(args.label, state)


if __name__ == "__main__":
    main()
