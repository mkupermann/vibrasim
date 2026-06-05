# JEP-306 — Integrated reasoning at scale: the honest operating envelope

## Motivation
JEP-294…305 validated each capability on small, clean stores. Characterize the INTEGRATED system at scale: a large
generated taxonomy (is-a forest) with inherited properties and exceptions, bridged into the durable GROWING
substrate (neurogenesis on), reasoned over (multi-hop is-a + defeasible property), vs the generated ground truth —
measuring where accuracy degrades. Finds the real envelope, not a single tuned point. No transformer.

## Method
Generate a controlled forest of is-a trees (branching b, depth d) over N concepts; attach properties to internal
nodes (inherited by descendants) and inject exceptions (a descendant with `not_hasprop` for an inherited prop).
Ground truth = transitive closure + most-specific-explicit-wins, computed directly from the generated graph.
Bridge all facts into `SubstrateMemory(D=4096, directed=True)` (auto-modules); sweep N; score multi-hop is-a +
defeasible property vs ground truth; reload and re-score.

## Pre-registered bars (BEFORE the run)
- **J306a (holds at moderate scale):** at N = 200 facts, integrated accuracy (is-a multi-hop + defeasible
  property, balanced) ≥ 0.90 vs ground truth, both seeds (0, 7).
- **J306b (envelope characterized):** report accuracy vs N for N ∈ {50,100,200,400,800}; identify N* where it
  first drops below 0.90 (a capacity finding — reported, never tuned). Neurogenesis must engage (≥2 modules at the
  larger N).
- **J306c (persists at scale):** at N = 200, reloaded-store accuracy equals pre-save (±0.01), both seeds.

Predicted most-likely failure: as N grows, per-fact similarity falls ~1/√(facts-per-module); the global gate
(calibrated once) may mis-fire, dropping deep multi-hop positives first. Expected: accuracy high until modules
fill, a soft decline thereafter — N* reported honestly. If even N=200 misses 0.90, the modular cap (0.8·D/32) is
too high → report, don't retune.

## Result (seeds 0, 7): **NULL / PARTIAL** — a real envelope finding
Envelope (integrated = mean of is-a multi-hop + defeasible property):

| N (facts) | modules | is-a acc | property acc | integrated |
|-----------|---------|----------|--------------|------------|
| ~50  | 1 | 1.00 | 1.00 | 1.00 |
| ~110 | 2 | 0.50 | 0.94 | 0.72 |
| ~230 | 3 | 0.51 | 0.96 | 0.74 |
| ~460 | 5 | 0.60 | 0.98 | 0.80 |
| ~910 | 9 | 0.79 | 1.00 | 0.88 |

- **J306a (≥0.90 at N=200): FAIL** — integrated ≈ 0.74, driven by is-a multi-hop ≈ 0.51.
- **J306b:** envelope characterized; **N\* (first <0.90) = ~100** (the 1→2 module boundary). Neurogenesis engages
  (9 modules at N=800). **Reported.**
- **J306c (persists at scale): PASS** (±0.01 on reload).

### Diagnosis (probed, two causes)
1. **Gate mis-calibration:** the calibration facts landed in the near-empty LAST module (high sim ~0.27), but real
   facts in FULL modules have sim ~0.13 < gate → true parents rejected. Forcing a single large module restored
   is-a to 0.83/0.97 at N=100; recalibrating the gate on REAL stored edges across modules lifted N=100 to
   0.79/0.96. So the global-gate-on-synthetic-calib was part of the failure.
2. **Residual cross-module multi-hop fragility:** even with the edge-calibrated gate, is-a multi-hop PLATEAUS at
   ~0.75–0.83 for N≥200 (vs property 0.96–1.0). A chained climb takes the GLOBAL argmax per hop; per-module sim
   varies and one hijacked hop breaks the whole chain. Single-step recall and membership/leaf checks (property,
   `contains`) stay robust to N=800.

## Verdict: **NULL / PARTIAL** (valid finding, not retried)
Honest envelope: the durable modular store scales well for **single-step recall and membership/inheritance-leaf
reasoning** (property robust to ~900 facts / 9 modules), but **deep multi-hop CHAINING is effectively
single-module-bounded** (~K*≈128 facts) — beyond that, cross-module crosstalk + per-hop similarity decay + gate
sensitivity erode it. This refines the JEP-296 "unbounded growth" claim: it holds for what JEP-296 measured
(single-step recall), NOT for multi-hop chains. Fix pre-registered as **JEP-307**: edge-calibrated gate +
module-aware climbing (route each hop to the module holding the fact) to remove cross-module argmax hijacking.

