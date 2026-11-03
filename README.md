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
2. **Validation.** The service checks that `text` is present, non-empty, and at most 100,000 characters. This adds an accept/reject decision; bad input is stopped here, before any model runs.
3. **Signal one — the model signal.** `detector.model_signal(text)` measures how predictable the text is to gpt2 and turns that into a 0–1 score. This adds `model_score`, where higher means more AI-like.
4. **Signal two — the style signal.** `stylometry.style_signal(text)` measures the shape of the text (sentence-length spread, vocabulary variety, punctuation density) and turns it into a 0–1 score. This adds `style_score`, where higher means more AI-like.
5. **Combining.** `scoring.combine_signals(model_score, style_score)` combines the two scores into one `confidence` between 0 and 1. This adds the single number the labels are based on.
6. **Labelling.** `scoring.score_to_label(confidence)` maps the score to `guess` (`human`, `unsure`, or `ai`) and to the sentence a reader sees. This adds the human-readable decision.
7. **Audit and response.** `audit.log_decision(...)` appends one JSON object to `logs/audit.jsonl` with the timestamp, `content_id`, `creator_id`, both signal scores, the combined score, the label, and the status. The response returns the same `content_id` plus the scores and label. This adds the durable record and the ID that `/appeal` needs.

The important seam is step 5: everything above it produces numbers, everything below it depends on the single number it produces. If a label looks wrong, the cause is either a signal or the combining rule — not the label code alone.

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** How predictable the text is to gpt2, expressed as perplexity and squashed into a 0–1 score. Lower perplexity (more predictable text) produces a higher score, so higher means more AI-like.

**Why that might differ between human and AI writing:** A language model writes by repeatedly choosing a likely next token, so its output tends to be text the model finds easy to predict. Human writing is lumpier — odd word choices, abrupt turns, concrete details the model did not expect.

**What it can't see:** Predictability is not authorship. The signal rewards common words in short, ordinary sentences, which is exactly how many real people write: second-language writers, younger writers, and anyone writing plainly on purpose. Dense, ornate prose often goes the other way and reads as human, because rare words are what the model fails to predict. The signal also shifts with text length and topic, and it truncates at 400 tokens. The people most likely to be accused are the ones with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text rather than its meaning: sentence-length spread (standard deviation divided by the mean), vocabulary variety (unique words over total words), and punctuation density (with commas, semicolons, and dashes mattering more than full stops). The three measures are normalised, direction-aligned, and combined into a 0–1 score where higher means more AI-like.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower vocabulary band, because that is what choosing the most likely next word produces on average. Human writing is more uneven: a three-word sentence next to a forty-word one, more repetition in some places and more variety in others.

**What it can't see:** It cannot read. It has no idea what the text says, so anything that changes the shape without changing the substance moves it: typos, sentence fragments, a pasted quotation, deliberate punctuation changes. That is cheap to do on purpose, and the attack set will do exactly that. Two further limits: vocabulary variety falls as text gets longer, so texts of different lengths are not directly comparable, and a one-sentence submission has no sentence-length spread at all.

### The combining rule

**The rule:** A weighted average of the two signal scores. Both signals point the same way — higher means more AI — so the combined score does too. When the signals disagree, the average lands in the unsure band rather than forcing a confident label; that disagreement is treated as genuine uncertainty, not as a tie to break.

**The numbers:** `0.5 × model_score + 0.5 × style_score`. Thresholds: `HUMAN_THRESHOLD = 0.35`, `AI_THRESHOLD = 0.80`. Bands: human `0.00–0.35`, unsure `0.35–0.80`, AI `0.80–1.00`.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:** A lightly edited AI paragraph can score high on the model signal (still predictable) but lower on the style signal (editing introduces uneven sentences). With `model_score = 0.92` and `style_score = 0.48`, the average is `0.70`, which lands in the unsure band. The rule does not force an AI label; it reports uncertainty, and the reader can appeal if the text is theirs.

<!-- M1 design note: the false-positive case that drives the 0.80 threshold is traced in notes/m1-design.md. M5 must set these thresholds in config.py and re-check this section against the code. -->



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "creator_id": "..."}'
```

```json

```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json

```

---

## How I Used AI

**Moment 1 — understanding the instructions**

- *What I asked for:* I asked an AI assistant to explain the project instructions. I was super confused by the two-unit structure and found it hard to start.
- *What came back:* A step-by-step breakdown of M1–M6, an explanation of the two signals and their blind spots, and the false-positive trade-off behind the thresholds.
- *What I changed:* I used it as a map, not an answer. I chose the 0.80 AI threshold, the 2/10 false-positive target, and the C2 “unsure” wording, and used those decisions to draft the M1 trace.

**Moment 2 — getting the model to load**

- *What I asked for:* `python detector.py` failed with `PermissionError` while creating `~/.cache/huggingface/models--gpt2`. I asked why, and whether the model could run without that cache.
- *What came back:* The diagnosis was a sandboxed shell that could not write outside the workspace, so the fix was a repo-local cache (`.hf-cache`) plus `HF_HOME`, with a `.gitignore` entry.
- *What I changed:* I ran the commands with the assistant's guidance, confirmed `detector.py` produced a score, and kept the cache out of git.

**Moment 3 — testing the false-positive number**

- *What I asked for:* I asked Claude to write the message a real writer would send if they were one of the people my 2/10 rate allows.
- *What came back:* A letter from a hypothetical plain-writing essayist whose own work was labeled high-confidence AI; they offered drafts, timestamps and notes, and asked how to appeal and whether the piece stays marked.
- *What I changed:* I kept 2/10, but rewrote the criterion's reason to name the cost: two of my ten pieces would produce that letter. I also noted for M5 that the AI label should tell the writer how to appeal.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

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
