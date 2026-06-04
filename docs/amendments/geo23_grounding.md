# GEO-23 — The VALUE-ADD over a raw LLM: grounded abstention (knowing what it doesn't know)

## Motivation
Sharpest honest question: does geometric retrieval ADD anything over a generative LLM? Key answer: GROUNDING
— a retrieval method can ABSTAIN when no fact supports an answer (max similarity below a threshold), whereas
a generative LLM confabulates a plausible-but-wrong answer. GEO-23 tests whether the method reliably
separates answerable (fact in store) from unanswerable (no fact) questions and abstains correctly.

## Pre-registration (locked BEFORE run)
- Store: 15 "The capital of <country> is <city>." for 15 countries.
- ANSWERABLE questions: 15 capitals of IN-STORE countries.
- UNANSWERABLE questions: 15 capitals of OUT-OF-STORE countries (not in the store at all).
- Method: retrieve nearest fact; if max cosine < threshold tau -> ABSTAIN ("unknown"), else answer.
- Choose tau by separation on a held-out split (NOT post-hoc on the test): split answerable/unanswerable
  50/50, set tau = midpoint of the two groups' mean max-sim on the CALIBRATION half, evaluate on the TEST
  half.
- Metrics: on TEST half, (a) answerable-correct (answered AND right), (b) unanswerable-abstain rate,
  (c) overall decision accuracy. Bars: decision accuracy >= 0.8 AND unanswerable-abstain >= 0.7.
- Control: report what happens with NO abstention (tau=0): unanswerable questions get WRONG confident
  answers (the LLM-confabulation failure mode this prevents).

PASS if the method reliably abstains (knows what it doesn't know) — the concrete value-add over generation.

## Result
| metric | value |
|--------|-------|
| calibrated tau (no test tuning) | 0.699 (answerable 0.868 vs unanswerable 0.531) |
| (a) answerable answered-correctly | **1.00** |
| (b) unanswerable abstain rate | **1.00** |
| (c) overall decision accuracy | **1.00** |
| control (no abstention) confidently WRONG on unanswerable | **1.00** |

**VERDICT: PASS** — large, clean separation between answerable (sim ~0.87) and unanswerable (~0.53)
questions lets the method ABSTAIN reliably (decision accuracy 1.00). The no-abstention control gets every
unanswerable question confidently wrong — exactly the confabulation a generative LLM produces. **This is the
concrete value-add: grounded, hallucination-free reasoning that knows what it doesn't know.** Combined with
updatable memory (GEO-11) and composable structure (GEO-12), it is what geometry-over-an-LLM gives that a
raw generative LLM does not.
