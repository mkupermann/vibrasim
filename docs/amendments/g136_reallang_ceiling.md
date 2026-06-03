# G136 — The no-LLM cognition CEILING: real text vs bigram

## Pre-registration (locked BEFORE run)
The EQMOD-2 stack (VSA-composed context → reservoir/ELM features → online RLS → cleanup) scored 90–100% on
TEMPLATED micro-languages (BET-130/132). Does it capture REAL language structure, or plateau at trivial
classical-LM level? Next-word prediction on a small real English corpus (K=2 context), held-out, vs a
BIGRAM baseline. No transformer.

**Bars (locked):**
- G136 PASS: stack held-out acc >= bigram + 0.10 (captures beyond local statistics).
- NULL(ceiling): stack ≈ bigram (within 0.05) → plateaus at trivial-LM level.
- NULL(worse): stack < bigram − 0.05.

## Result
vocab=13, 106 samples (train 79 / test 27), chance 0.077.
| model | held-out next-word acc |
|-------|------------------------|
| EQMOD-2 (VSA+reservoir+RLS) | 0.52 |
| bigram baseline | 0.48 |

**VERDICT: NULL (ceiling)** — the stack ≈ bigram (+0.04, below bar).

## Finding — on real text the no-LLM stack is bigram-level (the honest ceiling)
The sophisticated VSA+reservoir+RLS pipeline does no better than a trivial bigram on real text. Its strong
prior results were on TEMPLATED languages with a clean selectional rule it could exploit; real text (even
this small sample) has the long-tail statistics that local classical methods plateau on — which is exactly
why transformers/LLMs dominate real language. (Caveat: tiny corpus; this is an indicative ceiling, not a
benchmark — but it shows no magic generalization on real text.)

## Complete, evidence-based answer to the human-AI-without-LLM question
- PHYSICAL substrate: no computational role; memory/IO only (G133–G135 all NULL; reservoir.py is a numpy
  random matrix — the physics is unused).
- NO-LLM cognition stack: capable on TEMPLATED/structured tasks (BET-130–143: composition, QA, codegen),
  but on REAL language it is BIGRAM-LEVEL (G136). Far from human-like.
So "human-like AI without an LLM" is not reachable on this project's pieces: the substrate can't compute,
and the classical no-LLM cognition plateaus at trivial-LM level on real language. The genuine assets are a
no-LLM MEMORY (matter-position) and a bounded no-LLM symbolic/statistical toolkit — useful, honest, and
not a mind. Closing the gap to human-like language is the established hard problem that transformers
address and these methods do not.
