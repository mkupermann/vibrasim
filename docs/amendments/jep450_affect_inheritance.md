# JEP-450 — Affect inherits through the taxonomy (explainable inherited valence)

## Motivation
Valence is currently per-entity (`sm.valence`) and does NOT flow through the is-a hierarchy: teach
"reptiles are scary" + "a snake is a reptile", and the brain still cannot say a snake is scary. But
energies should flow through concept relationships — a kind-of inherits its parent's affect. JEP-450
wires affect to ride the existing taxonomy reasoning: `predict_valence` climbs is-a to the nearest
valenced ancestor, and the brain can EXPLAIN it ("a snake feels dark because it is a reptile"). This
combines two subsystems never combined — symbolic taxonomy reasoning + the affect model. Established
(inheritance reasoning + valence), named; the contribution is the integration. No transformer.

## Method (`world/substrate_memory.py`, `world/brain_query.py`, `tools/run_jep450_affect_inheritance.py`)
- `SubstrateMemory._valenced_ancestor(entity)`: BFS up is-a edges (most-specific first) to the nearest
  ancestor with a taught valence.
- `predict_valence` order: own taught valence → inherited ancestor valence → energy-model
  generalization. (Inheritance is exact/symbolic; it precedes the statistical fallback.)
- `brain_query`: "why is X good/bad/scary?" → the valenced ancestor reason.
- **Live test (Conversation):** teach affect on a PARENT class + a taxonomy; query a child's affect
  and its explanation; a control branch whose ancestors have no affect must NOT inherit.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J450a (affect inherits):** after "snakes are scary"(parent) + "a cobra is a snake", the brain
  answers a cobra is scary (inherited valence < 0), both seeds.
- **J450b (it is explained):** "why is a cobra scary?" cites the valenced ancestor (snake), both seeds.
- **J450c (no spurious inheritance):** a child whose ancestors carry NO valence is reported neutral /
  not-scary (no false affect), both seeds; conversation 10/10 + substrate_memory 14/14 stay green.

Predicted PASS: affect flows through is-a with an explanation, and does not appear where no ancestor
carries it. NULL if J450a fails (inheritance not reaching the child) or J450c fails (spurious affect).
Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL/partial — two real findings (test-word + a fallback bug)

Run with "scary"/"dangerous": J450a ✗, J450b ✗, J450c ✓. Diagnosis (verified):
1. **"scary"/"dangerous" are NOT affect-lexicon words** → they are stored as PROPERTIES, and property
   inheritance ALREADY answers "is a cobra scary?" → Yes. So valence inheritance was never exercised.
   With a real lexicon word ("Snakes are evil") the new mechanism works: `energy(cobra)` and
   `energy(python)` → dark, and "why is a cobra evil?" → **"because cobra is a kind of snake"** (J450a/b
   would pass).
2. **The energy-model FALLBACK hallucinates affect** (the J450c risk, surfaced): with the lexicon
   word, `energy(desk)` → "dark (generalized)" even though desk has NO valenced ancestor — because the
   backfilled reservoir, trained on a SINGLE negative example (snake=−1), is degenerate and predicts
   negative for everything. This is a pre-existing eager-fallback bug (the JEP-436 generalization
   always fires once any valence exists), surfaced by JEP-450's control.

So the inheritance + explanation are correct, but predict_valence's statistical fallback must ABSTAIN
when its training is too sparse/one-sided. Pre-registered as **JEP-451**: gate the energy-model
fallback (require ≥ a minimum number of valenced concepts spanning BOTH polarities, else return
neutral) and re-run the inheritance test with a lexicon affect word. Recorded NULL/partial against
the locked bars; no retuning.
