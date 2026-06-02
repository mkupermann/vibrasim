# G59 — Steady-state disturbance rejection: does the controller hold a bounded, proportional offset?

Pre-registered: 2026-06-02 (BEFORE the run). G58 established the proto-cell as a first-order linear
homeostatic controller (transient τ ≈ 75 ticks, magnitude-independent). The complementary
steady-state test: under SUSTAINED foreign influx into the interior (mimicking continuous internal
production), a first-order controller reaches a bounded steady-state N_ss = influx · τ — i.e. the
interior offset scales LINEARLY with the influx rate and never runs away (disturbance rejection).

## Method
Proto-cell (G30 membrane + G32 channel ON, pre-cleared). Then inject foreign vibrations into the
interior at a CONSTANT rate (n per tick) for the whole window; measure the steady-state interior
incompatible concentration (mean over last third). Rates {2, 4, 8} per tick. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G59a | Bounded (rejection) | steady-state interior conc < 0.5 at every rate, both seeds (does not run away) |
| G59b | Proportional (linear gain) | ss(rate 8)/ss(rate 2) ∈ [2.5, 5.5] (≈4×, first-order proportional), both seeds |

PASS = G59a–b → the proto-cell rejects a sustained disturbance with a bounded, influx-proportional
offset: a complete first-order linear controller (transient τ from G58 + proportional steady-state
gain here). NULL: if G59a fails the interior runs away at high influx (clearance saturates); if
G59b fails the offset is not proportional (nonlinear gain). Honest characterization either way.
No post-hoc threshold tuning.

## RESULT (2026-06-02): PASS — bounded, influx-proportional offset (complete first-order controller)

| seed | ss @ influx 2/4/8 | gain (8/2) |
|------|--------------------|------------|
| 42 | 0.122 / 0.238 / 0.472 | 3.88 |
| 7 | 0.106 / 0.234 / 0.459 | 4.35 |

G59a ✓ (bounded <0.5), G59b ✓ (gain ≈4 = proportional). **PASS.** Steady-state interior offset
scales linearly with influx rate (doubling influx ≈ doubles the offset) and never runs away —
exactly the first-order prediction ss = influx·τ. Combined with G58 (magnitude-independent transient
τ≈75 ticks), the proto-cell is a COMPLETELY characterized first-order linear homeostatic controller:
step response + DC gain both confirmed. A clean substrate-level analog control primitive.
