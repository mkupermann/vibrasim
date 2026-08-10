# PRIM14-D1 — restore-dynamics regime matrix (tension_k × damping)

**Status: SIGNED OFF 2026-08-10 (condition: config plumbing committed before any run) — committed before data generation (D2). Bars final per D3.**

## 1. The one question (D1)

> Across a FIXED matrix of spring constant × velocity damping, does the
> per-bond-rest restore dynamics (PRIM14-D0: attractor confirmed, R=0.357 at
> 2000 ticks) reach PRACTICAL recovery — R ≥ 0.9 within the same 2000-tick
> window — in any regime, with the control contrast and stability intact?

Scope note: this is a DYNAMICS question on the already-verified mechanism.
It deliberately does NOT touch recall-by-content (a G154-style re-run stays a
separate future ID, admissible only if D1 finds practical restore times).

## 2. Engineering prerequisite (config plumbing, behaviour-preserving)

`apply_bridge_tension` hardcodes `tension_k = 0.5` and damping `0.95`
(world/bridges.py). Add config fields `bridge_tension_k: float = 0.5` and
`bridge_tension_damping: float = 0.95` (defaults = current literals →
bit-identical default behaviour; guarded by existing tests).

## 3. Protocol

Identical single-bond diagnostic as D0 post-erratum (stored chain {13,17,29},
ends pinned, middle displaced 17→21, release, 2000 ticks, metric
R = (4 − |x_mid − 17|)/4, seeds {42, 7, 13}; deterministic regime).

Fixed 3×3 matrix (no adaptive search; changes = new ID):

| | damping 0.90 | 0.95 (anchor) | 0.98 |
|---|---|---|---|
| **tension_k 0.5 (anchor)** | C-a | **C0 = D0 anchor** | C-b |
| **2.0** | C-c | C-d | C-e |
| **8.0** | C-f | C-g | C-h |

Arms per condition: **ARM-P** (per-bond on) and **ARM-C** (flag off, global
r_eq) — the control contrast must survive the regime change.

Stability (recorded, never hidden): a condition is **UNSTABLE** if
max|x_mid − 17| during relax exceeds 1.5 × the start displacement (6 units
from stored) or the endpoint has not settled (|x(2000) − x(1500)| ≥ 0.1).
Unstable conditions are ineligible for PASS/PARTIAL regardless of R.

## 4. Pre-registered bars (fixed before any data; D3)

Per condition (3/3 seeds, deterministic):
- **PRACTICAL:** ARM-P R ≥ 0.9, stable, AND ARM-C R ≤ 0.2.
- **IMPROVED:** ARM-P 0.5 ≤ R < 0.9, stable, ARM-C ≤ 0.2.

Overall verdict:
- **PASS:** ≥1 condition PRACTICAL.
- **PARTIAL:** none PRACTICAL, ≥1 IMPROVED.
- **NULL:** no condition reaches R ≥ 0.5 stable (dynamics not fixable inside
  this matrix; a wider matrix would be a new ID).
- **FAIL:** anchor C0 deviates from D0 (ARM-P R outside 0.357 ± 0.05) —
  reproduction failure, stop and investigate; or ARM-C ≥ 0.5 anywhere
  (contrast collapses — the mechanism claim itself is in doubt).

## 5. Predictions (calibration, before data)

- C0 reproduces D0: 95%.
- ≥1 PRACTICAL (→ PASS): 70% — terminal-velocity scaling suggests k=8 or
  damping 0.98 buys ~8–10× restore speed; overshoot risk is what the
  stability gate is for.
- Verdict distribution: PASS 70%, PARTIAL 15%, NULL 5%, FAIL 5%,
  everything-unstable 5%.
- Most-likely failure mode: high-k conditions oscillate (flagged UNSTABLE)
  while low-k stays slow → PARTIAL.

## 6. Budget (hybrid, §5)

Config plumbing 20 min, harness extension 20 min, runs minutes, verdict +
LOGBOOK + FRONTIER (D10) 30 min. **Realistic 1.5 h → hard cap 3 h.**

## 7. Out of scope

Recall-by-content, multi-bond/multi-cell patterns, adaptive rest lengths,
any matrix widening beyond the 9 registered cells, changes to the force law.
