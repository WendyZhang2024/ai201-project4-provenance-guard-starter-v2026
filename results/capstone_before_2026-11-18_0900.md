# Capstone run log — before

- Produced by: `capstone_eval.py::trial_main` and `::trial_start`
- Service: `app.py::submit` · record: `observe.py::record`
- 2026-11-18 09:00 · warm-on-import: `0`

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. one record per request | 20 new lines, every field present | 20/20 | 20/20 | 20/20 | MET |
| 2. the duration is the real duration | 10/10 within 15% or 100 ms | 10/10 | 10/10 | 10/10 | MET |
| 3. stats match their own rows | n equal, p50 and p95 within 1 ms | ok | ok | ok | MET |
| 4. a fresh copy serves with its own record | 3/3 starts, own count 1-2-3 | 200, n=1 | 200, n=2 | 200, n=3 | MET |
| 5. the first request is not a load | under 3 s, 3 of 3 | 11.2 s | 11.3 s | 12.4 s | MISSED |

**Verdicts**

- Trial 1: C1 MET · C2 MET · C3 MET
- Trial 2: C1 MET · C2 MET · C3 MET
- Trial 3: C1 MET · C2 MET · C3 MET
- Start 1: C4 MET · C5 MISSED (import 426 ms + first request 11188 ms = 11613 ms)
- Start 2: C4 MET · C5 MISSED (import 408 ms + first request 11273 ms = 11681 ms)
- Start 3: C4 MET · C5 MISSED (import 425 ms + first request 12397 ms = 12822 ms)

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
| 1 | 131.9 | 134.8 | yes |
| 2 | 190.1 | 192.9 | yes |
| 3 | 111.1 | 117.2 | yes |
| 4 | 130.6 | 133.8 | yes |
| 5 | 203.4 | 206.8 | yes |
| 6 | 164.5 | 167.1 | yes |
| 7 | 133.2 | 139.0 | yes |
| 8 | 231.0 | 235.1 | yes |
| 9 | 212.0 | 214.4 | yes |
| 10 | 139.4 | 142.2 | yes |

### Criterion 3 — `/stats` against the rows

```json
{
  "n": 43,
  "lines": 43,
  "p50": 177.6,
  "p50_recomputed": 177.6,
  "p95": 12999.8,
  "p95_recomputed": 12999.8,
  "ok": true
}
```

### Criteria 4 and 5 — independent starts

```json
[
  {
    "ts": "2026-11-18T08:59:46",
    "import_ms": 425.5,
    "first_ms": 11187.6,
    "total_ms": 11613.1,
    "status": 200,
    "health_ok": true,
    "lines_in_this_copy": 1,
    "warm_on_import": "0"
  },
  {
    "ts": "2026-11-18T08:59:59",
    "import_ms": 408.1,
    "first_ms": 11273.3,
    "total_ms": 11681.3,
    "status": 200,
    "health_ok": true,
    "lines_in_this_copy": 2,
    "warm_on_import": "0"
  },
  {
    "ts": "2026-11-18T09:00:13",
    "import_ms": 424.9,
    "first_ms": 12396.9,
    "total_ms": 12821.9,
    "status": 200,
    "health_ok": true,
    "lines_in_this_copy": 3,
    "warm_on_import": "0"
  }
]
```

### Ten records from the log

```text
{"ts": "2026-11-18T01:00:48.575+00:00", "request_id": "6e0a74ed-2137-444e-ba9c-a7fe0e0700e1", "creator_id": "capbefore3_t0", "event": "decided", "status": 200, "input_sha256": "b9417d3d85ae2fac", "input_chars": 365, "input_preview": "As a fan of How It Works, I have a deep interest in astronomy. I first encounter", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.6349, "style_score": 0.2852, "t_total_ms": 125.6, "t_model_ms": 111.6, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 984.4, "reason": null}
{"ts": "2026-11-18T01:00:48.783+00:00", "request_id": "af8c65d3-e7b9-4e76-9c1d-667e0b629f35", "creator_id": "capbefore3_t1", "event": "decided", "status": 200, "input_sha256": "e17ceacd8bd5d70d", "input_chars": 712, "input_preview": "Music is a miracle, it is the root and soul of my life. I found music a second l", "output_guess": "unsure", "output_confidence": 0.4268, "model_score": 0.3466, "style_score": 0.547, "t_total_ms": 196.5, "t_model_ms": 179.7, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1437.5, "reason": null}
{"ts": "2026-11-18T01:00:48.903+00:00", "request_id": "0dc970f0-e453-4bbf-9e12-0cdbda31bfa6", "creator_id": "capbefore3_t0", "event": "decided", "status": 200, "input_sha256": "54b831aff4d0c8d7", "input_chars": 241, "input_preview": "I conducted several independent research studies including attention economy and", "output_guess": "unsure", "output_confidence": 0.4592, "model_score": 0.1556, "style_score": 0.9145, "t_total_ms": 108.8, "t_model_ms": 96.2, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 812.5, "reason": null}
{"ts": "2026-11-18T01:00:49.036+00:00", "request_id": "32b8891c-0bea-4742-8d5b-5cb8e516dd3c", "creator_id": "capbefore3_t1", "event": "decided", "status": 200, "input_sha256": "613ff153a0b26853", "input_chars": 304, "input_preview": "“Know Thyself” to me means embracing complexity: being both scientist and artist", "output_guess": "human", "output_confidence": 0.2822, "model_score": 0.2709, "style_score": 0.2991, "t_total_ms": 118.9, "t_model_ms": 104.0, "t_style_ms": 0.4, "t_load_ms": 0.0, "cpu_ms": 984.4, "reason": null}
{"ts": "2026-11-18T01:00:49.244+00:00", "request_id": "64f06e6b-3460-4ed2-a3e6-9974bba0cfb9", "creator_id": "capbefore3_t0", "event": "decided", "status": 200, "input_sha256": "7d62aaaaa91259e5", "input_chars": 635, "input_preview": "“Odors have a power of persuasion stronger than that of words, appearances, emot", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.594, "style_score": 0.2801, "t_total_ms": 198.8, "t_model_ms": 185.5, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1609.4, "reason": null}
{"ts": "2026-11-18T01:00:49.412+00:00", "request_id": "7bf8c2fc-9391-437d-8bfc-c399a60e7c0a", "creator_id": "capbefore3_t1", "event": "decided", "status": 200, "input_sha256": "2a10eaa04390438e", "input_chars": 427, "input_preview": "“And, following my “perfume atlas,” people, too, seemed to carry notes. I once s", "output_guess": "human", "output_confidence": 0.1917, "model_score": 0.2641, "style_score": 0.0831, "t_total_ms": 158.5, "t_model_ms": 144.6, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1234.4, "reason": null}
{"ts": "2026-11-18T01:00:49.556+00:00", "request_id": "b21ce6b4-139c-41f1-a7ea-4a389123408e", "creator_id": "capbefore3_t0", "event": "decided", "status": 200, "input_sha256": "d073e3ee0c3c146a", "input_chars": 328, "input_preview": "”And so the opening sentence returns to me with a different weight. “Odors have ", "output_guess": "human", "output_confidence": 0.2345, "model_score": 0.2033, "style_score": 0.2812, "t_total_ms": 132.2, "t_model_ms": 120.1, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1093.8, "reason": null}
{"ts": "2026-11-18T01:00:49.769+00:00", "request_id": "fc1ca42c-df01-41e5-8fdf-146f321be564", "creator_id": "capbefore3_t1", "event": "decided", "status": 200, "input_sha256": "e88773c747dd6f55", "input_chars": 767, "input_preview": "At Columbia, through the lens of both STEM and humanity, I’ll be able to explore", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.3678, "style_score": 0.4269, "t_total_ms": 202.8, "t_model_ms": 185.7, "t_style_ms": 0.4, "t_load_ms": 0.0, "cpu_ms": 1609.4, "reason": null}
{"ts": "2026-11-18T01:00:49.972+00:00", "request_id": "3103c3c3-b74c-4657-86be-6ad51b85ec14", "creator_id": "capbefore3_t0", "event": "decided", "status": 200, "input_sha256": "d6255b91530413ea", "input_chars": 710, "input_preview": "Apart from academics, the Twin Cities offers a world of creative exploration. I ", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.5625, "style_score": 0.1206, "t_total_ms": 192.1, "t_model_ms": 177.9, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1578.1, "reason": null}
{"ts": "2026-11-18T01:00:50.108+00:00", "request_id": "cf7125cf-a391-41f3-8982-8f1e39c4eab8", "creator_id": "capbefore3_t1", "event": "decided", "status": 200, "input_sha256": "8bd97a84ac20cc7a", "input_chars": 344, "input_preview": "He told me that one of my piano arrangements had kept him company during the low", "output_guess": "unsure", "output_confidence": 0.6076, "model_score": 0.6178, "style_score": 0.5922, "t_total_ms": 124.0, "t_model_ms": 108.9, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 984.4, "reason": null}
```
