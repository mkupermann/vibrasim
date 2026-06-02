# G58 — Homeostatic controller dynamics: is interior clearance first-order (linear)?

Pre-registered: 2026-06-02 (BEFORE the run). G44 showed the proto-cell RESTORES its interior after
a foreign bolus. Fresh dynamical question (orthogonal to the mapped frontiers): WHAT KIND of
controller is it? If interior clearance is FIRST-ORDER — exponential decay with a time-constant
INDEPENDENT of perturbation magnitude — the proto-cell is a clean linear homeostatic controller
(clearance rate ∝ amount present, the signature of passive selective efflux). Characterizing this
turns the qualitative G44 result into a quantitative control-theoretic property.

## Method
G30 membrane + G32 channel (proto-cell), channel ON, pre-cleared to set-point. Inject foreign
boluses of three sizes (60, 120, 240) into the interior; record interior incompatible concentration
each tick through the recovery. For each size, fit the per-tick clearance time-constant τ (ticks to
decay from peak to 1/e·peak). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G58a | Recovers at every magnitude | interior decays to ≤ 0.3·peak by end, all 3 sizes, both seeds |
| G58b | First-order (magnitude-independent rate) | τ consistent across sizes: max(τ)/min(τ) ≤ 1.6 (both seeds) |

PASS = G58a–b → the proto-cell is a first-order LINEAR homeostatic controller (clearance rate
independent of load = passive selective efflux). A clean quantitative control property of the
proto-cell. NULL: if G58a fails it does not recover at some magnitude (saturable clearance); if
G58b fails τ depends on magnitude (nonlinear controller). Either is an honest characterization.
No post-hoc threshold tuning.

## RESULT (2026-06-02): PASS — first-order LINEAR homeostatic controller

| seed | τ (bolus 60/120/240) | τ ratio | end/peak (all sizes) |
|------|----------------------|---------|----------------------|
| 42 | 77 / 74 / 72 | 1.07 | 0.01–0.06 |
| 7 | 73 / 83 / 74 | 1.14 | 0.02–0.05 |

G58a ✓ (recovers at every magnitude), G58b ✓ (τ magnitude-independent). **PASS.** Peak scales
exactly linearly with bolus (0.053/0.105/0.208 for 60/120/240) and the clearance time-constant is
constant (~75 ticks) regardless of load. The proto-cell is a clean FIRST-ORDER LINEAR homeostatic
controller — clearance rate ∝ amount present (passive selective efflux through the channel). A
quantitative control-theoretic property on top of the qualitative regulation (G44), robust across
seeds.
