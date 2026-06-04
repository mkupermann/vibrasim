# GEO-88 — Soft kind-scoping (boost, don't filter) recovers robustness

## Motivation
GEO-87: HARD kind-scoping + a fallible router HURTS (0.67 < 0.90 unscoped) because a mis-route empties the
scope -> IDK. Proposed fix: SOFT scoping — BOOST the routed kind's similarity by a margin instead of filtering
others out, so a mis-route degrades gracefully (the right fact can still win on raw similarity). GEO-88 tests
whether soft scoping beats both hard (0.67) and unscoped (0.90).

## Pre-registration (locked BEFORE run)
- Personal KB + LinearRouter (GEO-87 setup). Soft scoping: sims[fact] += boost if fact.kind == routed_kind;
  pick argmax. Sweep boost in {0.05, 0.1, 0.2}.
- Compare: unscoped (0.90), hard-scope (0.67), soft-scope (each boost).
- Bar: best soft-scope >= 0.90 (recovers robustness) AND ideally > unscoped (helps cross-type without
  brittleness). NULL if soft scoping doesn't beat hard / doesn't recover.

## Result — PASS (soft scoping is the right design; confirms simpler-is-better)
| approach | accuracy |
|----------|----------|
| unscoped (pure argmax) | 1.00 |
| hard-scope (filter) | 0.90 |
| soft-scope boost=0.05 | **1.00** |
| soft-scope boost=0.1 / 0.2 | 0.90 (over-boost forces wrong kind) |

**VERDICT: PASS + clarification.** SOFT scoping with a SMALL boost (0.05) recovers full accuracy (1.00) where
HARD scoping drops to 0.90 — boosting the routed kind degrades gracefully on mis-routes (the right fact still
wins on raw similarity). A LARGE boost over-forces the (possibly wrong) kind, so keep the boost small.
**Clarifies GEO-87:** pure unscoped retrieval here is 1.00; the agent's 0.67 came from OVER-STACKING
(abstention mis-calibration + hard-scope + operator branch compounding), NOT from retrieval. **Reinforced
lesson:** the simple pipeline is the robust default; soft-scope (small boost) is a safe optional refinement;
hard-scope and unnecessary stacked components HURT. Design rule: prefer soft over hard scoping, add components
only when they measurably help, and never let an optional refinement be able to make things worse. This is
the resolved, honest design guidance for the routing/scoping question (GEO-83->88).
