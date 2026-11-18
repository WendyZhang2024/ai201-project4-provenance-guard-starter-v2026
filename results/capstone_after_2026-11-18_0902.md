# Capstone run log — after

- Produced by: `capstone_eval.py::trial_main` and `::trial_start`
- Service: `app.py::submit` · record: `observe.py::record`
- 2026-11-18 09:02 · warm-on-import: `1`

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. one record per request | 20 new lines, every field present | 20/20 | 20/20 | 20/20 | MET |
| 2. the duration is the real duration | 10/10 within 15% or 100 ms | 10/10 | 10/10 | 10/10 | MET |
| 3. stats match their own rows | n equal, p50 and p95 within 1 ms | ok | ok | ok | MET |
| 4. a fresh copy serves with its own record | 3/3 starts, own count 1-2-3 | 200, n=1 | 200, n=2 | 200, n=3 | MET |
| 5. the first request is not a load | under 3 s, 3 of 3 | 0.2 s | 0.2 s | 0.3 s | MET |

**Verdicts**

- Trial 1: C1 MET · C2 MET · C3 MET
- Trial 2: C1 MET · C2 MET · C3 MET
- Trial 3: C1 MET · C2 MET · C3 MET
- Start 1: C4 MET · C5 MET (import 11275 ms + first request 215 ms = 11490 ms)
- Start 2: C4 MET · C5 MET (import 10996 ms + first request 198 ms = 11194 ms)
- Start 3: C4 MET · C5 MET (import 11677 ms + first request 290 ms = 11967 ms)

---

## What actually came back

### Criterion 1 — twenty calls, twenty records

```json
{
  "lines": 20,
  "expected": 20,
  "statuses": [
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    200,
    400,
    400,
    413
  ],
  "fields_ok": true,
  "decided_ok": true
}
```

### Criterion 2 — recorded against client wall time

| # | recorded `t_total_ms` | client wall ms | within tolerance |
|---|---|---|---|
| 1 | 144.1 | 146.7 | yes |
| 2 | 211.7 | 215.7 | yes |
| 3 | 92.3 | 94.7 | yes |
| 4 | 114.4 | 116.6 | yes |
| 5 | 174.9 | 177.3 | yes |
| 6 | 131.7 | 133.8 | yes |
| 7 | 129.3 | 132.0 | yes |
| 8 | 183.3 | 186.0 | yes |
| 9 | 231.5 | 233.8 | yes |
| 10 | 114.7 | 117.4 | yes |

### Criterion 3 — `/stats` against the rows

```json
{
  "n": 133,
  "lines": 133,
  "p50": 153.6,
  "p50_recomputed": 153.6,
  "p95": 9906.6,
  "p95_recomputed": 9906.6,
  "ok": true
}
```

### Criteria 4 and 5 — independent starts

```json
[
  {
    "ts": "2026-11-18T09:01:11",
    "import_ms": 11274.7,
    "first_ms": 215.2,
    "total_ms": 11489.9,
    "status": 200,
    "health_ok": true,
    "lines_in_this_copy": 1,
    "warm_on_import": "1"
  },
  {
    "ts": "2026-11-18T09:01:23",
    "import_ms": 10996.1,
    "first_ms": 198.5,
    "total_ms": 11194.5,
    "status": 200,
    "health_ok": true,
    "lines_in_this_copy": 2,
    "warm_on_import": "1"
  },
  {
    "ts": "2026-11-18T09:01:36",
    "import_ms": 11677.4,
    "first_ms": 289.5,
    "total_ms": 11966.8,
    "status": 200,
    "health_ok": true,
    "lines_in_this_copy": 3,
    "warm_on_import": "1"
  }
]
```

### Ten records from the log

```text
{"ts": "2026-11-18T01:02:06.841+00:00", "request_id": "b71218af-2082-4fe1-9bea-400bc9f76ce9", "creator_id": "capafter3_t0", "event": "decided", "status": 200, "input_sha256": "b9417d3d85ae2fac", "input_chars": 365, "input_preview": "As a fan of How It Works, I have a deep interest in astronomy. I first encounter", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.6349, "style_score": 0.2852, "t_total_ms": 154.2, "t_model_ms": 137.6, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 1203.1, "reason": null}
{"ts": "2026-11-18T01:02:07.065+00:00", "request_id": "d1d6e90b-0569-41c2-af4e-5360099e383d", "creator_id": "capafter3_t1", "event": "decided", "status": 200, "input_sha256": "e17ceacd8bd5d70d", "input_chars": 712, "input_preview": "Music is a miracle, it is the root and soul of my life. I found music a second l", "output_guess": "unsure", "output_confidence": 0.4268, "model_score": 0.3466, "style_score": 0.547, "t_total_ms": 209.5, "t_model_ms": 192.6, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1593.8, "reason": null}
{"ts": "2026-11-18T01:02:07.188+00:00", "request_id": "33c4ed64-9e9a-421e-a676-d888923845c7", "creator_id": "capafter3_t0", "event": "decided", "status": 200, "input_sha256": "54b831aff4d0c8d7", "input_chars": 241, "input_preview": "I conducted several independent research studies including attention economy and", "output_guess": "unsure", "output_confidence": 0.4592, "model_score": 0.1556, "style_score": 0.9145, "t_total_ms": 107.7, "t_model_ms": 92.7, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 859.4, "reason": null}
{"ts": "2026-11-18T01:02:07.343+00:00", "request_id": "fe300f93-71a3-401e-9247-eca40e3b518a", "creator_id": "capafter3_t1", "event": "decided", "status": 200, "input_sha256": "613ff153a0b26853", "input_chars": 304, "input_preview": "“Know Thyself” to me means embracing complexity: being both scientist and artist", "output_guess": "human", "output_confidence": 0.2822, "model_score": 0.2709, "style_score": 0.2991, "t_total_ms": 139.7, "t_model_ms": 122.7, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 984.4, "reason": null}
{"ts": "2026-11-18T01:02:07.589+00:00", "request_id": "a4965ac4-f913-4b18-aa37-c0e9c9aa1376", "creator_id": "capafter3_t0", "event": "decided", "status": 200, "input_sha256": "7d62aaaaa91259e5", "input_chars": 635, "input_preview": "“Odors have a power of persuasion stronger than that of words, appearances, emot", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.594, "style_score": 0.2801, "t_total_ms": 230.6, "t_model_ms": 212.5, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1718.8, "reason": null}
{"ts": "2026-11-18T01:02:07.799+00:00", "request_id": "bf71a28b-1a4c-4fbc-8138-355ad015a39a", "creator_id": "capafter3_t1", "event": "decided", "status": 200, "input_sha256": "2a10eaa04390438e", "input_chars": 427, "input_preview": "“And, following my “perfume atlas,” people, too, seemed to carry notes. I once s", "output_guess": "human", "output_confidence": 0.1917, "model_score": 0.2641, "style_score": 0.0831, "t_total_ms": 194.1, "t_model_ms": 176.7, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1328.1, "reason": null}
{"ts": "2026-11-18T01:02:07.983+00:00", "request_id": "d93234e1-97a8-436f-a053-3c0e4d9dcac0", "creator_id": "capafter3_t0", "event": "decided", "status": 200, "input_sha256": "d073e3ee0c3c146a", "input_chars": 328, "input_preview": "”And so the opening sentence returns to me with a different weight. “Odors have ", "output_guess": "human", "output_confidence": 0.2345, "model_score": 0.2033, "style_score": 0.2812, "t_total_ms": 170.4, "t_model_ms": 153.8, "t_style_ms": 0.6, "t_load_ms": 0.0, "cpu_ms": 1234.4, "reason": null}
{"ts": "2026-11-18T01:02:08.219+00:00", "request_id": "dba6fb98-4e4b-4000-91a0-dce9a94bf320", "creator_id": "capafter3_t1", "event": "decided", "status": 200, "input_sha256": "e88773c747dd6f55", "input_chars": 767, "input_preview": "At Columbia, through the lens of both STEM and humanity, I’ll be able to explore", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.3678, "style_score": 0.4269, "t_total_ms": 219.9, "t_model_ms": 202.4, "t_style_ms": 0.5, "t_load_ms": 0.0, "cpu_ms": 1671.9, "reason": null}
{"ts": "2026-11-18T01:02:08.442+00:00", "request_id": "b81d69ac-5bf5-4bd4-b507-b9796ea4d9b8", "creator_id": "capafter3_t0", "event": "decided", "status": 200, "input_sha256": "d6255b91530413ea", "input_chars": 710, "input_preview": "Apart from academics, the Twin Cities offers a world of creative exploration. I ", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.5625, "style_score": 0.1206, "t_total_ms": 210.2, "t_model_ms": 195.5, "t_style_ms": 0.4, "t_load_ms": 0.0, "cpu_ms": 1734.4, "reason": null}
{"ts": "2026-11-18T01:02:08.579+00:00", "request_id": "d12f9b1b-4f1a-4f36-b678-ba3aa3756bf7", "creator_id": "capafter3_t1", "event": "decided", "status": 200, "input_sha256": "8bd97a84ac20cc7a", "input_chars": 344, "input_preview": "He told me that one of my piano arrangements had kept him company during the low", "output_guess": "unsure", "output_confidence": 0.6076, "model_score": 0.6178, "style_score": 0.5922, "t_total_ms": 125.7, "t_model_ms": 111.7, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1000.0, "reason": null}
```
