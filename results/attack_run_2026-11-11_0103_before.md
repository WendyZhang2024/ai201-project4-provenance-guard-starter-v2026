# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-11 01:03
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `66d5f1c3-1ea9-4b7e-baa1-8c4a3f501ed0` | unsure | 0.415 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `fa5b0ddd-cc35-47cf-96f5-b322027bf7ed` | human | 0.300 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `5a7ea713-1ebe-4275-9a4c-47df1422226e` | unsure | 0.652 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `99858474-0802-403e-a786-f361dcb94f5c` | unsure | 0.680 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `7aedeea2-c1b2-4a30-8c0b-b3b36a0d0df2` | human | 0.300 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `fe717455-b66f-4a04-a2e3-3abc6d8a0cf3` | human | 0.300 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c903aaf6-0ada-4d88-8df5-ad5bcb66a1c7` | human | 0.300 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `a2f6cdc2-9d61-4c2f-a81a-6da2e93fa79d` | unsure | 0.476 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `fbed79be-ab74-4a67-8e4d-0dafaa213f37` | unsure | 0.650 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `6f43174a-33ba-44b7-bcd0-b73ea9e1664f` | ai | 0.889 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `a4066fc2-2feb-4e62-bec9-709e8b136a85` | unsure | 0.631 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c225865f-aadb-4263-a6be-e488d872a59d` | unsure | 0.769 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `8ba12104-edd6-4ec0-8031-46c19df17fc8` | ai | 0.801 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `498318b6-8d77-4901-8ca0-86c325022ea8` | unsure | 0.796 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `d3337434-65d5-4e24-a0e4-1c7043d9b2df` | unsure | 0.782 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | `8e9eb30e-efd3-4e03-91e1-9e764700b4a9` | ai | 0.800 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `9b616c86-6028-45be-afa0-86e93465ea47` | unsure | 0.718 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `ff9583d3-a2c0-46d7-bb2d-ddb7d2b57a37` | unsure | 0.485 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `34abd5ce-16b9-45b4-a2f3-7e80b5cc4537` | unsure | 0.512 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `41cdafb0-39dd-4a8c-b7fe-ce332dc3b49a` | human | 0.326 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `f2993596-0b41-429c-8238-40de3521235b` | unsure | 0.646 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `4ec376d1-aea5-49ac-9b21-fe48a8973993` | unsure | 0.551 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `b79f29f4-a748-465a-bb6e-4fb792bbfb49` | human | 0.300 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `8fb1ffac-a0d4-40ad-8ce0-543bd0d6a414` | unsure | 0.601 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `0bb1fdbf-a65d-43b6-9dfa-7c2e88b82859` | human | 0.300 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `ab824bf0-0b09-4ecd-9986-b22fe10eceee` | human | 0.207 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `8952936d-16f9-41ac-bed9-0785a9226aa3` | ai | 0.899 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `c1071f28-9668-482a-a79f-71f917fe1d95` | ai | 0.800 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | `6353aea7-4336-4f9e-929f-1c7e4361f6a1` | ai | 0.800 | BROKE |
| MF08 | malformed | text is 60,000 characters | 200 | `90cae794-22e9-4632-a251-b58a70128606` | ai | 0.861 | BROKE |
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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `10cc53a2-5ca6-4ef9-b1fa-3f35e5a3310f` | human | 0.317 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d559ddd2-aa33-4dec-aacc-4fe9163ecbe3` | human | 0.317 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `329c20a6-7e8b-4cf4-8695-99f5225e738a` | human | 0.317 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e9e8a227-fcaf-4fba-badd-8077fc28724f` | human | 0.317 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ace1994e-b257-48f4-baa4-8c39dbef78d9` | human | 0.317 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `478ddda5-b27e-4f09-8331-7cf11c418c23` | human | 0.317 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f438ad03-d876-47f9-b515-7c09be257563` | human | 0.317 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e177f036-f04e-4581-a894-03cd4a4148fa` | human | 0.317 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2f2e26ad-531f-41e9-9c02-baafa9d6f324` | human | 0.317 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8d12a961-b8a7-4d3a-b620-2e8c67506575` | human | 0.317 | HELD |
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
  "content_id": "66d5f1c3-1ea9-4b7e-baa1-8c4a3f501ed0",
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
  "content_id": "fa5b0ddd-cc35-47cf-96f5-b322027bf7ed",
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
  "content_id": "5a7ea713-1ebe-4275-9a4c-47df1422226e",
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
  "content_id": "99858474-0802-403e-a786-f361dcb94f5c",
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
  "content_id": "7aedeea2-c1b2-4a30-8c0b-b3b36a0d0df2",
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
  "content_id": "fe717455-b66f-4a04-a2e3-3abc6d8a0cf3",
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
  "content_id": "c903aaf6-0ada-4d88-8df5-ad5bcb66a1c7",
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
  "content_id": "a2f6cdc2-9d61-4c2f-a81a-6da2e93fa79d",
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
  "content_id": "fbed79be-ab74-4a67-8e4d-0dafaa213f37",
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
  "content_id": "6f43174a-33ba-44b7-bcd0-b73ea9e1664f",
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
  "content_id": "a4066fc2-2feb-4e62-bec9-709e8b136a85",
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
  "content_id": "c225865f-aadb-4263-a6be-e488d872a59d",
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
  "content_id": "8ba12104-edd6-4ec0-8031-46c19df17fc8",
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
  "content_id": "498318b6-8d77-4901-8ca0-86c325022ea8",
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
  "content_id": "d3337434-65d5-4e24-a0e4-1c7043d9b2df",
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
  "content_id": "8e9eb30e-efd3-4e03-91e1-9e764700b4a9",
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
  "content_id": "9b616c86-6028-45be-afa0-86e93465ea47",
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
  "content_id": "ff9583d3-a2c0-46d7-bb2d-ddb7d2b57a37",
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
  "content_id": "34abd5ce-16b9-45b4-a2f3-7e80b5cc4537",
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
  "content_id": "41cdafb0-39dd-4a8c-b7fe-ce332dc3b49a",
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
  "content_id": "f2993596-0b41-429c-8238-40de3521235b",
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
  "content_id": "4ec376d1-aea5-49ac-9b21-fe48a8973993",
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
  "content_id": "b79f29f4-a748-465a-bb6e-4fb792bbfb49",
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
  "content_id": "8fb1ffac-a0d4-40ad-8ce0-543bd0d6a414",
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
  "content_id": "0bb1fdbf-a65d-43b6-9dfa-7c2e88b82859",
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
  "content_id": "ab824bf0-0b09-4ecd-9986-b22fe10eceee",
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
  "content_id": "8952936d-16f9-41ac-bed9-0785a9226aa3",
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
  "content_id": "c1071f28-9668-482a-a79f-71f917fe1d95",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.8,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
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
  "content_id": "6353aea7-4336-4f9e-929f-1c7e4361f6a1",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.8,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
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
  "content_id": "90cae794-22e9-4632-a251-b58a70128606",
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
  "content_id": "10cc53a2-5ca6-4ef9-b1fa-3f35e5a3310f",
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
  "content_id": "d559ddd2-aa33-4dec-aacc-4fe9163ecbe3",
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
  "content_id": "329c20a6-7e8b-4cf4-8695-99f5225e738a",
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
  "content_id": "e9e8a227-fcaf-4fba-badd-8077fc28724f",
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
  "content_id": "ace1994e-b257-48f4-baa4-8c39dbef78d9",
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
  "content_id": "478ddda5-b27e-4f09-8331-7cf11c418c23",
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
  "content_id": "f438ad03-d876-47f9-b515-7c09be257563",
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
  "content_id": "e177f036-f04e-4581-a894-03cd4a4148fa",
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
  "content_id": "2f2e26ad-531f-41e9-9c02-baafa9d6f324",
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
  "content_id": "8d12a961-b8a7-4d3a-b620-2e8c67506575",
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
