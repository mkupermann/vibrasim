# G29 — Removing the frequency rule entirely BREAKS the substrate

Pre-registered: 2026-05-31 (BEFORE the run). Michael: the 8% rule is gone — drop it.
Taken literally: remove the frequency gate at every level (binding = proximity +
polarity only; freq window [0, 100] ≈ accept all; node_freq_binding=False), keep the
membrane machinery, measure whether the substrate still climbs.

## RESULT (2026-05-31): NULL — the rule is load-bearing, not just a bottleneck

| seed | peak atoms | molecules | species | bridges | max chain |
|------|-----------|-----------|---------|---------|-----------|
| 42 | 0 | 0 | 0 | 0 | 0 |
| 7 | 0 | 0 | 0 | 0 | 0 |
| 99 | 58 | 0 | 0 | 87 | 58 |

G29a ✗, G29b ✗, G29c ✗ → **NULL**. With NO frequency rule the substrate is erratic and
broken: 2 of 3 seeds produce NOTHING, and the one that makes atoms (58) produces ZERO
molecules. Without frequency selectivity the hierarchy cannot climb reliably or
reproducibly — and cannot reach molecules at all.

## Conclusion (honest, answers the directive)
The frequency-compatibility rule is the STRUCTURING PRINCIPLE (CONCEPT §3: "binding is
the only structuring principle"), not merely a bottleneck to delete. You cannot remove
it — the substrate collapses (G29). What WORKS is keeping frequency selectivity but
WIDENING the window: G27's ±2 % window (vs the original ±0.5 %) gave 195–203 atoms and
636–649 molecules robustly across seeds — 12× atoms, 22× molecules.

So "the 8 % rule is gone" is honestly realized as: the specific over-narrow 0.08 ±
0.005 value is REPLACED by a broader compatibility window (≈ ±2 %), NOT removed. The
rule, broadened, is the engine of the hierarchy; deleted, the hierarchy dies. The data
says WIDEN, don't DELETE.
