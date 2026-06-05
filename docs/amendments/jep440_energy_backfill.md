# JEP-440 — Backfill the energy model from stored valence (existing brains generalize immediately)

## Motivation
JEP-436/437 added/persisted the energy model, but a brain taught BEFORE this (e.g. Michael's live
GUI brain) has a populated `valence` dict and NO trained learner — so it cannot yet generalize affect
to untaught concepts until each fact is re-taught. JEP-440 backfills: the first time generalization
is needed, train the learner from all already-stored `(entity_cloud, valence)` pairs, so existing
brains gain the capability with no re-teaching. Established methods; integration only. No transformer.

## Method (`world/substrate_memory.py` + `tools/run_jep440_backfill.py`)
- Add `_backfill_energy()`: if `self.energy is None` and `self.valence` is non-empty, create a
  `ValenceReservoirLearner` and `experience` every stored `(entity_cloud(e), v)`. Idempotent (runs
  once; after it the learner exists).
- Call it lazily at the top of `predict_valence`, so any old/loaded brain generalizes on first query.
- **Test:** build a brain with feature-facts + valence set the OLD way (direct `valence[...]`, no
  learner), save in the legacy format, load, then `predict_valence` on UNTAUGHT related concepts.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J440a (backfill generalizes):** after loading an energy-less brain with stored valence,
  `predict_valence` on untaught related concepts is ≥ 0.80 accurate, both seeds.
- **J440b (no corruption of taught):** taught entities still return their exact stored valence, both seeds.
- **J440c (empty stays empty):** a brain with no valence at all → `predict_valence` returns None and
  no learner is created.

Predicted PASS: existing brains gain affect generalization for free via backfill. NULL if J440a fails
(stored valence is too sparse/feature-poor to generalize). Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | backfilled | held-out untaught | taught exact | empty→None |
|------|------------|-------------------|--------------|------------|
| 0 | True | 0.980 | True | True |
| 7 | True | 0.940 | True | True |

J440a ✓ · J440b ✓ · J440c ✓ → **PASS, both seeds.** substrate_memory 14/14 + conversation 10/10 green.

## Verdict: existing brains gain affect generalization for free
A brain whose valence was set the old way (no learner) — saved in legacy format, reloaded — now
trains the energy model from its stored `(entity_cloud, valence)` pairs on the first
`predict_valence` and generalizes to untaught related concepts at 0.94–0.98, with taught values
intact and no learner created for a valence-free store. Michael's live GUI brain therefore gains
affect generalization over everything already taught, with zero re-teaching. Established methods,
named — integration only, NOT new science.
