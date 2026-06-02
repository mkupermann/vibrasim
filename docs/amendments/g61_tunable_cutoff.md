# G61 — Tunable cutoff: does the filter time-constant scale with membrane size?

Pre-registered: 2026-06-02 (BEFORE the run). The proto-cell is a first-order low-pass controller
(G58–G60) with τ≈75 ticks on the box-22 membrane (R≈11). If τ is set by the interior size (bigger
interior → longer clearance), the filter cutoff (~1/τ) is TUNABLE by membrane size — making the
proto-cell a tunable analog element. Test τ on the small (box-22, R≈11) vs large (box-33, R≈16.5,
from G51) emergent membrane.

## Method
Measure interior-foreign clearance τ (G58 method: pre-clear → bolus 120 → ticks-to-1/e) on two
emergent membranes: box-22 (g43 cfg, R≈11) and box-33 (g51 cfg, R≈16.5). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G61a | Both recover | interior decays to ≤0.3·peak by end on both membranes, both seeds |
| G61b | τ scales with size | τ(large)/τ(small) ≥ 1.3 (larger membrane → longer τ), both seeds |

PASS = G61a–b → the filter time-constant scales with membrane size: the proto-cell's low-pass
cutoff is TUNABLE by the (emergent) membrane radius — a substrate-level design law for an analog
filter. NULL: if τ does not scale with size (G61b fails), the clearance rate is set by something
else (boundary efflux speed, not interior volume) — an honest negative on tunability-by-size. No
post-hoc threshold tuning.

## RESULT (2026-06-02): PASS — τ ∝ R (cutoff tunable by membrane size)

| seed | small R / τ | large R / τ | τ ratio (R ratio ≈1.5) |
|------|-------------|-------------|------------------------|
| 42 | 10.9 / 80 | 16.5 / 124 | 1.55 |
| 7 | 11.1 / 79 | 16.9 / 122 | 1.54 |

G61a ✓, G61b ✓ → **PASS.** τ scales ~linearly with membrane radius (R up 1.5× → τ up 1.55×),
both seeds — consistent with clearance time = interior size / efflux speed (τ ∝ R). The proto-cell's
low-pass cutoff (~1/τ) is TUNABLE by the emergent membrane radius: a substrate-level design law for
an analog filter. The proto-cell is a fully characterized, TUNABLE first-order analog low-pass element.
