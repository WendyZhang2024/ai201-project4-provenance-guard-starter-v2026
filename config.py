"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# ⚠️ These are placeholders. Milestone 4 asks you to write your combining rule
# down BEFORE you code it, and to put the numbers in your README. Whatever you
# decide, it goes here.

# The model signal separated the four calibration inputs better, and the style
# signal is noisier, so the model gets more weight. The two weights sum to 1.
WEIGHT_MODEL_SIGNAL = 0.6
WEIGHT_STYLE_SIGNAL = 0.4

# The gate: when the model signal is very confident and the style signal is not
# strongly human, lift the combined score to the AI floor. This catches AI text
# whose style score is only moderate without letting the plain weekend sample
# (model 0.8037) through. The values are a four-input design choice, not a
# statistically calibrated result.
AI_GATE_MODEL = 0.85
AI_GATE_STYLE = 0.50
AI_GATE_FLOOR = 0.80

# The human gate is the symmetric counterpart: when both signals are clearly on
# the human side, set the combined score to the human ceiling so the human
# label is reachable. This is what makes all three labels reachable in the
# four-input calibration set.
HUMAN_GATE_MODEL = 0.65
HUMAN_GATE_STYLE = 0.45
HUMAN_GATE_CEILING = 0.30


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

HUMAN_THRESHOLD = 0.35
AI_THRESHOLD = 0.80

# With the two gates above, all three labels are reachable on the four-input
# calibration set. `scoring.label_ranges()` prints the bands.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# ON for unit 8. The two numbers answer the brief's two people: a real writer
# submitting their own work a few times an hour, and a script sending a
# thousand variations to map the thresholds.
#
# 10/minute — a writer revising and resubmitting bursts at most 3–5 times a
#   minute, so 10 leaves about 2x headroom. A script mapping the 0.35 / 0.80
#   boundary needs hundreds of samples; at 10 a minute it would need half an
#   hour per hundred, and it hits the wall on its first burst.
# 200/day — a writer's heavy day is 10–30 submissions, so 200 is 6x their load.
#   It caps a slow mapping run at 200 boundary samples a day, a fifth of what
#   it needs, and bounds the model cost: every /submit runs gpt2.
#
# The trade this picks: a script gets slightly more boundary information rather
# than a writer being blocked mid-draft. A 429 mid-revision is its own harm.
#
# The run of status codes behind these numbers is in the README's Rate Limiting
# section, produced by `run_attacks.py --flood 15`.

RATE_LIMITING_ENABLED = True

RATE_LIMIT_PER_MINUTE = 10
RATE_LIMIT_PER_DAY = 200

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
RESULTS_DIR = ROOT / "results"
