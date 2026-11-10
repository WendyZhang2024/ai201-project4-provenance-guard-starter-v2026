# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-11 04:25
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `306bd539-4a6b-44b9-9111-10e76b1a66da` | unsure | 0.415 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `36ee12fe-d8ce-4f61-ad8f-d62d722a1253` | human | 0.300 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `2a7ad575-1ab4-4274-bd01-65f8e23c84dc` | unsure | 0.652 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `e4bcb6be-aea1-42eb-ab57-7fd319b1e798` | unsure | 0.680 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `fa59c3a7-c811-404c-9316-fc45210d9f05` | human | 0.300 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `ce8592b4-eb2b-4607-8269-542b93fa1fd5` | human | 0.300 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `123925fc-7b32-40ce-8fff-23c2c0fae36c` | human | 0.300 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `fd1974ba-1078-434b-a3aa-2fd1570608d3` | unsure | 0.476 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `26467ed4-63d5-4741-95b3-d065fbf86280` | unsure | 0.650 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `d852b5ae-dcd3-4a79-abf3-a631c53eb773` | ai | 0.889 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `ddb11559-94ae-4b0a-b4d6-dfe87141da24` | unsure | 0.631 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `002c6da8-e63d-49c5-a159-fd5533cda1d3` | unsure | 0.769 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `fdb3441c-a00d-42b7-9c27-ac7a958c3864` | ai | 0.801 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `f2ee7661-90cf-49c7-89bd-7f64e3f2962c` | unsure | 0.796 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `40de6e84-27e9-4ab1-aa29-c4345f4a5449` | unsure | 0.782 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | `399f56a4-ba23-4f2f-977a-aa80ae753367` | ai | 0.800 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `a086e48c-2ff5-419b-b89c-febccc549fb4` | unsure | 0.718 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `bc7b683c-ce61-4155-9907-6c42cdcb839f` | unsure | 0.485 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `f4ff27cc-b1e3-49f9-afb4-6daa3fd0b7f9` | unsure | 0.512 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `2cc4f316-2d8d-4581-b131-78734584f646` | human | 0.326 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `99a2c78d-b096-4c40-8ceb-27698d283e84` | unsure | 0.646 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `a809d78b-a1ca-440e-b6e7-4dde9c27d809` | unsure | 0.551 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `25985e47-5ffe-45c0-8216-7a723b1cadb8` | human | 0.300 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `97969ab9-971b-4f88-8321-f5b1f25c3780` | unsure | 0.601 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `48edd66f-4edf-47d8-9c12-e0283c710a8b` | human | 0.300 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `0d7df898-a110-4009-892c-ffa40f10eac5` | human | 0.207 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `34c99e7d-f4fe-4904-b1ce-50db6b19c3f4` | ai | 0.899 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `1a74b717-21b7-4c2f-803a-f55304c85f8c` | unsure | 0.798 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `abd27bc0-691a-4978-b079-ac4febfb3119` | unsure | 0.744 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `9b3021b0-50e8-46c8-b4fa-6356aec67a13` | ai | 0.861 | BROKE |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `39a9a983-4862-428d-af4e-be133e04f90f` | human | 0.317 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8cd03bdf-3209-4282-8317-02488a2b575e` | human | 0.317 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9554646e-1e5a-4363-b90c-27067a1909a4` | human | 0.317 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2e2295b3-fb37-4c21-a4f1-22b33d4307e4` | human | 0.317 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `770b2050-484a-4142-8b31-c28775e52746` | human | 0.317 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `083b5fa3-a905-4038-b35d-5d33d02b8ed5` | human | 0.317 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b1f51533-bb41-49bb-aaa2-6e540b42c662` | human | 0.317 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `66f76f12-3678-4533-9a87-8fd1687afdbc` | human | 0.317 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a4c4dd4c-fc36-4d54-89cf-9da395d9ca88` | human | 0.317 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `22af8c20-b965-48a2-85c0-3e531609d3e5` | human | 0.317 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "306bd539-4a6b-44b9-9111-10e76b1a66da",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.4151,
  "model_score": 0.1635,
  "style_score": 0.7924,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "36ee12fe-d8ce-4f61-ad8f-d62d722a1253",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.3,
  "model_score": 0.5943,
  "style_score": 0.4423,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "2a7ad575-1ab4-4274-bd01-65f8e23c84dc",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.6525,
  "model_score": 0.6662,
  "style_score": 0.632,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "e4bcb6be-aea1-42eb-ab57-7fd319b1e798",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6805,
  "model_score": 0.6114,
  "style_score": 0.7841,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "fa59c3a7-c811-404c-9316-fc45210d9f05",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3,
  "model_score": 0.3212,
  "style_score": 0.3994,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "ce8592b4-eb2b-4607-8269-542b93fa1fd5",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.3,
  "model_score": 0.5727,
  "style_score": 0.375,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "123925fc-7b32-40ce-8fff-23c2c0fae36c",
  "creator_id": "attacker_EV07",
  "guess": "human",
  "confidence": 0.3,
  "model_score": 0.5862,
  "style_score": 0.25,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "fd1974ba-1078-434b-a3aa-2fd1570608d3",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.4764,
  "model_score": 0.2452,
  "style_score": 0.8232,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "26467ed4-63d5-4741-95b3-d065fbf86280",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6501,
  "model_score": 0.7042,
  "style_score": 0.5689,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "d852b5ae-dcd3-4a79-abf3-a631c53eb773",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.889,
  "model_score": 0.9792,
  "style_score": 0.7538,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "ddb11559-94ae-4b0a-b4d6-dfe87141da24",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.6311,
  "model_score": 0.6175,
  "style_score": 0.6516,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "002c6da8-e63d-49c5-a159-fd5533cda1d3",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.7689,
  "model_score": 0.7387,
  "style_score": 0.8141,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "fdb3441c-a00d-42b7-9c27-ac7a958c3864",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.801,
  "model_score": 0.8051,
  "style_score": 0.7949,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "f2ee7661-90cf-49c7-89bd-7f64e3f2962c",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.7956,
  "model_score": 0.8329,
  "style_score": 0.7396,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "40de6e84-27e9-4ab1-aa29-c4345f4a5449",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.7825,
  "model_score": 0.8005,
  "style_score": 0.7555,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "399f56a4-ba23-4f2f-977a-aa80ae753367",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.8,
  "model_score": 0.8814,
  "style_score": 0.6339,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "a086e48c-2ff5-419b-b89c-febccc549fb4",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.7177,
  "model_score": 0.8816,
  "style_score": 0.4718,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "bc7b683c-ce61-4155-9907-6c42cdcb839f",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.4851,
  "model_score": 0.3223,
  "style_score": 0.7294,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "f4ff27cc-b1e3-49f9-afb4-6daa3fd0b7f9",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.5118,
  "model_score": 0.4625,
  "style_score": 0.5858,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "2cc4f316-2d8d-4581-b131-78734584f646",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.3264,
  "model_score": 0.2044,
  "style_score": 0.5093,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "99a2c78d-b096-4c40-8ceb-27698d283e84",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.6458,
  "model_score": 0.5943,
  "style_score": 0.7231,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "a809d78b-a1ca-440e-b6e7-4dde9c27d809",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.5507,
  "model_score": 0.4998,
  "style_score": 0.6271,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "25985e47-5ffe-45c0-8216-7a723b1cadb8",
  "creator_id": "attacker_PI05",
  "guess": "human",
  "confidence": 0.3,
  "model_score": 0.6401,
  "style_score": 0.2054,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "97969ab9-971b-4f88-8321-f5b1f25c3780",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.6014,
  "model_score": 0.5583,
  "style_score": 0.666,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "48edd66f-4edf-47d8-9c12-e0283c710a8b",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.3,
  "model_score": 0.0,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "0d7df898-a110-4009-892c-ffa40f10eac5",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.2067,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "34c99e7d-f4fe-4904-b1ce-50db6b19c3f4",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.8986,
  "model_score": 0.9976,
  "style_score": 0.75,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "1a74b717-21b7-4c2f-803a-f55304c85f8c",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.7981,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "abd27bc0-691a-4978-b079-ac4febfb3119",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.7438,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "9b3021b0-50e8-46c8-b4fa-6356aec67a13",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.8605,
  "model_score": 0.9876,
  "style_score": 0.6699,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "39a9a983-4862-428d-af4e-be133e04f90f",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "8cd03bdf-3209-4282-8317-02488a2b575e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "9554646e-1e5a-4363-b90c-27067a1909a4",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "2e2295b3-fb37-4c21-a4f1-22b33d4307e4",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "770b2050-484a-4142-8b31-c28775e52746",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "083b5fa3-a905-4038-b35d-5d33d02b8ed5",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "b1f51533-bb41-49bb-aaa2-6e540b42c662",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "66f76f12-3678-4533-9a87-8fd1687afdbc",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "a4c4dd4c-fc36-4d54-89cf-9da395d9ca88",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "22af8c20-b965-48a2-85c0-3e531609d3e5",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3172,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
