# M1 design record — Provenance Guard

Status: draft for review before the first commit.

This is the Milestone 1 trace, not the final README. The polished path and
signal descriptions live in `README.md`; this file keeps the full design,
including the false-positive case and the endpoint contracts.

---

## 1. Seven-step path

| # | What it passes through | What it adds | If this step breaks |
|---|---|---|---|
| 1 | `POST /submit` parses the JSON | `text` and `creator_id` | Invalid JSON → 400 |
| 2 | Validation: present, non-empty, under the size limit | An accept/reject decision | Empty or oversized text → 400/413; no validation → 500 |
| 3 | `detector.model_signal(text)` | `model_score` (0–1, higher = more AI) | Model not loaded or text too short → error |
| 4 | `stylometry.style_signal(text)` | `style_score` (0–1, higher = more AI) | One-sentence text has no spread → needs a decision |
| 5 | `scoring.combine_signals(model_score, style_score)` | `confidence` (0–1) | A signal running backwards or wrong weights → distorted score |
| 6 | `scoring.score_to_label(confidence)` | `guess` (`human`/`unsure`/`ai`) + label text | A gap in the ranges → one label is unreachable |
| 7 | `audit.log_decision(...)` + response | `content_id` + a durable audit row | No log or no `content_id` → the appeal path breaks |

One-paragraph version:

> Someone POSTs a piece of text and a `creator_id`. The service checks that
> the text is scoreable. Signal one measures how predictable the text is to
> gpt2. Signal two measures the shape of the text. The two scores are combined
> into one `confidence`. That number is mapped to a `guess` and to a sentence a
> reader sees. The decision is appended to `logs/audit.jsonl`, and the response
> returns the `content_id`, both signal scores, the combined score and the
> label.

The important seam is step 5. Everything above it produces numbers; everything
below it depends on the one number it produces. If a label looks wrong, the
cause is a signal or the combining rule, not the label code alone.

---

## 2. Two signals

| | Signal one — model | Signal two — style |
|---|---|---|
| File | `detector.py` (given) | `stylometry.py` (to build) |
| Measures | Predictability: gpt2 perplexity, squashed to 0–1 | Shape: sentence-length spread, vocabulary variety, punctuation density |
| Direction | Lower perplexity → higher AI score | Low spread / narrow variety / uniform punctuation → higher AI score |
| Why human and AI differ | A model picks likely next tokens, so its text is more predictable; human writing is lumpier | Generated prose tends toward even, mid-length sentences and a narrower vocabulary band |
| Blind spot | Predictability is not authorship: plain, common-word writing (second-language writers, younger writers, deliberate plain style) is flagged; ornate prose can read as human | It cannot read: typos, fragments, quotations and punctuation changes move it without changing the substance; vocabulary variety also falls with length, and one sentence has no spread |

### Signal one, in detail

- What it measures: how predictable the text is to gpt2. The raw number is
  perplexity; `detector.model_signal` squashes it onto 0–1 with a logistic
  curve (midpoint around 45, steepness 1.6), so lower perplexity gives a higher
  AI score. The text is truncated to 400 tokens, and fewer than 3 tokens
  raises an error.
- Why human and AI differ: a language model writes by repeatedly choosing a
  likely next token. Its output tends to be text the model finds easy to
  predict. Human writing wanders: odd word choices, abrupt turns, concrete
  details the model did not expect.
- What it cannot see: predictability is not authorship. The signal rewards
  common words in short, ordinary sentences, which is exactly how many real
  people write. Second-language writers, younger writers, and anyone writing
  plainly on purpose are measured as machine-like. Dense, ornate prose often
  goes the other way and reads as human, because rare words are what the model
  fails to predict. Length and topic also move the score, and the 400-token
  truncation can change it. The people most likely to be accused are the ones
  with the least room to argue back.

### Signal two, in detail

- What it measures: the shape of the text, not its meaning.
  - Sentence-length spread: standard deviation divided by the mean. Low spread
    means the sentences march in step, which is more AI-like.
  - Vocabulary variety: unique words over total words. Higher variety is more
    human-like, but the measure falls as text gets longer.
  - Punctuation density: punctuation per length. Commas, semicolons and dashes
    are more informative than full stops because they vary more between
    writers.
- Why human and AI differ: generated prose tends toward even, mid-length
  sentences and a narrower vocabulary band, because that is what choosing the
  most likely next word produces on average. Human writing is more uneven: a
  three-word sentence next to a forty-word one, more repetition in some places
  and more variety in others.
- What it cannot see: it cannot read. It has no idea what the text says, so
  anything that changes the shape without changing the substance moves it:
  typos, sentence fragments, a pasted quotation, deliberate punctuation
  changes. That is cheap to do on purpose. Two further limits: vocabulary
  variety falls with length, so texts of different lengths are not directly
  comparable, and a one-sentence submission has no sentence-length spread at
  all.
- Combining the three measures: their directions and scales differ. Low
  sentence spread is AI-like; high vocabulary variety is human-like;
  punctuation density depends on what you count. Each measure has to be
  normalised and direction-aligned before they are combined, and the resulting
  `style_signal` must be 0–1 with higher meaning more AI-like, so it can be
  combined directly with `model_score`.

The two signals must measure different things. "Two versions of the same idea
count as one." One reads predictability; the other reads surface shape. If both
were word-frequency variants, the project would only have one signal.

---

## 3. Calibration: true negative (my smell paragraph) and false positive (plain weekend sample)

### True negative: my smell paragraph

This paragraph is my own writing:

> “Odors have a power of persuasion stronger than that of words, appearances,
> emotions, or will…” I lost almost all my sense of smell after a childhood
> illness, and yet this line always rings in my mind. When I was very young, I
> suffered a serious illness and underwent surgery that left me with almost no
> sense of smell. The only scent I could detect was perfume – something I
> discovered by accident one day while walking past my mother’s dresser. At
> first, the loss felt like a void, a nightmare that I could no longer
> experience the world in the same way as others. Yet what seemed like an
> absence soon became a new kind of compass.

Measured with the real detector on 2026-11-04:

- `perplexity = 37.1`
- `model_score = 0.5762`
- `style_score`: not implemented yet; to be measured in Milestone 4.

This is a **true negative / unsure** case, not a false positive. Even a style
score of 1.0 would give `0.5 × 0.5762 + 0.5 × 1.0 = 0.788`, still below the
0.80 threshold, so this text cannot be labelled AI under the current design.
That is the correct outcome: the writing is personal and specific, and the
model signal reads it as more human, not more AI. The opening line is a
quotation; the rest is my own narrative.

### False positive: a deliberately plain weekend sample

This is a **constructed plain sample**, not my natural writing. It is a
deliberately simple rewrite of my weekend paragraph, produced with AI help, so
it is weaker than the true-negative case above for the brief's "real writer"
requirement. It is still useful for the design because it shows the mechanism
that produces a false positive.

The sample:

> "I like my weekends. I do simple things: I play music. I cook. I watch shows.
> I do my work. I talk to my friends."

Measured with the real detector on 2026-11-04:

- `perplexity = 18.6`
- `model_score = 0.8037`
- `style_score`: not implemented yet; to be measured in Milestone 4.

Six short sentences. A five-sentence version scored 0.7289, below 0.80; this
one is just above at 0.8037. The margin is thin: the model signal alone is above
0.80, and with equal weights the combined score crosses 0.80 only if the style
score is at least `2 × 0.80 − 0.8037 = 0.7963`. A text this list-like and
repetitive is likely to score high on the style signal, but that is a Milestone
4 measurement, not an assumption. For the trace below, the style score is
illustrative.

The writer sees:

```json
{
  "content_id": "b7e2c1a4-...",
  "guess": "ai",
  "confidence": 0.81,
  "label": "We think this was probably generated with AI.",
  "model_score": 0.8037,
  "style_score": 0.81
}
```

The writer appeals:

```json
POST /appeal
{"content_id": "b7e2c1a4-...", "reasoning": "I wrote this myself. This is just how I write."}
```

The service returns:

```json
{
  "ok": true,
  "content_id": "b7e2c1a4-...",
  "status": "under_review",
  "appeal_count": 1,
  "message": "Thanks — a human will review this."
}
```

The log afterwards:

```json
{"timestamp":"...","content_id":"b7e2c1a4-...","creator_id":"weekend_writer","guess":"ai","model_score":0.8037,"style_score":0.81,"combined_score":0.81,"label":"We think this was probably generated with AI.","status":"decided"}
{"timestamp":"...","content_id":"b7e2c1a4-...","creator_id":"weekend_writer","event":"appeal","status":"under_review","reasoning":"I wrote this myself. This is just how I write."}
```

The case matters because both signals can be wrong in the same direction. Plain
writing is both predictable and uniform, so the average does not save the
writer. Raising the AI threshold moves the line but does not remove the
problem. The appeal is the only remedy for the people who fall on the wrong
side of the line.

This is also the case the false-positive criterion has to measure. The working
target from the design discussion is "at most 2 of 10 pieces I wrote myself are
labelled high-confidence AI", with a reason specific to plain writing and the
model signal. The number and the reason belong in `criteria.md` (Milestone 2).

---

## 4. Endpoint contracts

### `POST /submit`

Request:

| Field | Type | Required | Constraint |
|---|---|---|---|
| `text` | string | yes | 1–100,000 characters; empty or oversized is rejected |
| `creator_id` | string | yes | non-empty; opaque identifier |

`100,000` characters is a policy limit, not a model limit: the detector
truncates at 400 tokens, so larger text does not improve the score. The cap
bounds request size, memory and latency, and gives the client a clear `413`
case.

Success `200`:

```json
{
  "content_id": "string (UUID)",
  "guess": "human | unsure | ai",
  "confidence": 0.0,
  "label": "the full sentence a reader sees",
  "model_score": 0.0,
  "style_score": 0.0
}
```

Errors:

| Status | When | Body |
|---|---|---|
| `400` | missing `text`, empty `text`, invalid JSON | `{"error":"bad_request","message":"..."}` |
| `413` | `text` exceeds 100,000 characters | `{"error":"text_too_large","message":"..."}` |
| `500` | internal failure, for example the model cannot load | `{"error":"internal","message":"..."}` |

Notes:

- `guess` is machine-readable; `label` is the sentence a person sees. They must
  agree.
- `content_id` is the key `/appeal` uses. It must be present in the response
  and in the log.
- `model_score` and `style_score` must be in the response, not only in the
  log. The next unit's tools read them from the response.

### `POST /appeal`

Request:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `content_id` | string | yes | must exist in the audit log |
| `reasoning` | string | yes | non-empty; the writer's explanation |
| `creator_id` | string | no | if sent, it must match the original; if omitted, the service derives it from the log |

Success `200`:

```json
{
  "ok": true,
  "content_id": "string",
  "status": "under_review",
  "appeal_count": 1,
  "message": "Thanks — a human will review this."
}
```

Errors:

| Status | When | Body |
|---|---|---|
| `400` | missing `content_id` or `reasoning`, or empty `reasoning` | `{"error":"bad_request","message":"..."}` |
| `404` | `content_id` does not exist, or `creator_id` does not match | `{"error":"not_found","message":"No matching submission."}` |

Notes:

- The `404` is deliberately the same for "unknown id" and "wrong creator" so
  the endpoint does not reveal whether a `content_id` exists.
- A repeated appeal appends another `event=appeal` row. The status stays
  `under_review`, `appeal_count` increases, and the response is `200`. The log
  is append-only; the original decision is never overwritten.
- No automatic re-checking is required. The appeal changes the status and
  leaves a trace for a human.

---

## 5. Labels and thresholds

| Label | Score range | Text (draft; final wording in Milestone 5) |
|---|---|---|
| high-confidence human | `0.00–0.35` | "We think this was probably written by a person." |
| unsure | `0.35–0.80` | "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review." |
| high-confidence AI | `0.80–1.00` | "We think this was probably generated with AI." |

Configuration intent:

- `HUMAN_THRESHOLD = 0.35`
- `AI_THRESHOLD = 0.80`

The AI band is only 0.20 wide. If calibration in Milestone 4 shows that
clearly-AI text never reaches 0.80, the AI label is unreachable. The fix is
either a lower AI threshold or a different combining rule (for example, require
both signals to be high before calling AI), not a label-only change.

---

## 6. Read-back result

1. **Path** — Yes. Seven steps, each with what it adds; another person can draw
   the boxes.
2. **Signals** — Yes. Each signal has a property, a reason it differs, and a
   named blind spot.
3. **False positive** — Yes. The plain sample scores `0.8037`, gets the AI
   label, and has an appeal path.
4. **`/submit`** — Yes. `text` (string, 1–100,000 characters), `creator_id`
   (string, required); response fields and types are listed; 400/413/500 are
   defined.
5. **`/appeal`** — Yes. Required `content_id` + `reasoning`; optional
   `creator_id`; 400 for missing/empty; 404 for unknown id or wrong creator;
   repeated appeals append and increment `appeal_count`.
6. **Could another developer build a client?** — Yes. The fields, types,
   ranges and error codes are specified. The only open item is the exact label
   text, which is a Milestone 5 decision; the `label` field itself is defined as
   a full sentence.
7. **What remains ambiguous?** — The final label wording (M5) and the style
   signal's calibration (M4). Neither changes the request/response shape.

---

## 7. Open items

- **M1:** the false-positive sample is a constructed plain rewrite (AI-assisted),
  not my natural writing. It scores `0.8037`, just above 0.80. Replace it with a
  natural real sample if one becomes available. The true-negative case (my smell
  paragraph) is real and measured.
- **M2:** done — five criteria are in `criteria.md`; the false-positive target
  is 2/10, and the reason names the cost of two appeal letters per ten pieces.
- **M4:** calibrate the four inputs (clearly AI, clearly human, formal human,
  lightly-edited AI) and confirm the AI label is reachable at 0.80.
- **M5:** set `AI_THRESHOLD = 0.80` in `config.py` (it is still 0.65 in the
  starter) and re-check the README against the code.
- **M5:** finalise the three label texts.
- **M5:** implement `score_to_label`, the appeal endpoint, and update
  `notes/` if the design changes.
