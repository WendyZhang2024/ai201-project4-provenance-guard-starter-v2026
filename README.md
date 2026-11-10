# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

A submission goes through seven steps:

1. **Request arrives.** `POST /submit` parses the JSON and takes `text` and `creator_id`. This adds the raw input and the identity of the submitter.
2. **Validation.** The service checks that `text` is present, non-empty, at most 100,000 characters, and long enough for the model (at least 3 tokens). This adds an accept/reject decision; bad input is stopped here, before any model runs. Only the first 400 tokens are scored, so most of a very long submission is never read by the model.
3. **Signal one — the model signal.** `detector.model_signal(text)` measures how predictable the text is to gpt2 and turns that into a 0–1 score. This adds `model_score`, where higher means more AI-like.
4. **Signal two — the style signal.** `stylometry.style_signal(text)` measures the shape of the text — sentence-length spread and punctuation density; vocabulary variety is measured but excluded after calibration — and turns it into a 0–1 score. This adds `style_score`, where higher means more AI-like.
5. **Combining.** `scoring.combine_signals(model_score, style_score)` combines the two scores into one `confidence` between 0 and 1. This adds the single number the labels are based on.
6. **Labelling.** `scoring.score_to_label(confidence)` maps the score to `guess` (`human`, `unsure`, or `ai`) and to the sentence a reader sees. This adds the human-readable decision.
7. **Audit and response.** `audit.log_decision(...)` appends one JSON object to `logs/audit.jsonl` with the timestamp, `content_id`, `creator_id`, both signal scores, the combined score, the label, and the status. The response returns the same `content_id` plus the scores and label. This adds the durable record and the ID that `/appeal` needs.

The important seam is step 5: everything above it produces numbers, everything below it depends on the single number it produces. If a label looks wrong, the cause is either a signal or the combining rule — not the label code alone.

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** How predictable the text is to gpt2, expressed as perplexity and squashed into a 0–1 score. Lower perplexity (more predictable text) produces a higher score, so higher means more AI-like.

**Why that might differ between human and AI writing:** A language model writes by repeatedly choosing a likely next token, so its output tends to be text the model finds easy to predict. Human writing is lumpier — odd word choices, abrupt turns, concrete details the model did not expect.

**What it can't see:** Predictability is not authorship. The signal rewards common words in short, ordinary sentences, which is exactly how many real people write: second-language writers, younger writers, and anyone writing plainly on purpose. Dense, ornate prose often goes the other way and reads as human, because rare words are what the model fails to predict. The signal also shifts with text length and topic, and it truncates at 400 tokens: anything after the first 400 tokens is invisible, so appending human-style text or hiding AI content later can evade it. gpt2 is also English-centric; text in other languages often has very high perplexity and is read as human, which is a direct bypass. The people most likely to be accused are the ones with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text rather than its meaning: sentence-length spread (standard deviation divided by the mean) and punctuation density (commas, semicolons, colons, and dashes per sentence). Vocabulary variety (unique words over total words) is also computed, but on the four calibration inputs it did not separate the texts — it sat at roughly 0.73–0.80 and was slightly higher for the AI sample — so it is reported but not included in the score. The two used measures are normalised and combined into a 0–1 score where higher means more AI-like.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and more uniform punctuation, because that is what choosing the most likely next word produces on average. Human writing is more uneven: a three-word sentence next to a forty-word one, and punctuation that varies with the writer.

**What it can't see:** It cannot read. It has no idea what the text says, so anything that changes the shape without changing the substance moves it: typos, sentence fragments, a pasted quotation, deliberate punctuation changes. That is cheap to do on purpose, and the attack set will do exactly that. Two further limits: vocabulary variety falls as text gets longer, which is one reason it was excluded from the score, and a one-sentence submission has no sentence-length spread at all; the code treats that spread component as neutral (0.5) rather than calling it AI.

### The combining rule

**The rule:** A weighted average of the two signal scores, plus two symmetric gates. Both signals point the same way — higher means more AI. When they disagree, the weighted average usually pulls toward the unsure band. The AI gate is the exception on the high side: when the model signal is at least `0.85` and the style signal is at least `0.50`, the score is lifted to the AI floor (`0.80`); on the long-AI calibration input, `model_score = 0.8810` and `style_score = 0.5603` average to `0.7527`, and the gate lifts it to `0.8000`. The human gate is the exception on the low side: when the model signal is at most `0.65` and the style signal is at most `0.45`, the score is capped at `0.30`, so the human label is reachable. The human gate does not fire for the plain weekend sample (`model_score = 0.8037`), so that false positive stays in unsure.

**The numbers:** weights `0.6 × model_score + 0.4 × style_score`; AI gate `model_score >= 0.85 and style_score >= 0.50` lifts to `0.80`; human gate `model_score <= 0.65 and style_score <= 0.45` caps at `0.30`; thresholds `HUMAN_THRESHOLD = 0.35`, `AI_THRESHOLD = 0.80`. Bands: human `0.00–0.35`, unsure `0.35–0.80`, AI `0.80–1.00`. These are four-input design choices, not a statistical calibration; Unit 8 tests them on more inputs.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:** On the formal-human calibration input, the model signal is `0.6349` — formal prose is predictable enough to look AI-ish — but the style signal is `0.2852`, because the sentences and punctuation look human. The weighted average would be `0.6 × 0.6349 + 0.4 × 0.2852 = 0.4950`, but the human gate sees both signals on the human side and caps the score at `0.30`, so the label is human. The rule does not force an AI label; when the signals disagree it reports uncertainty, and when both agree human it calls human.

**A limitation of the pair:** the two signals are not independent. Both reward plain, short, common-word writing, so a plain human writer can score high on both; the weighted average does not cancel that, and the gate can make it worse. The appeal path and the false-positive criterion are the mitigation, not the signals themselves.





---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00–0.35 | We think this was probably written by a person. |
| unsure | 0.35–0.80 | We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review. |
| high-confidence AI | 0.80–1.00 | We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review. |

**Boundary rule:** a score of `0.35` or below is human; a score of `0.80` or above is AI; only scores strictly between are unsure.  
**Reachability check (four M4 inputs):** human `0.30` from the clearly-human input (`model_score 0.5762`, `style_score 0.3801`, human gate); unsure `0.7622` from the weekend input (`0.8037`, `0.7000`); AI `0.8000` from the long-AI input (`0.8810`, `0.5603`, AI gate); the short-AI input reached `0.8048` (`0.8864`, `0.6823`). The long-AI input returned `guess: "ai"`. The 9-piece coverage set is the Unit 8 test.

**Why I worded the "unsure" one this way:** It puts the uncertainty on the system rather than the writer — “we couldn't make a confident call” — and gives the writer a next step: appeal and a human review. It does not say “we think you used AI.”



---

## Sample Run

**A submission**

```powershell
curl.exe -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" --data-raw '{"text": "I like my weekends. I do simple things: I play music. I cook. I watch shows. I do my work. I talk to my friends.", "creator_id": "demo_writer"}'
```

```json
{
  "content_id": "d50ec03c-7c67-4121-8a4b-cf2987139897",
  "guess": "unsure",
  "confidence": 0.7622,
  "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
  "model_score": 0.8037,
  "style_score": 0.7
}
```

The `style_score` of `0.7` is the average of the spread component (`0.4833`) and the punctuation component (`0.9167`), rounded to four decimals; it is not a fallback.

**An appeal**

```powershell
curl.exe -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" --data-raw '{"content_id": "d50ec03c-7c67-4121-8a4b-cf2987139897", "reasoning": "I wrote this myself. This is just how I write."}'
```

```json
{
  "ok": true,
  "content_id": "d50ec03c-7c67-4121-8a4b-cf2987139897",
  "status": "under_review",
  "appeal_count": 1,
  "message": "Thanks — a human will review this."
}
```

**What the log shows afterwards**

```powershell
curl.exe "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.7622,
      "content_id": "d50ec03c-7c67-4121-8a4b-cf2987139897",
      "creator_id": "demo_writer",
      "guess": "unsure",
      "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
      "model_score": 0.8037,
      "status": "decided",
      "style_score": 0.7,
      "timestamp": "2026-11-04T00:17:44+00:00"
    },
    {
      "content_id": "d50ec03c-7c67-4121-8a4b-cf2987139897",
      "creator_id": "demo_writer",
      "event": "appeal",
      "reasoning": "I wrote this myself. This is just how I write.",
      "status": "under_review",
      "timestamp": "2026-11-04T00:17:47+00:00"
    }
  ]
}
```

This query returns the two entries for this submission; the earlier test rows remain in `logs/audit.jsonl`. `confidence` in the response and `combined_score` in the audit log are the same number.

---

## How I Used AI

**Moment 1 — understanding the instructions**

- *What I asked for:* I asked an AI assistant to explain the project instructions. I was super confused by the two-unit structure and found it hard to start.
- *What came back:* A step-by-step breakdown of M1–M6, an explanation of the two signals and their blind spots, and the false-positive trade-off behind the thresholds.
- *What I changed:* I used it as a map, not an answer. I chose the 0.80 AI threshold, the 2/10 false-positive target, and the “unsure” label wording, and used those decisions to draft the M1 trace.

**Moment 2 — getting the model to load**

- *What I asked for:* `python detector.py` failed with `PermissionError` while creating `~/.cache/huggingface/models--gpt2`. I asked why, and whether the model could run without that cache.
- *What came back:* The diagnosis was a sandboxed shell that could not write outside the workspace, so the fix was a repo-local cache (`.hf-cache`) plus `HF_HOME`, with a `.gitignore` entry.
- *What I changed:* I ran the commands with the assistant's guidance, confirmed `detector.py` produced a score, and kept the cache out of git.

**Moment 3 — testing the false-positive number**

- *What I asked for:* I asked Claude to write the message a real writer would send if they were one of the people my 2/10 rate allows.
- *What came back:* A letter from a hypothetical plain-writing essayist whose own work was labeled high-confidence AI; they offered drafts, timestamps and notes, and asked how to appeal and whether the piece stays marked.
- *What I changed:* I kept the 2/10 target, but rewrote the criterion's reason to name the cost: two of my ten pieces would produce that letter. The 2/10 is a target, not a measured rate; Unit 8 measures it. I also noted for M5 that the AI label should tell the writer how to appeal.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 per minute, 200 per day

**Why those numbers and not others:**
Two callers have to be liveable at once. A real writer revising their own work
bursts three to five submissions in a minute and makes ten to thirty in a heavy
day, so 10 a minute leaves about twice their burst and 200 a day leaves six
times their day. A script mapping the 0.35 / 0.80 boundary needs hundreds of
samples: at 10 a minute it needs half an hour per hundred, and 200 a day gives
it a fifth of what it needs before it is shut out for the rest of the day. The
daily cap is also the cost ceiling, since every `/submit` runs gpt2 on this
laptop — 200 model calls a day per caller is affordable, thousands are not.

The trade is chosen, not hidden: the limit leans loose enough that a script gets
slightly more boundary information, because the other failure is worse. A 429
mid-revision costs that writer the submission itself, and this project exists
because a wrong accusation costs the person on the other end more than a missed
detection costs the site.

Two limits on the numbers. The flood below proves the per-minute limit; the
daily one is reasoned from those two load profiles, not measured, because
proving it would take 200 timed submissions. And the storage is `memory://`, so
a restart forgets every count and two copies of the service would not share
limits. That is right for one laptop and wrong for anything real.

**What a caller counts as:** `creator_id` when the body carries a non-empty
string, otherwise the caller's address (`app.py::rate_limit_key`). The two keys
fail differently, which is why the hybrid is worth naming:

- Per address alone counts one household, dorm or classroom as one caller, and
  it would also have blocked my own `run_eval.py`, which sends thirty-odd
  submissions in about a minute from one machine.
- Per creator alone is free to evade: a script that changes `creator_id` on
  every request looks like a thousand different writers.
- The fallback is the seam. A body that is not JSON (`Content-Type:
  text/plain`, say) carries no usable `creator_id`, so it lands in the address
  bucket. And every row of the attack set submits as `attacker_<id>`, so a full
  attack run never trips the limiter; only the `flood_same_creator` family does.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15`, fifteen submissions as `flood_tester`:

```text
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

Ten got through and five were rejected. `run_attacks.py::run_flood` wrote the
same run to `results/flood_2026-11-05_1044.md`.

The rejections are in the log, which is the point — an attack visible only as an
absence is one nobody finds:

```json
{"creator_id": "flood_tester", "event": "rejected", "limit": "10 per 1 minute", "reason": "rate_limited", "status": "rejected", "timestamp": "2026-11-05T02:44:12+00:00"}
```

And three ordinary submissions afterwards, read back with `GET /log`. The first
one is reconstructible from the entry alone: `0.6 × 0.4154 + 0.4 × 0.3527 =
0.3903`, the human gate caps it at `0.30` because both signals sit on the human
side (`model_score ≤ 0.65`, `style_score ≤ 0.45`), and `0.30 ≤ 0.35` is the
`human` label. The other two in that batch came back `ai` at `0.8000` and
`0.8048`.

```json
{"combined_score": 0.3, "content_id": "cd0699a0-12a2-4ee7-875e-5d8f03dffdc4", "creator_id": "log_check_1", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.4154, "status": "decided", "style_score": 0.3527, "timestamp": "2026-11-05T02:44:24+00:00"}
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

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

**How I marked it:** an evasion is BROKE when the label is not `ai`; a
false_positive is BROKE when the label is `ai`; a prompt injection is BROKE
only if the instruction changed the label text or the log; a malformed request
is BROKE on a 5xx, an HTML error page, a 200 `ai` on non-prose, or a 200 that
accepts input the route should have rejected (control characters,
punctuation-only); the flood family is HELD if any row got a 429.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
{"timestamp": "2026-11-10T17:03:17+00:00", "content_id": "66d5f1c3-1ea9-4b7e-baa1-8c4a3f501ed0", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.7924, "combined_score": 0.4151, "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:18+00:00", "content_id": "fa5b0ddd-cc35-47cf-96f5-b322027bf7ed", "creator_id": "attacker_EV02", "guess": "human", "model_score": 0.5943, "style_score": 0.4423, "combined_score": 0.3, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:19+00:00", "content_id": "fbed79be-ab74-4a67-8e4d-0dafaa213f37", "creator_id": "attacker_EV09", "guess": "unsure", "model_score": 0.7042, "style_score": 0.5689, "combined_score": 0.6501, "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:20+00:00", "content_id": "8ba12104-edd6-4ec0-8031-46c19df17fc8", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.7949, "combined_score": 0.801, "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:20+00:00", "content_id": "8e9eb30e-efd3-4e03-91e1-9e764700b4a9", "creator_id": "attacker_FP06", "guess": "ai", "model_score": 0.8814, "style_score": 0.6339, "combined_score": 0.8, "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:22+00:00", "content_id": "8952936d-16f9-41ac-bed9-0785a9226aa3", "creator_id": "attacker_MF05", "guess": "ai", "model_score": 0.9976, "style_score": 0.75, "combined_score": 0.8986, "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:23+00:00", "content_id": "c1071f28-9668-482a-a79f-71f917fe1d95", "creator_id": "attacker_MF06", "guess": "ai", "model_score": 0.9969, "style_score": 0.5, "combined_score": 0.8, "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:23+00:00", "content_id": "6353aea7-4336-4f9e-929f-1c7e4361f6a1", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 0.5, "combined_score": 0.8, "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:23+00:00", "content_id": "90cae794-22e9-4632-a251-b58a70128606", "creator_id": "attacker_MF08", "guess": "ai", "model_score": 0.9876, "style_score": 0.6699, "combined_score": 0.8605, "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.", "status": "decided"}
{"timestamp": "2026-11-10T17:03:24+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "10 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

The worst outcome was **FP03**: a piece of careful non-native English writing.
The service returned `guess = "ai"`, `confidence = 0.801`, with
`model_score = 0.8051` and `style_score = 0.7949`. This is the worst because
the writer did nothing wrong: the care that makes the prose clear — plain
vocabulary and even sentences — is exactly what the detector reads as
AI-assisted. The only way to look more human to this system is to write
worse, so the accusation punishes the writer for the skill it claims to
reward.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | ≤ 2 of 10 labeled high-confidence AI, each trial | 0/10 | 0/10 | 0/10 | **MET** |
| 2. score spread | ≥ 3 of 4 pairs: AI ≥ 0.80 and human ≤ 0.35, each trial | 2/4 | 2/4 | 2/4 | **MISSED** |
| 3. label coverage | all three labels appear in the 9-piece set, each trial | 3/3 | 3/3 | 3/3 | **MET** |
| 4. appeal path | valid 200 + under_review + count; empty 400; unknown/mismatch 404 | 4/4 | 4/4 | 4/4 | **MET** |
| 5. bad input | 400/400/413/400/400, no 500, rejection logged | 5/5 | 5/5 | 5/5 | **MET** |

**Real output from one trial**, pasted as text, naming the file and function
that produced it. Criteria 1, 2, 3 and 5 come from
`results/run_2026-11-11_0238_before.md`, produced by `run_eval.py::write_report`
from `scenarios.py::SCENARIOS`. Criterion 4 comes from the direct `/appeal`
calls against `app.py::appeal`.

**Criterion 1 — my own writing, trial 1**

```json
[
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.6349,
    "style_score": 0.2852,
    "label": "We think this was probably written by a person.",
    "sent": "As a fan of How It Works, I have a deep interest in astronomy. I first"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4268,
    "model_score": 0.3466,
    "style_score": 0.547,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Music is a miracle, it is the root and soul of my life. I found music "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4592,
    "model_score": 0.1556,
    "style_score": 0.9145,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "I conducted several independent research studies including attention e"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2822,
    "model_score": 0.2709,
    "style_score": 0.2991,
    "label": "We think this was probably written by a person.",
    "sent": "“Know Thyself” to me means embracing complexity: being both scientist "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.594,
    "style_score": 0.2801,
    "label": "We think this was probably written by a person.",
    "sent": "“Odors have a power of persuasion stronger than that of words, appeara"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1917,
    "model_score": 0.2641,
    "style_score": 0.0831,
    "label": "We think this was probably written by a person.",
    "sent": "“And, following my “perfume atlas,” people, too, seemed to carry notes"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2345,
    "model_score": 0.2033,
    "style_score": 0.2812,
    "label": "We think this was probably written by a person.",
    "sent": "”And so the opening sentence returns to me with a different weight. “O"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.3678,
    "style_score": 0.4269,
    "label": "We think this was probably written by a person.",
    "sent": "At Columbia, through the lens of both STEM and humanity, I’ll be able "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.5625,
    "style_score": 0.1206,
    "label": "We think this was probably written by a person.",
    "sent": "Apart from academics, the Twin Cities offers a world of creative explo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6076,
    "model_score": 0.6178,
    "style_score": 0.5922,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "He told me that one of my piano arrangements had kept him company duri"
  }
]
```

**Criterion 2 — score spread, trial 1** (pairs are texts 1–2, 3–4, 5–6, 7–8)

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8048,
    "model_score": 0.8864,
    "style_score": 0.6823,
    "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
    "sent": "The implementation of the proposed framework requires careful consider"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.6349,
    "style_score": 0.2852,
    "label": "We think this was probably written by a person.",
    "sent": "As a fan of How It Works, I have a deep interest in astronomy. I first"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8,
    "model_score": 0.881,
    "style_score": 0.5603,
    "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Artificial intelligence has become an important part of modern life. I"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.594,
    "style_score": 0.2801,
    "label": "We think this was probably written by a person.",
    "sent": "“Odors have a power of persuasion stronger than that of words, appeara"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6712,
    "model_score": 0.7499,
    "style_score": 0.5532,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Effective communication is essential in today's fast-paced world. It h"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4268,
    "model_score": 0.3466,
    "style_score": 0.547,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Music is a miracle, it is the root and soul of my life. I found music "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6746,
    "model_score": 0.8532,
    "style_score": 0.4066,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "The future of technology depends on responsible innovation. Companies "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.3678,
    "style_score": 0.4269,
    "label": "We think this was probably written by a person.",
    "sent": "At Columbia, through the lens of both STEM and humanity, I’ll be able "
  }
]
```

**Criterion 3 — label coverage, trial 1**

```json
[
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.6349,
    "style_score": 0.2852,
    "label": "We think this was probably written by a person.",
    "sent": "As a fan of How It Works, I have a deep interest in astronomy. I first"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3,
    "model_score": 0.594,
    "style_score": 0.2801,
    "label": "We think this was probably written by a person.",
    "sent": "“Odors have a power of persuasion stronger than that of words, appeara"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4268,
    "model_score": 0.3466,
    "style_score": 0.547,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Music is a miracle, it is the root and soul of my life. I found music "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.7622,
    "model_score": 0.8037,
    "style_score": 0.7,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "I like my weekends. I do simple things: I play music. I cook. I watch "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6969,
    "model_score": 0.7912,
    "style_score": 0.5555,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "The implementation of the proposed framework requires careful consider"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6988,
    "model_score": 0.77,
    "style_score": 0.592,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Artificial intelligence is now a normal part of daily life. It is used"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8048,
    "model_score": 0.8864,
    "style_score": 0.6823,
    "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
    "sent": "The implementation of the proposed framework requires careful consider"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8,
    "model_score": 0.881,
    "style_score": 0.5603,
    "label": "We think this was probably generated with AI. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Artificial intelligence has become an important part of modern life. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6712,
    "model_score": 0.7499,
    "style_score": 0.5532,
    "label": "We couldn't make a confident call on this piece. If this is your own work, you can appeal and ask for a human review.",
    "sent": "Effective communication is essential in today's fast-paced world. It h"
  }
]
```

**Criterion 4 — appeal path, trial 1**

```json
[
  {
    "check": "valid appeal",
    "status": 200,
    "body": {
      "appeal_count": 1,
      "content_id": "dd56910d-6941-424f-83e7-f5875ac5f446",
      "message": "Thanks — a human will review this.",
      "ok": true,
      "status": "under_review"
    }
  },
  {
    "check": "empty reasoning",
    "status": 400,
    "body": {
      "error": "bad_request",
      "message": "reasoning is required and must be a non-empty string."
    }
  },
  {
    "check": "unknown content_id",
    "status": 404,
    "body": {
      "error": "not_found",
      "message": "No matching submission."
    }
  },
  {
    "check": "mismatched creator_id",
    "status": 404,
    "body": {
      "error": "not_found",
      "message": "No matching submission."
    }
  }
]
```

**Criterion 5 — bad input, trial 1**

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 413,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "word word word word word word word word word word word word word word "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": null, \"creator_id\": \"eval_bad_null\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "hi"
  }
]
```


**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
