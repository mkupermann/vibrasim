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
