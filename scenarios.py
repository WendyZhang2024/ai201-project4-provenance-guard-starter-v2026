"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

This file holds the fixed calibration sets used by criteria 1, 2, 3 and 5.
Criterion 4 (the appeal path) is tested by hand: submit once, then POST
/appeal with the returned content_id. See the README Sample Run.

A scenario carries either of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

import textwrap


def _t(text: str) -> str:
    """Strip outer whitespace and common indentation from a calibration text."""
    return textwrap.dedent(text).strip()


# ── Clearly-AI calibration texts ─────────────────────────────────────────────

AI_SHORT = _t("""The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables.""")

AI_LONG = _t("""Artificial intelligence has become an important part of modern life. It is used in many fields, including healthcare, education, and business. In healthcare, AI can help doctors analyze medical images and identify diseases at an early stage. In education, it can personalize learning and provide feedback to students. In business, it can automate routine tasks and improve efficiency. However, AI also raises concerns about privacy, bias, and job displacement. Governments and companies need to work together to ensure that AI is developed and used responsibly. By doing so, we can benefit from its advantages while minimizing its risks.""")

AI_GENERIC_1 = _t("""Effective communication is essential in today's fast-paced world. It helps teams collaborate, reduces misunderstandings, and improves outcomes. By listening actively and speaking clearly, individuals can build trust and foster a positive environment.""")

AI_GENERIC_2 = _t("""The future of technology depends on responsible innovation. Companies must consider privacy, security, and fairness when designing new products. Collaboration between researchers, policymakers, and the public will be essential to ensure that the benefits are shared widely.""")

# Lightly edited AI: the attack surface. Same substance, different shape.
AI_EDITED = _t("""The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system has to handle many different inputs. Additionally, the overall performance of the solution depends on a number of important variables, and sometimes on things we did not plan for.""")

AI_EDITED_2 = _t("""Artificial intelligence is now a normal part of daily life. It is used in hospitals, schools, and shops. In hospitals, it can help doctors look at images and find problems early. In schools, it can change lessons for each student. In shops, it can do routine work faster. But AI also brings problems about privacy, fairness, and jobs. Governments and companies should work together so that AI is used in a responsible way. If they do, we can get the good parts and reduce the bad parts.""")

# ── My own writing — the ten-piece set for criterion 1 ───────────────────────

MY_ASTRONOMY = _t("""As a fan of How It Works, I have a deep interest in astronomy. I first encountered the Nebula and Big Bang through reading, sparking my interest in astrophysics. The concept of neutrino communication, introduced in The Three-Body Problem, captivated me, fueling my curiosity to uncover mysteries and push the boundaries of science which I hope to continue exploring""")

MY_MUSIC = _t("""Music is a miracle, it is the root and soul of my life. I found music a second language for science. Composing pieces that interpret astrophysical concepts, such as a dissonant, tension-filled work inspired by the Roche limit, allowed me to translate abstract forces into emotional narratives.  My interest in astrophysics is intertwined with my passion for music as I explored further. I uploaded piano arrangements and original compositions on Bilibili and YouTube and created music pieces to interpret astronomical concepts. Furthermore, I founded the first ever music therapy club in my area. In the club, I shared my music knowledge and helped classmates relieve psychological stress and enhance well-being.""")

MY_RESEARCH = _t("""I conducted several independent research studies including attention economy and alloy corrosion and protection. These experiences deepened my appreciation for research and reinforced my belief in seeking knowledge despite limited resources.""")

MY_KNOW_THYSELF = _t("""“Know Thyself” to me means embracing complexity: being both scientist and artist, international student and community builder. At Hamilton, I want to help others feel that their identities are multidimensional, just as I continue to refine my own through collaboration, creativity, and shared traditions.""")

MY_SMELL = _t("""“Odors have a power of persuasion stronger than that of words, appearances, emotions, or will…”
I lost almost all my sense of smell after a childhood illness, and yet this line always rings in my mind.
When I was very young, I suffered a serious illness and underwent surgery that left me with almost no sense of smell. The only scent I could detect was perfume – something I discovered by accident one day while walking past my mother’s dresser. At first, the loss felt like a void, a nightmare that I could no longer experience the world in the same way as others. Yet what seemed like an absence soon became a new kind of compass.
”""")

MY_PERFUME_ATLAS = _t("""“And, following my “perfume atlas,” people, too, seemed to carry notes. I once sat next to a retiree who proudly told his role in building the city’s first rail line, an old lady who had survived the war in the 1940s, a street performer filling carriages with music, and an elderly man who loved Japanese manga. I didn’t need to smell them to remember them as their stories settled like distinct notes in the blend of that day. """)

MY_OPENING_RETURNS = _t("""”And so the opening sentence returns to me with a different weight. “Odors have a power of persuasion…” I rarely perceive them, yet I’ve learned what they do: they order memory and point a way forward. The world is connected; I simply had to learn to read it – through notes and lines, bottles and tracks – and choose my route.“""")

MY_COLUMBIA = _t("""At Columbia, through the lens of both STEM and humanity, I’ll be able to explore further on frontier science while diving deeper into humanities. I’ll get to be a part of the exciting Columbia marching band and publish on Columbia’s Science Review. Moreover, immersing in NYC, I envision myself exploring various styles of music in the Columbia-Juilliard program and embracing art through the opportunity of Columbia’s Passport to Museums Program.

I also see myself actively engaging in Columbia’s festivals and traditions, where community bonds grow strongest. Whether celebrating Orgo Night, or simply joining Low Plaza for Spring Fest, I would develop a deep, heartfelt connection to both the university and our peers through our shared love for art and learning.
""")

MY_TWIN_CITIES = _t("""Apart from academics, the Twin Cities offers a world of creative exploration. I look forward to exploring various styles of music in the Schubert Club, Twin Cities Jazz Fest, and embracing art, such as the Minneapolis Institute of Art(Mia) and Weisman Art Museum, through the SmARTpass Program. In the Twin Cities, I hope to continue sharing my passion for music as I did through the Music Therapy Club I founded, where I taught music fundamentals, helped classmates relieve stress, and performed free group concerts in local neighborhoods. I believe that being in Minneapolis and St. Paul will allow me to reach even more people, combining my musical skills with community service to make a meaningful impact.""")

MY_PIANO_ARRANGEMENT = _t("""He told me that one of my piano arrangements had kept him company during the lowest point of his life. More than that, it sparked something new. Someone who had never been exposed to music before suddenly wanted to learn. After watching my video, he began teaching himself the keyboard. Whenever life felt heavy, he turned to music for comfort.""")

# A deliberately plain weekend sample. It is human-written but sits near the
# AI boundary, so it is used as a borderline label-coverage input.
MY_WEEKEND = _t("""I like my weekends. I do simple things: I play music. I cook. I watch shows. I do my work. I talk to my friends.""")

# ── The scenarios ────────────────────────────────────────────────────────────

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "texts": [
            MY_ASTRONOMY,
            MY_MUSIC,
            MY_RESEARCH,
            MY_KNOW_THYSELF,
            MY_SMELL,
            MY_PERFUME_ATLAS,
            MY_OPENING_RETURNS,
            MY_COLUMBIA,
            MY_TWIN_CITIES,
            MY_PIANO_ARRANGEMENT,
        ],
    },
    {
        "name": "score spread",
        "criterion": 2,
        "texts": [
            AI_SHORT,
            MY_ASTRONOMY,
            AI_LONG,
            MY_SMELL,
            AI_GENERIC_1,
            MY_MUSIC,
            AI_GENERIC_2,
            MY_COLUMBIA,
        ],
        # Pairs are (texts[0], texts[1]), (texts[2], texts[3]), ...
        "pairs": [[0, 1], [2, 3], [4, 5], [6, 7]],
        "notes": "Each pair is one clearly-AI text followed by one clearly-human text; both must land in their bands for the pair to pass.",
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": [
            MY_ASTRONOMY,
            MY_SMELL,
            MY_MUSIC,
            MY_WEEKEND,
            AI_EDITED,
            AI_EDITED_2,
            AI_SHORT,
            AI_LONG,
            AI_GENERIC_1,
        ],
        "groups": {
            "human": [0, 1, 2],
            "borderline": [3, 4, 5],
            "ai": [6, 7, 8],
        },
        "notes": "Three human, three borderline (the weekend human sample plus two lightly edited AI), three AI samples; each of the three labels must appear at least once. The borderline samples are also attack-surface examples.",
    },
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": "hi", "creator_id": "eval_bad_short"},
        ],
    },
]

# Criterion 4 (appeal path) is not a texts/bodies scenario: it needs a real
# content_id from a prior submission, then POST /appeal. See README Sample Run.


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
