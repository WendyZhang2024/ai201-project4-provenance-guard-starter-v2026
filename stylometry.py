"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are computed below because the brief names those three. The
combined style signal uses two of them; type-token ratio is reported but was
excluded after calibration because it did not separate the test inputs.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    Coefficient of variation of sentence lengths: stdev / mean.

    Higher means more variation, which is more human-like. A text with fewer
    than two sentences has no spread, so it returns 0.0; `style_signal`
    treats that case as neutral (0.5) instead of calling it AI.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Higher means more varied vocabulary, which is more human-like. It falls as
    text gets longer, because common words repeat; see the module docstring.
    """
    ws = words(text)
    if not ws:
        return 0.0
    return len(set(ws)) / len(ws)


def punctuation_density(text: str) -> float:
    """
    "Interesting" punctuation per sentence: commas, semicolons, colons, and
    em/en dashes. Higher means more varied punctuation, which is more
    human-like. Full stops are excluded because every sentence has one.
    """
    sents = sentences(text)
    if not sents:
        return 0.0
    count = len(re.findall(r"[,;:—–]", text))
    return count / len(sents)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    Two measures are used, not three:

      - sentence-length spread: more variation is human; cap at 0.8
      - punctuation density: more varied punctuation is human; cap at 2.0
        interesting marks per sentence

    Type-token ratio is still computed and printed, but on the four calibration
    inputs it did not separate the texts (roughly 0.73–0.80, slightly higher for
    the AI sample), so including it added noise rather than signal. That is a
    real finding, not a bug; see the README's Signals and Scoring section.

    A one-sentence text has no spread, so its spread component is neutral (0.5)
    rather than 1.0.
    """
    if not words(text):
        return 0.5

    nsent = len(sentences(text))
    spread = sentence_length_spread(text)
    punct = punctuation_density(text)

    spread_ai = 0.5 if nsent < 2 else 1.0 - min(spread / 0.8, 1.0)
    punct_ai = 1.0 - min(punct / 2.0, 1.0)

    score = (spread_ai + punct_ai) / 2.0
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nM4: style_signal uses sentence spread + punctuation density; TTR is measured but excluded.")
