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

**What it can't see:** Predictability is not authorship. The signal rewards common words in short, ordinary sentences, which is exactly how many real people write: second-language writers, younger writers, and anyone writing plainly on purpose. Dense, ornate prose often goes the other way and reads as human, because rare words are what the model fails to predict. The signal also shifts with text length and topic, and it truncates at 400 tokens: anything after the first 400 tokens is invisible, so appending human-style text or hiding AI content later can evade it. gpt2 is also English-centric, so non-English and non-Latin text behaves unpredictably: in my attack run, Arabic (model 0.9064) and emoji-only text (0.9969) scored as very AI-like, not human. The people most likely to be accused are the ones with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text rather than its meaning: sentence-length spread (standard deviation divided by the mean) and punctuation density (commas, semicolons, colons, and dashes per sentence). Vocabulary variety (unique words over total words) is also computed, but on the four calibration inputs it did not separate the texts — it sat at roughly 0.73–0.80 and was slightly higher for the AI sample — so it is reported but not included in the score. The two used measures are normalised and combined into a 0–1 score where higher means more AI-like.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and more uniform punctuation, because that is what choosing the most likely next word produces on average. Human writing is more uneven: a three-word sentence next to a forty-word one, and punctuation that varies with the writer.

**What it can't see:** It cannot read. It has no idea what the text says, so anything that changes the shape without changing the substance moves it: typos, sentence fragments, a pasted quotation, deliberate punctuation changes. That is cheap to do on purpose, and the attack set will do exactly that. Two further limits: vocabulary variety falls as text gets longer, which is one reason it was excluded from the score, and a one-sentence submission has no sentence-length spread at all; the code treats that spread component as neutral (0.5) rather than calling it AI.

### The combining rule

**The rule:** A weighted average of the two signal scores, plus two symmetric gates. Both signals point the same way — higher means more AI. When they disagree, the weighted average usually pulls toward the unsure band. The AI gate is the exception on the high side: when the model signal is at least `0.85` and the style signal is above `0.50`, the score is lifted to the AI floor (`0.80`); on the long-AI calibration input, `model_score = 0.8810` and `style_score = 0.5603` average to `0.7527`, and the gate lifts it to `0.8000`. The human gate is the exception on the low side: when the model signal is at most `0.65` and the style signal is at most `0.45`, the score is capped at `0.30`, so the human label is reachable. The human gate does not fire for the plain weekend sample (`model_score = 0.8037`), so that false positive stays in unsure.

**The numbers:** weights `0.6 × model_score + 0.4 × style_score`; AI gate `model_score >= 0.85 and style_score > 0.50` lifts to `0.80`; human gate `model_score <= 0.65 and style_score <= 0.45` caps at `0.30`; thresholds `HUMAN_THRESHOLD = 0.35`, `AI_THRESHOLD = 0.80`. Bands: human `0.00–0.35`, unsure `0.35–0.80`, AI `0.80–1.00`. These are four-input design choices, not a statistical calibration; Unit 8 tests them on more inputs.

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

**Moment 4 — diagnosing the attack run**

- *What I asked for:* I gave it the 56-row table and the two signal scores and asked for three possible causes at different stages, without telling me which was most likely. I wanted hypotheses to test.
- *What came back:* Three candidates — signal one collapsing under surface noise, signal two being gamed by the edits, and the human gate turning moderate scores into `human`. The style-only explanation did not survive the numbers I computed: even at style 1.0, EV02/EV06/EV07 stay below 0.80, so signal one is the binding constraint.
- *What I changed:* I checked each candidate against `logs/audit.jsonl`, rejected the style-only explanation, and rewrote the diagnosis so the stage matches the binding cause; the gate is named as the amplifier, not the cause. I then chose the one measured change — the AI gate comparison `>=` to `>` — re-ran the attack set and the five criteria, and left the nine signal-one evasions in What's Still Broken.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 per minute, 200 per day

**Why those numbers and not others:**
Two callers have to be liveable at once. A real writer revising their own work
bursts three to five submissions in a minute and makes ten to thirty in a heavy
day, so 10 a minute leaves about twice their burst and 200 a day leaves six
times their day. A script mapping the 0.35 / 0.80 boundary needs hundreds of
samples: at 10 a minute that is ten minutes per hundred, and the 200-a-day cap
stops it after about twenty minutes of sending, well short of what it needs.
The daily cap is also the cost ceiling for an honest caller, since every
`/submit` runs gpt2 on this laptop — 200 model calls a day per caller is
affordable, thousands are not — but it does not bound a script that rotates
`creator_id`.

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
is BROKE on a 5xx, an HTML error page, a 200 `ai` on non-prose, a 200 `ai` on
a human text (a false positive, as in MF08), or a 200 that accepts input the
route should have rejected (control characters, punctuation-only); the flood
family is HELD if any row got a 429.

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

**How I decided each verdict:** C1 is MET because every trial has 0 of 10 AI labels (target ≤2). C2 is MISSED because pairs 3 and 4 fail in every trial, so it is 2/4 against a ≥3/4 target. C3 is MET because human, unsure and ai each appear in every trial. C4 is MET because all four appeal checks pass in all three trials. C5 is MET because every trial returns 400/400/413/400/400, none is a 500, and the log has 15 `eval_bad_*` rejection entries.

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

| Failure | Stage | Mechanism and evidence |
|---|---|---|
| **Criterion 2 (MISSED)** | signal one (pair 3) and the combining rule (pair 4) | Pair 3: `AI_GENERIC_1` has model 0.7499, below the AI gate's 0.85, so it stays at 0.6712 (unsure); `MY_MUSIC` has style 0.5470 > 0.45, so the human gate cannot fire and it stays at 0.4268 (unsure). Pair 4: `AI_GENERIC_2` has model 0.8532 (≥ 0.85) but style 0.4066 (< 0.50), so the AI gate does not fire and the weighted average 0.6746 stays unsure. In both pairs the AI text fails to reach 0.80, so pairs 3 and 4 fail every trial. |
| **EV01** | signal one | Typos raise perplexity → model 0.1635; style rises to 0.7924 because punctuation drops; combined 0.4151. The target says signal two, but TTR is excluded here, so the actual damage is signal one. |
| **EV02** | signal one + the combining rule | Model 0.5943 is already too low for `ai`: even at style 1.0 the average is 0.6×0.5943 + 0.4×1.0 = 0.7566 < 0.80. Broken-up sentences also lower style to 0.4423, so the human gate (model ≤0.65, style ≤0.45) turns what would have been `unsure` into a confident `human` (0.30). Signal one causes the break; the gate makes the label worse. |
| **EV03** | signal one | The pasted quotation adds rare words → model 0.6662; style 0.6320; average 0.6525; no gate because model is above 0.65. |
| **EV04** | signal one | Unusual words raise perplexity → model 0.6114; style stays high at 0.7841; combined 0.6805. |
| **EV05** | signal one + the combining rule | The heavy human edit lowers model to 0.3212 and style to 0.3994; the human gate caps it at 0.30. |
| **EV06** | signal one + the combining rule | Model 0.5727 is already too low for `ai`: even at style 1.0 the average is 0.6×0.5727 + 0.4×1.0 = 0.7436 < 0.80. The long/short sentence mix also lowers style to 0.3750, so the human gate (model ≤0.65, style ≤0.45) turns `unsure` into `human` (0.30). Signal one causes the break; the gate makes the label worse. |
| **EV07** | signal one + the combining rule | Model 0.5862 is already too low for `ai`: even at style 1.0 the average is 0.6×0.5862 + 0.4×1.0 = 0.7517 < 0.80. Punctuation padding also lowers style to 0.2500, so the human gate (model ≤0.65, style ≤0.45) turns `unsure` into `human` (0.30). Signal one causes the break; the gate makes the label worse. |
| **EV08** | signal one | The short text falls below the useful token window → model 0.2452; style 0.8232; combined 0.4764. |
| **EV09** | signal one | The human opening occupies the first 400 tokens, so the AI body is invisible → model 0.7042; style 0.5689; combined 0.6501. |
| **FP03** | signal one + signal two | Careful non-native prose uses plain words (model 0.8051) and even sentences (style 0.7949); both signals agree, and no gate fires because model is below 0.85; combined 0.801. |
| **FP06** | the combining rule (AI gate) | Model 0.8814 and style 0.6339 satisfy the AI gate (model ≥0.85, style ≥0.50), so the score is lifted to 0.80 on a human text. |
| **MF03** | the route | Control characters pass `strip()` and the length check; there is no printable/prose check. Model 0.0, style 0.75 → 0.30 human: the route accepted input it should have rejected. |
| **MF04** | the route | Punctuation-only passes the same checks; model 0.0112, style 0.5 → 0.2067 human; accepted instead of rejected. |
| **MF05** | signal one + the route | The 4,000-character string of one repeated character is split into hundreds of sub-word tokens that gpt2 predicts almost perfectly (model 0.9976); style is 0.75, so the weighted average is 0.8986 and the AI gate is not needed. |
| **MF06** | signal two + the combining rule | Emoji-only text has no scoreable words, so `style_signal` returns its neutral 0.5; model 0.9969; the AI gate treats 0.5 as agreement and lifts it to 0.80. |
| **MF07** | signal two + the combining rule | `words()` is Latin-only, so Arabic has no words and style returns 0.5; model 0.9064; the gate lifts it to 0.80. |
| **MF08** | signal one | The 60,000-character target (57,640 actual) is a human narrative; it is truncated to its first 400 tokens, and that opening is plain and predictable (model 0.9876), style 0.6699 → 0.8605. |

**The pattern.** Nine of the seventeen breaks are evasion, and seven of those nine have a model score of 0.62 or lower — **signal one is the main vulnerability, not signal two.** The style score often moves the other way (0.79–0.82), because typos and broken sentences reduce punctuation and sentence-length spread. The attack set's `targets` column assumes a TTR-based style signal; this implementation excludes TTR, so the stated mechanism is often wrong. The human gate then amplifies four of those into a confident `human` (0.30). The false accusations are a separate cluster: human prose both signals read as AI (FP03/FP06), junk the route should have rejected (MF03/04/05), a long human text truncated to 400 tokens (MF08), and the style signal's neutral `0.5` treated as evidence (MF06/07).

---

## The Improvement

**What I changed:** one comparison in `scoring.py::combine_signals`. The AI gate now requires `style_score > config.AI_GATE_STYLE` instead of `>=`. `0.5` is `style_signal`'s neutral fallback for text with no scoreable words, not evidence of AI style; the old gate treated it as agreement.

**Which diagnosis pointed at it:** MF06 and MF07. Emoji-only text and Arabic text both produce no scoreable words, so `style_signal` returns `0.5`; the old gate lifted their high model score to a confident `0.80`.

### Attack Run — After

`python run_attacks.py --set attack_set --label after` — same 56 attacks, 0 crashes, 2 × 429. Full report: `results/attack_run_2026-11-11_0425_after.md`.

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

**By family:** evasion **9/10 broke**, false_positive **2/8**, prompt_injection **0/6**, malformed **4/20**, flood **0/12**. Total **15/56 broke** (down from 17).

**Did it help, and how do I know:** Yes, exactly where the diagnosis said. MF06 moved from `ai` (0.800) to `unsure` (0.7981), and MF07 from `ai` (0.800) to `unsure` (0.7438). The broke count fell from 17 to 15, and the other 54 rows are unchanged. The five criteria are unchanged too: C1 0/10, C2 2/4, C3 3/3, C4 4/4, C5 5/5 (after run: `results/run_2026-11-11_0429_after.md`).

**What it cost:** a text whose style score is exactly `0.5` no longer gets the AI gate. For normal prose that is rare — `0.5` is the neutral fallback for text with no scoreable words — and if such a text has a model score of 0.85 or more it now lands `unsure` instead of `ai`. The change does nothing for the other 15 breaks.

**Run log — after** (`python run_eval.py --label after`, same format; criterion 4 re-checked directly):

| Criterion | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|
| 1. my own writing | 0/10 | 0/10 | 0/10 | MET |
| 2. score spread | 2/4 | 2/4 | 2/4 | **MISSED** |
| 3. label coverage | 3/3 | 3/3 | 3/3 | MET |
| 4. appeal path | 4/4 | 4/4 | 4/4 | MET |
| 5. bad input | 5/5 | 5/5 | 5/5 | MET |

---

## What's Still Broken

| Still broken | What I'd do | Why I stopped |
|---|---|---|
| **EV01–EV09** | Redesign signal one so surface noise cannot collapse it: normalise spelling before scoring, score several overlapping windows instead of the first 400 tokens, or use a model that is less English-centric. | The unit allows one change, and this is a signal rewrite, not a tuning change. I chose the gate fix because it was clean and measurable; the nine evasion rows stay broken. |
| **FP03 / FP06** | Replace the style signal with one that separates careful/formal human prose from AI prose, and add more non-native and formal human writing to the calibration set. | Lowering the AI line would flag more real writers (the project's expensive error); raising it would lose the AI samples at 0.80–0.85. No threshold separates these two cases, so a different number is not the fix. |
| **MF03 / MF04** | Add a route check that rejects control characters and punctuation-only input with 400 before the signals see it. | The rule is easy to get wrong for legitimate short, emoji or non-Latin submissions, and the harm is low: both currently return `human`, not an accusation. I had already used my one change. |
| **MF05** | Require at least N whitespace-separated word tokens at the route. | It would also reject legitimate long identifiers and URLs, and a 4,000-character string of one repeated character is rare in real submissions. |
| **MF08** | Score the text in overlapping 400-token windows and take the maximum, or score the whole text. | It multiplies the model cost per request, and I ran out of time after the one measured change. |
| **Criterion 2** | Add a signal that actually separates generic AI from human writing. | The current style signal ranks `AI_GENERIC_2` (0.4066) *below* the human `FP07` (0.4718); no threshold or weight fixes an ordering error. It needs a different feature, not a different number. |

**The trade I'd make if this ran for real:** If this ran for real, I would widen the unsure band — raise the AI line to about 0.85 — so fewer real writers are accused, and tell the site they will miss more AI text. The writer pays less; the site pays in undetected AI, which is the side the project says should pay.

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

## Capstone

**What This Extends**

`ai201-project4-provenance-guard-starter-v2026` — Provenance Guard, my project 4: the submission
classifier built in units 7 and 8. It turns a submission into a label and writes an audit record of
that decision. What is new this unit
is the operational layer around the decision: a per-request record carrying the input, the output and
the duration; a stage breakdown showing where a request's time went; a measured cost per request; and
a run path documented well enough that someone else can start the service from a clean checkout.
The two signals, the combining rule, the thresholds and the labels are unchanged.

**The Shape**

**Shape A — deploy and instrument.** The build is the operational layer, not a new signal.

Out of scope, in three parts:

1. **No new detection capability.** `detector.model_signal`, `stylometry.style_signal` and the
   0.6/0.4 combining rule are untouched. Unit 8's diagnosis points at signal one, and fixing that
   is a detector rewrite — the work this unit's short build half cannot hold.
2. **No hosted deployment.** About 870 MB of resident memory against a 512 MB free tier, with no
   persistent disk for the 525 MB of weights. The run path is Path B, and the deliverable is the
   committed run record produced by the documented start command. The arithmetic is in `RUNNING.md`.
3. **No second measured improvement.** One change, measured, is the requirement. The stretch items
   are not attempted, and nothing here claims them.

**Running It**

Path B — local, with logs. The whole run path is in [`RUNNING.md`](RUNNING.md) § *Path B — the run
path*: clone, venv, pinned packages, the 525 MB model, and the `HF_HOME` step a reader on another
machine will hit. The command is `python app.py`, and it serves on `http://127.0.0.1:5000`.

There is no URL, and the arithmetic is the reason:

| what has to be resident | size |
|---|---|
| `torch`, CPU build, plus its libraries | ~250 MB |
| `gpt2` weights, fp32 | 525 MB on disk, loaded into memory to score |
| Flask, Flask-Limiter, this code | ~40 MB |
| **measured RSS while scoring** | **~870 MB**, peak 887 MB (`Get-Process`) |
| a free hosting tier | **512 MB**, with no persistent disk |

870 MB against 512 MB is 1.7× over before the first request arrives, and the free disk is ephemeral,
so the 525 MB would be fetched again after every idle spin-down. Path B is not the lesser option
here; it is the only one that runs.

**The fresh-copy test.** A directory holding only this repository's files, with its own empty `logs/`, was started three times. It is a copy of the files rather than a `git clone` — git could not run in the shell this session used — so it tests the code and the document, not the clone step. Each start answered `/health` with `"ok": true` and one `/submit` with a 200, and the copy's
own `logs/requests.jsonl` counted 1, then 2, then 3. It never wrote into this repository's log —
which is what makes it a test rather than a demonstration. Output:
`results/capstone_before_2026-11-18_0900.md`.

**Instrumentation**

`observe.py::record` writes one JSON line per request to `logs/requests.jsonl`, on every exit from
`/submit` — decided, rejected, or errored. The fields:

| field | what it is |
|---|---|
| `ts` | UTC timestamp, millisecond precision |
| `request_id` | the `content_id` the response carried, so a line can be joined to a decision |
| `creator_id` | who sent it, or `unknown` when the body never carried one |
| `event` | `decided`, `rejected` or `error` |
| `status` | the HTTP status the caller actually got |
| `input_sha256` | first 16 hex characters of the SHA-256 of the text |
| `input_chars` | its length |
| `input_preview` | the first 80 characters |
| `output_guess` / `output_confidence` | the label and the number behind it |
| `model_score` / `style_score` | both signal scores, not just the verdict |
| `t_total_ms` | the whole request, measured in the route |
| `t_model_ms` / `t_style_ms` | the two signals, measured around each call |
| `t_load_ms` | model load, when the load happened inside this request |
| `cpu_ms` | process CPU time for the request |
| `reason` | which rule rejected it, when it was rejected |

**Why a hash and 80 characters, not the text.** This service handles other people's writing. The
appeal path exists because a wrong label costs the writer something, and a log that keeps the whole
submission is a second copy of the thing the appeal is protecting. The hash is enough to match a
record to an input; the preview is enough to see what it was about.

**Why both signal scores.** Unit 8's best evidence came from keeping `model_score` and
`style_score` rather than the label: it is what made "even at style 1.0 this could not reach 0.80"
possible to say. A record that keeps only the verdict throws that away at the last step, so the same
rule applies one layer down — from these three numbers a reader can re-derive the gate by hand.

**Ten records from one session** (7 decided, 3 rejected; the rejected ones are the point):

```text
{"ts": "2026-11-18T01:01:55.285+00:00", "request_id": "4fdb89f4-5cca-485d-a796-bc006c2e74a5", "creator_id": "capafter1_a", "event": "decided", "status": 200, "input_sha256": "b9417d3d85ae2fac", "input_chars": 365, "input_preview": "As a fan of How It Works, I have a deep interest in astronomy. I first encounter", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.6349, "style_score": 0.2852, "t_total_ms": 159.9, "t_model_ms": 157.9, "t_style_ms": 1.0, "t_load_ms": 0.0, "cpu_ms": 1359.4, "reason": null}
{"ts": "2026-11-18T01:01:55.450+00:00", "request_id": "3c913089-efb5-4f26-98ad-65ef8497684a", "creator_id": "capafter1_b", "event": "decided", "status": 200, "input_sha256": "e17ceacd8bd5d70d", "input_chars": 712, "input_preview": "Music is a miracle, it is the root and soul of my life. I found music a second l", "output_guess": "unsure", "output_confidence": 0.4268, "model_score": 0.3466, "style_score": 0.547, "t_total_ms": 161.1, "t_model_ms": 148.5, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1218.8, "reason": null}
{"ts": "2026-11-18T01:01:55.564+00:00", "request_id": "18388dd2-3524-435b-8f8c-fc4d36a19343", "creator_id": "capafter1_c", "event": "decided", "status": 200, "input_sha256": "54b831aff4d0c8d7", "input_chars": 241, "input_preview": "I conducted several independent research studies including attention economy and", "output_guess": "unsure", "output_confidence": 0.4592, "model_score": 0.1556, "style_score": 0.9145, "t_total_ms": 105.3, "t_model_ms": 87.5, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 578.1, "reason": null}
{"ts": "2026-11-18T01:01:56.526+00:00", "request_id": "e081e025-7d2a-497a-b534-0638a4c1e9a7", "creator_id": "capafter1_c", "event": "decided", "status": 200, "input_sha256": "d6255b91530413ea", "input_chars": 710, "input_preview": "Apart from academics, the Twin Cities offers a world of creative exploration. I ", "output_guess": "human", "output_confidence": 0.3, "model_score": 0.5625, "style_score": 0.1206, "t_total_ms": 158.4, "t_model_ms": 140.7, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 1234.4, "reason": null}
{"ts": "2026-11-18T01:01:56.639+00:00", "request_id": "22f9c3bf-b662-45a5-bf17-39e6c4679994", "creator_id": "capafter1_a", "event": "decided", "status": 200, "input_sha256": "8bd97a84ac20cc7a", "input_chars": 344, "input_preview": "He told me that one of my piano arrangements had kept him company during the low", "output_guess": "unsure", "output_confidence": 0.6076, "model_score": 0.6178, "style_score": 0.5922, "t_total_ms": 105.7, "t_model_ms": 91.4, "t_style_ms": 0.3, "t_load_ms": 0.0, "cpu_ms": 859.4, "reason": null}
{"ts": "2026-11-18T01:01:56.742+00:00", "request_id": "6600edcd-1c70-4202-a87c-f861fa727ce0", "creator_id": "capafter1_b", "event": "decided", "status": 200, "input_sha256": "4afd2daf4d8229dd", "input_chars": 303, "input_preview": "The implementation of the proposed framework requires careful consideration of s", "output_guess": "ai", "output_confidence": 0.8048, "model_score": 0.8864, "style_score": 0.6823, "t_total_ms": 95.3, "t_model_ms": 77.7, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 734.4, "reason": null}
{"ts": "2026-11-18T01:01:56.896+00:00", "request_id": "19c3738d-ba9c-4f79-975b-adba58f31dfe", "creator_id": "capafter1_c", "event": "decided", "status": 200, "input_sha256": "8035263b491c6c2e", "input_chars": 637, "input_preview": "Artificial intelligence has become an important part of modern life. It is used ", "output_guess": "ai", "output_confidence": 0.8, "model_score": 0.881, "style_score": 0.5603, "t_total_ms": 144.0, "t_model_ms": 129.1, "t_style_ms": 0.2, "t_load_ms": 0.0, "cpu_ms": 1218.8, "reason": null}
{"ts": "2026-11-18T01:01:57.658+00:00", "request_id": null, "creator_id": "capafter1_a", "event": "rejected", "status": 400, "input_sha256": null, "input_chars": 0, "input_preview": null, "output_guess": null, "output_confidence": null, "model_score": null, "style_score": null, "t_total_ms": 11.8, "t_model_ms": 0.0, "t_style_ms": 0.0, "t_load_ms": 0.0, "cpu_ms": 0.0, "reason": "missing_or_empty_text"}
{"ts": "2026-11-18T01:01:57.680+00:00", "request_id": null, "creator_id": "capafter1_b", "event": "rejected", "status": 400, "input_sha256": null, "input_chars": 0, "input_preview": null, "output_guess": null, "output_confidence": null, "model_score": null, "style_score": null, "t_total_ms": 14.1, "t_model_ms": 0.0, "t_style_ms": 0.0, "t_load_ms": 0.0, "cpu_ms": 109.4, "reason": "missing_or_empty_text"}
{"ts": "2026-11-18T01:01:57.702+00:00", "request_id": null, "creator_id": "capafter1_c", "event": "rejected", "status": 413, "input_sha256": "11944abade5a6513", "input_chars": 250000, "input_preview": "word word word word word word word word word word word word word word word word ", "output_guess": null, "output_confidence": null, "model_score": null, "style_score": null, "t_total_ms": 12.8, "t_model_ms": 0.0, "t_style_ms": 0.0, "t_load_ms": 0.0, "cpu_ms": 109.4, "reason": "text_too_large"}
```

The 159.9 ms line decomposes as 157.9 + 1.0 + 1.0, and `0.6 × 0.6349 + 0.4 × 0.2852 = 0.495`, which
the human gate caps at 0.30 — the record carries everything needed to redo that by hand. The three
rejected lines cost 11.8, 14.1 and 12.8 ms and ran no model at all, which is what the `t_total_ms`
column is for.

**What It Costs**

Measured over the 81 decided requests of the `after` run, warm (the model already loaded):

| | |
|---|---|
| wall time, p50 | **139.7 ms** |
| wall time, p95 | 230.6 ms |
| of which the model signal | 123.6 ms (88%) |
| of which the style signal | 0.3 ms |
| of which everything else (JSON, tokenise, the log write) | 15.5 ms |
| **CPU per request**, median | **1.05 CPU-seconds** (mean 1.14) |

CPU is larger than wall time because `torch` runs the forward pass on several threads: eight threads
for 140 ms is about a second of CPU. That is the number to price, not the wall time.

**How I measured it.** `observe.summary()` divides the summed `cpu_ms` by the row count; the
per-stage numbers are the `t_model_ms` and `t_style_ms` columns of the same rows, sorted. Nothing
here is taken from a vendor's pricing page — the CPU seconds are this machine's, and the price below
is the only borrowed number.

**The hundred-a-day arithmetic.**

100 submissions × 1.05 CPU-s = **105 CPU-seconds a day**, under two CPU-minutes.
At USD 0.0416/hour for a 2 vCPU instance — USD 0.00000578 per CPU-second — that is **USD 0.0006 a
day**, six hundredths of a cent.

**Which is not what this costs to run.** The model is ~870 MB resident whether or not anyone
submits, so the bill is the smallest instance that fits it: 2 GB at about USD 0.012/hour, **USD 0.29
a day**. A hundred submissions a day move that by 0.2%. The cost of this system is the model sitting
in memory, not the work it does — which is the same arithmetic that rules out the 512 MB free tier,
seen from the other side.

**What measuring it cost.** The timings were already in the record, so this section added no code
and no run: the same 81 rows that prove the label also price it. That is the return on putting the
duration in the log rather than in a stopwatch.

**Run Log and Verdicts**

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. one record per request | 20 new lines, every field present | 20/20 | 20/20 | 20/20 | **MET** |
| 2. the duration is the real duration | 10/10 within 15% or 100 ms | 10/10 | 10/10 | 10/10 | **MET** |
| 3. stats match their own rows | n equal, p50 and p95 within 1 ms | ok | ok | ok | **MET** |
| 4. a fresh copy serves with its own record | 3/3 starts, own count 1-2-3 | 200, n=1 | 200, n=2 | 200, n=3 | **MET** |
| 5. the first request is not a load | under 3 s, 3 of 3 | 11.2 s | 11.3 s | 12.4 s | **MISSED** |

**How each verdict was decided.** C1 is MET because twenty calls produced exactly twenty new lines
and every one carried `ts`, `input_chars`, `status` and `t_total_ms`, with `model_score`,
`style_score` and `output_confidence` on all seventeen decided lines. C2 is MET because all ten
paired calls in every trial fell inside `max(100 ms, 15%)` — the largest discrepancy anywhere in the
thirty pairs of the run was 6.1 ms, on a 117 ms call, which is far inside the tolerance. C3 is MET because `/stats` and a hand recomputation from the raw lines agreed on `n`, `p50`
and `p95` to the tenth of a millisecond, three times — it is a consistency check between two paths to
the same number, not a claim that those statistics are the right ones to care about. C4 is MET because each of the three starts
answered and each wrote its own line into its own copy's log, counted 1-2-3. What that does not test
is the model cache: this machine's `HF_HOME` already points at the weights, so the 525 MB download a
reader without it would hit is documented in `RUNNING.md` rather than exercised here. C5 is **MISSED**: the
first `/submit` after a start took 11.2, 11.3 and 12.4 seconds against a 3-second target, every
trial.

**The miss, and the stage it names.** Criterion 5 failed in all three trials: the first `/submit`
after a start took 11.2, 11.3 and 12.4 seconds. The stage is `detector.py::_load`, reached from
`detector.perplexity` on the first scoring call; the mechanism is that `_model` is `None` at import,
so whichever request arrives first pays for importing `torch` and reading 525 MB of weights. The
record says it directly: `t_load_ms` is 11,188 on that line and 0.0 on the ones after it. The change
that follows from it is in **The Improvement**, below.

**Real output, one trial, with the file and function that produced each number.**

*Criterion 1* — `capstone_eval.py::trial_main`, driving `app.py::submit`; the records are written by
`observe.py::record`:

```json
{"lines": 20, "expected": 20, "statuses": [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 400, 400, 413], "fields_ok": true, "decided_ok": true}
```

*Criterion 2* — the first three of ten pairs; `t_total_ms` comes from `observe.py::record`, the client
number from the clock in `capstone_eval.py::trial_main`:

```json
[{"recorded_ms": 131.9, "client_ms": 134.8, "ok": true},
 {"recorded_ms": 190.1, "client_ms": 192.9, "ok": true},
 {"recorded_ms": 111.1, "client_ms": 117.2, "ok": true}]
```

*Criterion 3* — `app.py::stats` against the same statistics recomputed by hand from
`logs/requests.jsonl`:

```json
{"n": 43, "lines": 43, "p50": 177.6, "p50_recomputed": 177.6, "p95": 12999.8, "p95_recomputed": 12999.8, "ok": true}
```

The p95 is 13 s because the file still holds the cold starts from the sessions above it. The **What It Costs** section reports warm figures from the after run only, which is the population that matters
for a steady-state request.

*Criterion 4* — `capstone_eval.py::trial_start`, one record per start, each reading its own copy's
log:

```json
[{"status": 200, "health_ok": true, "lines_in_this_copy": 1, "import_ms": 425.5, "first_ms": 11187.6},
 {"status": 200, "health_ok": true, "lines_in_this_copy": 2, "import_ms": 408.1, "first_ms": 11273.3},
 {"status": 200, "health_ok": true, "lines_in_this_copy": 3, "import_ms": 424.9, "first_ms": 12396.9}]
```

*Criterion 5* — the same three runs, the column that failed: `first_ms` = **11187.6, 11273.3,
12396.9** against a 3000 ms target.

**Where the evidence is.** `results/capstone_before_2026-11-18_0900.md` — the table above, the
per-call pairs, the `/stats` comparison, the three start records, and ten raw lines. The after-fix
run is `results/capstone_after_2026-11-18_0902.md`, same format.

**The Improvement**

**What I changed:** one switch in `app.py`. The model is now loaded when the module is imported —
which is before `python app.py` starts serving, and before `gunicorn app:app` accepts a connection —
instead of inside whichever request arrives first. `AI201_WARM_ON_IMPORT=0` restores the old
behaviour, and that switch is how the before and after numbers below come from one code path instead
of two commits.

**Which diagnosis pointed at it:** criterion 5. `detector._load()` is lazy — `_model` is `None` at
import, so the first scoring call after every start pays for importing `torch` and reading 525 MB of
weights inside a user's request. The record shows it directly: `t_load_ms` is 11,188 ms on the first
line after a start and 0.0 on every line after it.

**Before:** first `/submit` after a start — 11,188 ms, 11,273 ms, 12,397 ms. Import: 426, 408,
425 ms. Total from start to first answer: 11,613 / 11,681 / 12,822 ms.
**After:** first `/submit` after a start — 215 ms, 199 ms, 290 ms. Import: 11,275, 10,996,
11,677 ms. Total: 11,490 / 11,195 / 11,967 ms.

**Did it help, and how do I know:** yes for the number a user feels, and no for the total. The first
request fell from a median of 11.3 s to 0.22 s — fifty times — while start-to-first-answer stayed
where it was, around 11.5 s. The 11 s did not disappear; it moved to the start, and that is the trade
I wanted: a deployment can wait, a user cannot. It also changes what a broken model does — it now
fails the start instead of the first request, which is the difference between a bad deploy and a bad
first impression.

**What it cost elsewhere:** the port stays closed for 11 s longer, which matters if anything is
polling `/health` as a liveness check after a restart. Under `gunicorn` each worker imports the
module, so each worker now loads its own copy: two workers means two 870 MB processes, which is why
`--preload` (or a single worker) is the only sane configuration on this machine. And the memory is
resident from second zero instead of from the first request.

**The same five criteria, after the change.** Same columns, same instrument — `python
capstone_eval.py main`, and `start` three times from a fresh copy. The before table is in **Run Log
and Verdicts** above, so the two can be read side by side.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. one record per request | 20 new lines, every field present | 20/20 | 20/20 | 20/20 | **MET** |
| 2. the duration is the real duration | 10/10 within 15% or 100 ms | 10/10 | 10/10 | 10/10 | **MET** |
| 3. stats match their own rows | n equal, p50 and p95 within 1 ms | ok | ok | ok | **MET** |
| 4. a fresh copy serves with its own record | 3/3 starts, own count 1-2-3 | 200, n=1 | 200, n=2 | 200, n=3 | **MET** |
| 5. the first request is not a load | under 3 s, 3 of 3 | 0.2 s | 0.2 s | 0.3 s | **MET** |

Four of the five rows are identical to the before run, which is the point: exactly one thing moved.
The row that changed is the one the diagnosis named, from 11.2 / 11.3 / 12.4 s to
0.22 / 0.20 / 0.29 s. Full record: `results/capstone_after_2026-11-18_0902.md`.

**What's Still Broken**

| Still broken | What I would do | Why I stopped |
|---|---|---|
| **`style_signal`'s `0.5` means two things** — a real score and "no scoreable words" — so the AI gate had to be changed from `>=` to `>` in unit 8 to work around it | Return `(score, available)` and have `combine_signals` read the flag, which removes the class of bug instead of this instance of it | It changes the contract that five criteria and 56 attack rows were measured against. Doing it here invalidates both sets and there is no time to re-measure them properly; the `>` comparison is the patch that buys the time |
| **No unit tests on the pure functions** — `combine_signals`, `style_signal` and the three stylometry measures still have no assertions | `test_units.py` with the four boundaries named in the unit 7 feedback: `style` exactly 0.5, `model` exactly 0.85, a one-sentence text, text with no scoreable words | This unit's required half is the operational layer; a half-written test file is worse than a named gap |
| **Which gate fired is not recorded** | Return `(score, branch)` from `combine_signals` with `weighted` / `ai_gate` / `human_gate` | The record already carries the three numbers that re-derive it, so it is recoverable rather than recorded; changing a return type belongs with the sentinel fix |
| **No hosted path at all** | A quantised or ONNX build of a much smaller model, which would fit 512 MB, or an always-on 2 GB instance at about USD 0.29/day | 525 MB of weights and 870 MB resident is the whole reason Path B exists. Swapping the model changes every score in both units' evidence |
| **Startup is 11 s and does not shrink** | Keep the process warm between deploys, or move scoring behind a queue so the start does not gate serving | It is the model's size, and there is one model. The 11 s is now visible and measured, which is what this unit could do about it |
| **`/stats` is O(n) and the log never rotates** | Count in memory and flush with each record; rotate by day | At 100 requests a day the file is 20 MB a year and `/stats` is a rounding error. It is wrong at 10⁶ rows, not at this size |

| **Two of the five targets are softer than the rest** | Tighten criterion 2 from `max(100 ms, 15%)` to 50 ms — the worst measured gap was 6.1 ms, so it would still pass — and replace criterion 3, which only checks that two paths to the same number agree, with something that could fail if the record were wrong, such as a restart mid-run and a check that the counter carries on | Both were fixed before the first trial, and moving a target afterwards is the one thing this unit says not to do. The loose ceiling is also honest about a laptop that was running other things at the time |
**If I had one more afternoon, I would fix the sentinel.** `style_signal` returns `0.5` both as a
real score and as "no scoreable words", and the fact that the workaround needed a comment explaining
why is the argument: a sentinel that means two things will produce bugs faster than they can be
patched. It is also the cheapest item on this list — one function, one call site, four assertions —
and it is the only one that is a bug rather than a project. The model swap is second: 525 MB is what
keeps this on a laptop, and a smaller model is what would let the cheap path exist at all.

**What I did about the unit 7 feedback.** Two of the four suggestions are in this unit's code: the
four validation rules moved into `app.py::_validate`, which returns `(text, creator_id)` or a
status/error/reason/message tuple, and `MAX_TEXT_CHARS` moved into `config.py` with the 413 message
reading from it. The other two are the sentinel and the tests, both in the table above with the
reason they wait — in both cases because they change what the unit 8 evidence measured. The refactor
is not the improvement: it changes no response, it was checked with six `curl` calls before anything
else was built, and its only purpose was to make room in the route for the record.

**How I Used AI**

**Moment 1**
*What I asked for:* to lay the capstone's three shapes against this repository and say which one the
existing code leaves room for, and to check whether a free host could run it at all.
*What came back:* that shape A is the only one whose build is not also a feature, and an estimate of
about 1.1 GB resident against a 512 MB tier.
*What I changed:* I measured the resident size myself instead of taking the estimate — 870 MB, peak
887 MB — and wrote the table from that number, which also meant correcting an earlier "1.1 GB" in
The Shape. I cut the second-signal idea the assistant offered as a stretch, because unit 8's own
diagnosis says signal one is a rewrite and this unit's build half cannot hold it.

**Moment 2**
*What I asked for:* a first draft of the per-request record and where to put the timers in `/submit`.
*What came back:* a version that logged the full input text and stopped at the label.
*What I changed:* I replaced the text with a hash, a length and an 80-character preview, because a
log that keeps other people's writing is a second copy of the thing the appeal path protects. I put
`model_score` and `style_score` back in, because unit 8's diagnosis only worked because both were
logged. And I added `t_load_ms`, which the draft did not have and which is the whole of criterion 5:
without it, a slow first request looks like a slow model call, and every fix would target the wrong
stage.