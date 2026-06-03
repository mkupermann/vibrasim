# G74 — The substrate's nonlinear element: does the controller saturate?

Pre-registered: 2026-06-03 (BEFORE the run). The proto-cell controller is LINEAR in its tested
range (G58 step response, G59 DC gain — both linear up to influx 8). Linear elements can FILTER but
cannot COMPUTE (no decisions, no logic). A computing substrate needs a nonlinearity. The simplest
one to find here: push the sustained foreign influx far higher and look for SATURATION — a point
where clearance can't keep up and the steady-state stops scaling linearly (a limiter). Saturation =
the substrate's first computing nonlinearity, the building block for analog computation beyond
filtering.

## Method
Proto-cell disturbance-rejection (G59 machinery), sustained influx ∈ {4, 8, 16, 32, 64, 128}/tick.
Measure steady-state interior concentration; compute incremental gain ss/influx. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G74a | Saturation (nonlinearity) | ss/influx at the highest rate ≤ 0.6 × ss/influx at the lowest rate (gain drops ≥ 40% — sub-linear), both seeds |

PASS = G74a → the controller saturates: a nonlinear limiter, the substrate's first computing
nonlinearity (complements the linear filter — together they enable thresholding/decisions). NULL =
linear across the full range (no nonlinearity found this way → the analog element is purely linear,
and a nonlinearity must come from a different mechanism, e.g. the bistable bridge). Honest either
way. No post-hoc threshold tuning.

## RESULT (2026-06-03): PASS — the controller SATURATES (a clamped-linear nonlinearity)

| influx | seed 42 ss | seed 7 ss |
|--------|-----------|-----------|
| 4 / 8 / 16 | 0.24 / 0.47 / 0.98 | 0.23 / 0.46 / 0.93 |
| 32 / 64 / 128 | 1.56 / 1.56 / 1.56 | 1.46 / 1.46 / 1.46 |

Incremental gain ss/influx: 0.060 → 0.012 (seed 42), 0.059 → 0.011 (seed 7) — an ~80% drop. G74a ✓
→ **PASS.** The interior concentration scales LINEARLY up to influx ~16 then HARD-SATURATES at a
ceiling (~1.5, identical for influx 32/64/128). The proto-cell is a CLAMPED-LINEAR unit: linear for
small inputs, saturating for large — the upper half of a neuron-like activation function. This is
the substrate's first computing NONLINEARITY (clearance saturates: a natural limiter). Combined with
the tunable low-pass (linear), the substrate now has both a linear filter and a nonlinear limiter —
the building blocks for analog computation beyond filtering. Next: the lower threshold (bistable
bridge) to complete a full sigmoid/comparator activation.
