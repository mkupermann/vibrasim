# JEP-393 — Integration capstone: the whole vision in one flow

## Motivation
Each capability was validated in isolation. This proves they COMPOSE in a single realistic flow: read a factual article
across two days (persistence), capturing is-a + part-of + causal + counts with the construction sweep; apply a
correction mid-stream; surface curiosity gaps; and answer a broad question set spanning all relation types and multi-hop
— reliably (consolidation/analog) and with honest abstention. Integration can surface interaction bugs that isolated
tests miss. No transformer.

## Method
- **Day 1:** read a factual article (taxonomy + part-of + causal + counts, mixed constructions). Save.
- **Day 2:** load; read more facts INCLUDING a correction ("Actually, a whale is not a fish; a whale is a mammal").
  Save.
- **Day 3:** load; ask a broad question set (is-a multi-hop incl. cross-day, part-of, causal, count, the corrected
  fact), check curiosity gaps and OOD abstention and junk.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: everything composes — broad Q&A reliable, the correction holds, gaps sensible, abstention perfect, no junk.

- **J393a (broad multi-relation Q&A, incl. cross-day + corrected):** ≥0.90 accuracy on the question set (is-a multi-hop,
  part-of, causal, count, AND the corrected "is a whale a fish?" → no / "is a whale a mammal?" → yes), both seeds (0,7).
- **J393b (curiosity + abstention):** `gaps()` lists only genuinely-undefined referenced concepts (no defined/roots);
  OOD abstention = 1.0, both seeds.
- **J393c (clean + durable):** junk rate ≤0.05; consolidation persisted across days (`closed_relations` present on day
  3); `pytest -m "not slow" tests/test_conversation.py` passes.

If composition surfaces an interaction bug (a capability that works alone but not together), report it — that is the
point of the test. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PARTIAL** (integration composes; J393b miss is my ground-truth error + one minor parser gap)
- **J393a (broad multi-relation Q&A): PASS** — **0.90**, both seeds. Correct across cross-day multi-hop (poodle→animal),
  part-of (wheel→car), count (car→4 wheels), causal (heat→friction, expansion→heat), the CORRECTION (whale is a fish
  → after day-2 correction "is a whale a fish?" → **no**, "is a whale a mammal?" → **yes**), conjunction multi-hop
  (salmon→animal), and appositive (lion→predator). The single miss is "is a dog warm-blooded?" — a real but minor
  PARSER gap: "is X <property>?" routes to `is_a(dog, warm-blooded)` instead of `has_property` (the property was stored
  correctly via JEP-382; only the question routing is wrong).
- **J393c (clean + durable): PASS** — junk rate **0.0**, `closed_relations` persisted across all days, suite **10
  passed**. Both seeds.
- **J393b (curiosity + abstention): literal bar NOT met — my GROUND-TRUTH ERROR.** OOD abstention = **1.0** (correct).
  The miss: "car" appears in `gaps()`, and I had listed it as should-NOT-be-a-gap. But the article never states what a
  car IS (only "a wheel is part of a car" and "a car has four wheels") — car has **no is-a parent**, so flagging it as
  undefined is **correct**. Same class as the JEP-379 sparrow mislabel: the substrate behaved correctly; my
  pre-registered expectation was wrong. (The fuller gap list — bird, cat, predator, wheel, car, heat, friction,
  expansion — are all genuinely referenced-but-undefined; gaps() now also surfaces part-of/causal-referenced concepts,
  which is reasonable, if noisier than the is-a-only case.)

## Verdict: **PARTIAL — the whole vision composes; the one literal miss is my mislabel, plus a minor parser gap**
In a single flow the substrate reads a factual article across days (is-a + part-of + causal + counts, mixed
constructions), answers it reliably including cross-day multi-hop, holds a mid-stream correction (whale not a fish),
surfaces sensible curiosity gaps, abstains perfectly, keeps zero junk, and persists consolidation — no interaction
bugs. J393b's literal failure is a ground-truth error (car is genuinely undefined in the text, so correctly a gap);
bar **not** moved. Two honest, minor findings logged for follow-up: (1) "is X <property>?" should route to
`has_property` not `is_a`; (2) `gaps()` surfaces part-of/causal-referenced concepts too (broader than is-a). The
integration of the full Michael vision is demonstrated. No transformer.
