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



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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
