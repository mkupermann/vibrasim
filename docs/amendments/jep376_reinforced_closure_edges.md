# JEP-376 — Reinforce closure edges to close the faint-edge deep-recall gap

## Motivation
JEP-375 fixed negative is-a probes (skip the BFS on a consolidated store → neg 1.0) but exposed a complementary gap:
direct single-hop membership MISSES the faintest true ancestor edges whose cleanup similarity dips below the gate
(true-edge sim min ~0.022 vs gate ~0.027), so deep recall floats 0.93–0.97. The fix is to REINFORCE the materialized-
closure edges: store each derived ancestor edge with extra weight so its cleanup similarity rises above the gate, while
NEGATIVE probes (which reference no such edge) keep their headroom. `add_fact(weight=w)` scales a binding's
contribution; `consolidate_closure(reinforce=w)` applies it to the derived edges only. No transformer.

## Method
Re-run the JEP-375 end-to-end harness with `Conversation.consolidate()` using `reinforce=2.0`. Measure deep + negative
is-a via `Conversation.say()`, exceptions, persistence (save/load), non-consolidated multi-hop regression, and the
suite.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: reinforcing derived edges (weight 2×) lifts faint deep edges above the gate → deep recovers to ≥0.95 on
BOTH seeds, WHILE negatives stay ≥0.95 (the reinforcement adds coherent signal only to TRUE ancestor edges; random
non-ancestor probes are unaffected). Exceptions respected, persistence holds, multi-hop intact, suite green.

- **J376a (deep recovered):** deep is-a via `say()` ≥0.95, BOTH seeds (0, 7).
- **J376b (negatives stay fixed):** negative is-a via `say()` ≥0.95, BOTH seeds.
- **J376c (persist + exceptions + multi-hop + suite):** reload deep AND neg ≥0.95; exceptions respected; non-
  consolidated multi-hop is-a intact; `pytest -m "not slow" tests/test_conversation.py tests/test_substrate_memory.py`
  passes.

If reinforcing deep edges also lifts NEGATIVE false-positives back up (because the extra energy raises the crosstalk
floor), that is the honest trade-off to report — it would mean deep and negatives cannot both be maximized by
reinforcement alone. Predicted: 2× cleanly separates them. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **NULL — reinforcement is ineffective; root cause is sign() readout + genuine sim overlap**
- **J376a (deep recovered): NOT met** — deep is-a via `say()` = **0.933 / 0.967**, IDENTICAL to JEP-375 (no
  reinforcement). The 2× weight changed nothing.
- **J376b (negatives): borderline** — neg = 1.0 (seed 0) / **0.967 (seed 7)** — reinforcement slightly RAISED the
  crosstalk floor on one seed (extra bundle energy), the opposite of helping.
- **J376c: not met** (reload deep 0.9; same gap), multi-hop intact, exceptions respected, 23 tests pass.

### Diagnostic (the real finding)
Instrumenting the deep misses (seed 0, 2/30): both have the ancestor edge **materialized** but `edge_sim` BELOW the
gate — (xij→xf) sim 0.0195, (xhx→xb) sim 0.0232, gate 0.0272. Two compounding causes:
1. **sign() readout discards weight.** Modules are stored as a running sum but *read* as `sign(module)` (binarized
   ±1). Scaling a binding by 2× barely changes which sign wins per component, so reinforcement weight is essentially
   lost on read — that is why deep was unchanged. Reinforcement is the wrong tool under a sign-based bundle.
2. **Genuine similarity overlap for deep-many-ancestor nodes.** The missed nodes carry **8–10** materialized is-a
   edges, so the `(x,isa)` bundle is heavily loaded and each value's cleanup sim is diluted (~1/√load) — the faintest
   true edge (0.0195) sits BELOW the strongest false-pair sim (~0.035 measured earlier). The true and false single-hop
   distributions **overlap**, so no gate or reweight separates them cleanly.

## Verdict: **NULL — honest residual floor; stop chasing the last ~5%**
Reinforcement does not work because the bundle readout is binarized (sign), and the residual deep misses are a genuine
VSA capacity/overlap effect for the deepest nodes (those with ~10 ancestors), not a tunable gate. The within-domain
reliability arc is nonetheless a large, real win and should be recognized as substantially solved: consolidation took
**adversarial composition 0.4 → 0.87+ and deep is-a 0.85 → 0.93–0.97, with negatives 1.0** (JEP-370/375), all
end-to-end and persistent. The remaining ~3–7% on the very deepest queries is the honest floor of a sign-readout VSA
store at this scale; closing it would need a different readout (magnitude-preserving / normalized cleanup) — a larger
architectural change logged as future work, not pursued now (diminishing returns). `reinforce` reverted to 1.0; the
`weight` parameter is kept but documented as ineffective under sign() readout. Bars not moved. No transformer.
