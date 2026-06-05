# JEP-242 — CAPSTONE: the FULL multi-relation Understanding Engine reasons through the substrate, from one prose passage

Pre-registered 2026-06-05 (BEFORE the run). JEP-235 ran is-a through the substrate from prose; JEP-232..241 proved
store/chain/type/DAG/interaction/online/aggregation in isolation. This capstone integrates them: read ONE real
multi-domain passage, store ALL relation types (is-a, part-of, causal, comparison, temporal) in ONE typed substrate
net, and answer a Q&A battery across every relation type — multi-hop chains + the part-of × is-a interaction — by
substrate retrieval, matching the symbolic engine. The substrate as a drop-in relational backend for the whole engine.

## Method (no transformer)
- `e.read(passage)` → the engine's symbolic relation stores (`parents`, `part_of_g`, `causes`, `_orders[bigger|before]`).
  Edges are single-valued per (subject, relation) by passage construction (chains), so the basic typed store suffices.
- Store every edge `(subject, relation, object)` as `concat(subject_code ⊙ relation_code, object_code)` in ONE
  EnergyNet (JEP-234 typed binding). Total edges ≤ ~18 (within the JEP-232 ~20 capacity).
- ANSWER through the substrate: chain a relation by iterated retrieval keyed by that relation (JEP-233/234), gated by
  retrieval overlap (JEP-235 SIM_STOP); part-of × is-a interaction by composing a part-of hop with the is-a chain
  (JEP-238). Battery: is-a multi-hop, part-of (+interaction), causal chain, comparison chain, temporal chain, each
  with negatives. Ground truth = the engine's symbolic `is_a / part_of / causes_effect / _order_holds`. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J242a | All relation types answered via substrate | battery match vs symbolic ≥ 0.90 over all relation types (both seeds) |
| J242b | Multi-hop in EACH type | a depth≥3 positive resolves through the substrate for is-a AND comparison AND (causal or temporal) (both seeds) |
| J242c | Interaction holds | part-of × is-a UP ("a heart is part of an animal") = True via substrate, leak guard False (both seeds) |
| J242d | Above an untrained control | untrained net battery match ≤ 0.60 (both seeds) |

PASS = J242a–d → the full multi-relation engine reasons through the substrate from real prose. NULL (honest): J242a
fails → cross-relation interference in the shared net or a chaining desync; J242c fails → composition breaks; J242d
fails → readout trivial. No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS. Each piece is proven: typed binding separates relations with no crosstalk (234), chaining is 1.00 within
capacity (233), the interaction composes (238), and ≤18 total edges sit within the ~20 capacity. So the integrated
battery matches symbolic ≥ 0.90 (~1.00), multi-hop resolves in each type (J242b), the interaction + leak guard hold
(J242c), control fails (J242d). RISK (integration, in-rung): (i) shared capacity is over ALL edges now — keep ≤ ~18;
(ii) the chain stop-gate must fire per relation so a chain doesn't run past its root into a spurious cross-relation
hop — verify negatives (a wrong-type or off-chain target returns False); (iii) order relations (bigger/before) are
directional — store x→y as the smaller/earlier mapping consistently. Established (typed Hopfield CAM + iterated
recall + composition), named; no novelty — the value is the integrated demonstration that the WHOLE engine, not just
is-a, runs on the energy substrate from real prose.

## RESULT (2026-06-05): PARTIAL — the full engine runs through the substrate; the 2-step INTERACTION is brittle on one seed

| seed | battery match | control | deep multi-hop (all types) | interaction + leak |
|------|---------------|---------|----------------------------|--------------------|
| 42 | 1.00 | 0.33 | True | True |
| 7  | 0.93 | 0.33 | True | False |

- **J242a ✓** — the battery across ALL relation types (is-a, part-of, causal, comparison, temporal — multi-hop +
  negatives) answered by substrate retrieval matches the symbolic engine **1.00 / 0.93**, both ≥ 0.90. The whole
  engine, not just is-a, runs on one typed substrate net from real prose.
- **J242b ✓** — depth-3 positives resolve through the substrate in is-a AND comparison AND temporal, both seeds.
- **J242c ✗** — the part-of × is-a interaction holds on seed 42 but FAILS on seed 7. The interaction is a TWO-step
  composition (a part-of hop THEN an is-a chain); seed 7 has one occasional single-retrieval flake (the same 0.93
  imperfection as its battery), and a 2-step composition has no redundancy to absorb it → the conjunction breaks.
- **J242d ✓** — untrained control 0.33.

**FINDING:** the FULL multi-relation Understanding Engine reasons through the substrate from one real multi-domain
passage — is-a, part-of, causal, comparison, temporal, multi-hop in each, all from one typed EnergyNet (10 edges,
within capacity), matching the symbolic engine (1.00 / 0.93). The honest gap is ROBUSTNESS of COMPOSED multi-step
queries: a single-retrieval flake (seed 7) breaks the 2-step interaction, because a bare composition has no
redundancy. This is exactly the JEP-240/241 lesson surfacing at the integration level — per-hop AGGREGATION (the
JEP-241 cure) is the indicated robustness fix for composed substrate queries (NOT verified cleanly here: my quick
aggregated check dropped the SIM_STOP chain-gate and was invalid; deferred). Verdict: **PARTIAL** (a/b/d PASS; c
fails on one seed — the integration works, composed-query robustness is the residual). predict-calibrate: I predicted
a clean PASS; the J242c miss is the integration risk (ii) I flagged (chain/compose robustness) materializing on the
flakier seed — recorded, not retuned. Established (typed Hopfield CAM + iterated recall + composition), named; no
novelty — the value is the integrated demonstration that the whole engine runs on the energy substrate from prose,
with the composed-query robustness gap honestly marked.
