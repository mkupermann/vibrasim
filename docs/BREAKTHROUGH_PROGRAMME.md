# The Breakthrough Programme — attacking the wall via predictions

Michael's directive: *"create experiments with predictions in order to reach the scientific breakthrough nobody has
— we work together on the breakthrough via experiments and predictions."*

## What the breakthrough actually is (honest)
The wall (JEP-351, demonstrated): without an LLM, the system reads ~100% of CLEAR factual prose but only ~25% of
genuinely complex REAL prose, and cannot do creative generation (JEP-332). The honest, *reachable* breakthrough is
NOT "match a transformer" — it is: **a transparent system that EXTENDS ITS OWN understanding from a few examples,
instead of a human hand-coding every sentence form.** A child doesn't get a new grammar rule programmed in; it
generalises one from a handful of examples. If the substrate could do that — *few-shot construction induction* and
*self-directed gap-filling* — it would close the messy-text gap by learning, not by us coding. That is a genuine,
publishable, no-LLM result.

## The attack (each step a pre-registered experiment with a prediction)
- **A. Construction induction (JEP-354+):** learn a NEW sentence pattern from 2-3 (sentence → facts) examples
  (anti-unification / template generalisation), then apply it to unseen sentences of that pattern. Honest prediction:
  works for slot-templates (same fixed words), not deep syntactic novelty — measure exactly how far it generalises.
- **B. Self-directed gap-filling:** the system uses "what is not clear to you?" (JEP-346) to drive its OWN learning —
  ask for missing definitions, integrate, re-read. Toward autonomous understanding.
- **C. Generalisation across templates:** can induced templates compose / abstract (passive ↔ active; "X is in Y" ↔
  "Y contains X")? The honest test of whether induction yields real structure or just memorised slots.
- **D. The creativity wall (JEP-332):** revisit only if A–C succeed — whether learned structure ever yields genuine
  novelty, or recombination remains the ceiling (likely the latter; we'll prove it either way).

## Rules (unchanged)
No LLM / transformer / pretrained. Pre-register the prediction AND most-likely failure before each run. Record
PASS/NULL/PARTIAL honestly; never move a bar. Name established methods (anti-unification, template induction,
ILP) as such; reserve "breakthrough" for a genuinely new result, and only claim it once it survives adversarial
checks. A NULL here is the most valuable kind of finding — it maps exactly what is and isn't reachable.
