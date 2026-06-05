# JEP-437 — Persist the energy model so generalized valence survives a reload

## Motivation
JEP-436 integrated the energy model but left it in-memory: after `save`→`load` the learner is gone,
so the substrate falls back to taught-only valence and loses its ability to predict the affect of
untaught concepts. Taught valence already persists; the generalization should too. JEP-437 persists
the learner (lightweight: seed + readout state; the random projection is re-seeded deterministically)
so a brain reopened across sessions keeps its learned affect generalization — matching the durability
of every other store in `SubstrateMemory`. Established methods; no new science. No transformer.

## Method (`world/substrate_memory.py` save/load + `tools/run_jep437_persist_energy.py`)
- **save:** if `self.energy` is set, write its readout state `w` (M+1) and `P` ((M+1)²) into
  vectors.npz, and `{present, seed, M}` into meta.json. The projection `R`,`b` are NOT stored — they
  are regenerated from `seed` on load (deterministic, cross-process stable), keeping save small.
- **load:** if energy present, reconstruct `ValenceReservoirLearner(n_inputs=D, n_features=M,
  seed=seed)` (rebuilds identical R,b) then overwrite `w`,`P` → byte-identical learner.
- **Test:** teach valence (train the model) → predict held-out untaught concepts → save → load →
  predict the SAME held-out concepts; predictions must be identical and accuracy preserved. Also a
  store with no energy must save/load cleanly (energy stays None).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J437a (round-trip exact):** for every held-out untaught concept, `predict_valence` after load
  equals before load (max abs diff < 1e-6), both seeds.
- **J437b (accuracy preserved):** held-out untaught sign-accuracy after load ≥ 0.80, both seeds.
- **J437c (no-energy store still round-trips):** a SubstrateMemory with no taught valence saves and
  loads with `energy is None` and no error.

Predicted PASS: the learner round-trips exactly and the generalization survives reload. NULL if
predictions drift (R/b not reproduced) — would indicate the seed-regeneration is not stable. Bars
locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | round-trip max│diff│ | acc after load | no-energy store ok |
|------|----------------------|----------------|--------------------|
| 0 | 0.00e+00 | 0.980 | True |
| 7 | 0.00e+00 | 0.990 | True |

J437a ✓ (byte-identical round-trip), J437b ✓ (accuracy preserved), J437c ✓ (no-energy store loads
clean) → **PASS, both seeds.** substrate_memory suite 14/14 green.

## Verdict: the energy model is now durable
Saving `w`,`P` + re-seeding `R`,`b` from the stored seed reconstructs a byte-identical learner
(max diff exactly 0.0), so the substrate's generalized affect survives `save`→`load` exactly like
taught valence, facts, and synonyms already do. A store that never taught valence saves and loads
with `energy is None` and no error (back-compatible). The JEP-436 integration is now complete and
durable across sessions. Established methods (deterministic hash-seeded random projection + RLS
state serialization), named — NOT new science.
