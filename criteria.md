# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## 1. False positives

**Criterion:** Of the 10 pieces I wrote myself in my fixed calibration set, at most **2** are labeled high-confidence AI in **each of 3 trials**.

**Why this target:** Signal one rewards common words and short sentences, and my own writing is plain; a wrong accusation costs the writer more than a missed detection costs the site. At 2/10, two of my ten pieces would produce the kind of appeal letter from the brief's real-writer exercise — that is the cost I am accepting — and I keep 2/10 because my own plain style is exactly what signal one over-flags, while a stricter 1/10 would be a number I cannot yet defend.

---

## 2. Score spread

**Criterion:** In at least **3 of 4 pairs** from my fixed calibration set, the clearly-AI text lands in the AI band (confidence **≥ 0.80**) and the clearly-human text lands in the human band (confidence **≤ 0.35**).

**Why this target:** The bands are 0.45 apart; if the two texts do not land in different bands, the labels are not separating the cases they are supposed to separate. 3 of 4 allows one noisy pair without letting the whole standard slide.

---

## 3. Label coverage

**Criterion:** Each of the three labels appears at least once in a fixed **9-piece calibration set** (three human, three borderline, three AI samples).

**Why this target:** A label that never appears is a dead branch. With `AI_THRESHOLD = 0.80`, the AI label is only reachable if some text scores at least 0.80; three examples per label gives each one a chance to appear even if one is misclassified.

---

## 4. Appeal path

**Criterion:** Every valid appeal (existing `content_id`, non-empty `reasoning`) returns **200**, appends an entry with `status: under_review`, and increments `appeal_count`; an unknown `content_id` or a mismatched `creator_id` returns **404**.

**Why this target:** The appeal is the only remedy for a false positive; if it does not record, the wrong label stands. The 404 is deliberately the same for an unknown id and a wrong creator, so the endpoint does not leak whether an id exists.

---

## 5. Bad input

**Criterion:** Missing or empty `text` returns **400**; `text` over **100,000 characters** returns **413**; neither returns **500**; both leave a rejection entry in the log.

**Why this target:** Malformed input is one of the most common real failures; 400/413 are contract responses, 500 is a bug. The rejection entry makes the attempt visible instead of leaving an absence.

**Where the sets live:** the 10 pieces for criterion 1, the 4 pairs for criterion 2, and the 9 pieces for criterion 3 will be fixed in `scenarios.py`, so someone else can rerun them without asking me which texts I meant.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
