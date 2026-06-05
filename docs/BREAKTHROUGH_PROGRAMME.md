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

## Results so far (all pre-registered, all predictions HIT)
- **JEP-354 PASS** — construction induction: learn a sentence pattern from 2 examples, apply to unseen (1.0).
- **JEP-355 PASS** — naive induction memorises literal words (0.0 on article change); function-word abstraction
  generalises (1.0). A step from slots toward structure.
- **JEP-356 PASS** — the synonym wall: pure induction canNOT invent equivalence (0.0 on "tamed" vs "domesticated");
  separately-TAUGHT equivalence routes through (1.0). **Key finding: the route is COMPOSITIONAL.**
- **JEP-357 PASS** — self-extending reading wired into the live Conversation; teach 2 examples → reads that form
  by itself.
- **JEP-358 PASS** — INTERACTIVE: when it can't parse, it ASKS the teacher and learns the form live (talk.py + web
  GUI). Human-in-the-loop made real.
- **JEP-359 PASS** — facts from taught constructions are fully queryable (who/what/by). Loop closed.

### The honest synthesis (the real result)
Closing the messy-text gap without an LLM is **compositional and teacher-coupled**, not a single mechanism: the
system *learns constructions* from examples + *learns equivalences* from examples + *fills gaps by asking* — and
where knowledge is fundamentally missing, a **human supplies it**. Michael's teaching-in-the-loop turns out to BE
the mechanism. It genuinely self-extends (template-level + function-word abstraction); it does NOT reach human-level
open-domain understanding or creativity (those walls, JEP-351/332, stand and are mapped). Open frontiers: deep
structural generalisation across templates (word order, embedding) and self-directed gap-filling at scale.

## Rules (unchanged)
No LLM / transformer / pretrained. Pre-register the prediction AND most-likely failure before each run. Record
PASS/NULL/PARTIAL honestly; never move a bar. Name established methods (anti-unification, template induction,
ILP) as such; reserve "breakthrough" for a genuinely new result, and only claim it once it survives adversarial
checks. A NULL here is the most valuable kind of finding — it maps exactly what is and isn't reachable.
