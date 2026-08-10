# PRIM14-D2 — pure attractor test with the write channel closed

**Status: SIGNED OFF 2026-08-10 — committed before any data generation (D2 rule).
Bars final per D3.**

## 1. The one question (D1 rule)

> With bond formation disabled during the probe (valence saturation — no new
> physics), does the per-bond rest length hold its quantitative equilibrium
> prediction: displaced middle settles at the STORED position (x=17) under
> per-bond rest, and at the global-rule equilibrium (x=19) under global r_eq —
> each within ±0.4?

Context: D0 (PARTIAL) and D1 (NULL) were both contaminated by measurement-write
coupling — a second bond formed DURING the probe at the displaced geometry
(LOGBOOK 2026-08-10). D2 closes that channel: `atom_valence=1`, so the single
consolidation bond (13↔17, rest 4) saturates both endpoints and the relax phase
cannot write. This turns the diagnostic into a falsifiable point prediction per
arm instead of the D0/D1 recovery fraction (whose ARM-C ≤ 0.2 bar breaks on
single-bond topology: the global rule also pulls toward the stored side).

## 2. Protocol

Chain {13, 17, 29}, `atom_valence=1`, consolidation 8 ticks (forms exactly the
13↔17 bond, rest 4; verified bond census before displacement — a bond count ≠ 1
or endpoints ≠ {0,1} makes the run INVALID, engineering stop). Displace middle
17 → 21, release, 2000 ticks, ends pinned. Seeds {42, 7, 13} (deterministic
regime). Dynamics: k=8.0, damping=0.95 (a D1-stable fast cell — fixed here,
not tuned later). Bond census re-checked after relax: any new bond = INVALID.

Arms:
- **ARM-P:** per_bond_rest_enabled=True → predicted equilibrium x* = 13+4 = 17.
- **ARM-C:** flag off (global r_eq=6) → predicted x* = 13+6 = 19.
- **NC (no-bond):** ARM-P setup, bridges deleted after displacement → middle
  must stay at 21 ± 0.4 (no hidden force).

## 3. Pre-registered bars (fixed before any data)

On 3/3 seeds:
- **PASS:** |x_P(2000) − 17| ≤ 0.4 AND |x_C(2000) − 19| ≤ 0.4 AND
  NC stays 21 ± 0.4 AND both arms settled (|x(2000) − x(1500)| < 0.1).
- **PARTIAL:** both arms settled and separated by ≥ 1.0 in the predicted
  ORDER (x_P < x_C), but at least one misses its ±0.4 window.
- **NULL:** arms not separated by ≥ 1.0, or not settled at 2000 ticks.
- **FAIL:** bond census violated (write channel not actually closed — the
  design premise is wrong), or NC moves > 0.4 (hidden force), or separation
  in the WRONG order (x_P > x_C — mechanism backwards).

## 4. Predictions (calibration, before data)

- Bond census holds (valence saturation works): 85%.
- PASS: 60%; PARTIAL 20% (springs settle slightly off-prediction — e.g.
  discrete-tick offset or the pinned end's re-zeroing biasing equilibrium);
  NULL 8%; FAIL 12% (valence rule may not gate bridge formation the way
  assumed — that would itself be a finding).
- Most-likely failure mode: bridge formation ignores atom_valence in this
  code path → FAIL via bond census, revealing the write channel needs an
  explicit freeze flag instead.

## 5. Budget

Harness variant of run_bp_prim14_d0.py: 20 min. Runs: minutes. Verdict +
LOGBOOK + FRONTIER: 30 min. **Realistic 1 h → hard cap 2 h.**

## 6. Out of scope

Recall-by-content, multi-bond patterns, adaptive rest, any parameter beyond
the two fixed dynamics values, matrix sweeps.
