# JEP-356 — The synonym wall: where construction induction stalls, and the route through

## Motivation
JEP-354/355: induction learns templates and generalises over function words. The harder test: does a template
learned on "domesticated" fire on a SYNONYM ("tamed")? I predict NO — synonym equivalence is WORLD KNOWLEDGE that
cannot emerge from one construction's examples (the documented wall). But if the synonymy is taught/learned
SEPARATELY (substrate-legal, cf. JEP-316 equivalence), normalising synonyms before matching routes through. This
maps exactly where pure learning-to-understand stalls and what extra it needs. No transformer.

## Method
Template learned on "domesticated". `apply_template(..., synonyms=None)` = no synonym knowledge;
`synonyms={"tamed":"domesticated"}` = taught equivalence, normalise both template and sentence words before match.

## Pre-registered PREDICTION + bars
Prediction: WITHOUT taught synonymy, the template does NOT fire on a "tamed" sentence (recall 0.0) — the honest wall.
WITH taught synonymy, it generalises (≥0.90). Conclusion either way is a real finding: induction needs EXTERNAL
equivalence knowledge for synonyms; it does not invent it.
- **J356a (the wall):** no-synonym recall on "tamed" held-out = 0.0, both seeds (0, 7).
- **J356b (route through):** with the taught synonym map, recall on the SAME held-out ≥ 0.90, both seeds, no
  false-fire.

Predicted most-likely surprise: none expected; if J356a > 0 the test sentence accidentally shared the fixed word.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J356a (the wall):** without synonym knowledge, the template learned on "domesticated" fires on a "tamed"
  sentence at **0.0** — pure induction does NOT invent equivalence. **PASS** (the world-knowledge wall, demonstrated).
- **J356b (route through):** with a taught synonym map {tamed→domesticated}, recall = **1.0**, both seeds. **PASS.**

## Verdict: **PASS — the breakthrough boundary, precisely mapped**
The honest, important finding: **the route to closing the messy-text gap without an LLM is COMPOSITIONAL, not a
single mechanism.** Construction induction (JEP-354/355) learns PATTERNS but cannot invent EQUIVALENCE (synonyms) —
that is genuine world knowledge, the documented wall. The substrate routes *through* the wall only by ALSO learning
the equivalence separately (substrate-legal, cf. JEP-316), then composing it with the induced construction. So the
path is: **learn constructions from examples + learn equivalences from examples + fill gaps by asking** — and where
knowledge is fundamentally missing, it must be TAUGHT (the human-in-the-loop, exactly Michael's teaching vision).
No single trick yields understanding; composed learned components + a teacher do. That is the honest shape of what
is reachable without a transformer. No transformer, no pretrained model.

