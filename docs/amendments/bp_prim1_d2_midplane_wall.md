# PRIM1-D2 — Midplane / slab wall containment

**PRE-REGISTERED 2026-07-19 before data**  
**Depends on:** PRIM1-D0 leaky (χ≈0.43), PRIM1-D1 NULL (dual spheres χ≈0.41)  
**Discipline:** sharp — new geometry, not bar retune of D1’s 0.15

---

## Hypothesis

**H-D2.** A **reflecting midplane wall** at `x = mid` (free vibrations cannot cross) reduces occupation cross-talk χ to **≤ 0.15**, while both half-boxes still form ≥1 level≥4 node in ≥80% of trials.

Unlike dual spheres (D1), a slab separates the box into two half-volumes completely.

---

## Mechanism

Config (defaults OFF):

```text
midplane_wall_enabled: bool = False
midplane_wall_x: float = 40.0
```

When ON: after free-vibration motion each tick, any free vib that **crossed** the plane is reflected (reverse `v_x`, clamp position to the side it came from). Bound nodes unaffected.

---

## Bars (locked)

| ID | Criterion | thr |
|----|-----------|-----|
| P1 | mean χ (same definition as D0: tagged free wrong-side occupation fraction over train) with wall ON | ≤ **0.15** |
| P2 | both halves ≥1 level≥4 (wall ON) | ≥ **0.80** of trials |
| P3 | χ_on < χ_off (informative; must hold) | True |

Protocol: N=400/side inject, T=1200, seeds {171,173}, 2 trials, bands as C1b/D0.  
Compare wall ON vs OFF in same runner.

## Time budget
Estimate 20 min impl + 15 min run · 2× ceilings apply.

## Prediction
Prior ≈ 0.55 PASS if reflection is correct; NULL if tagging/spawn or periodic wrap still mixes sides.

## RESULT
**PASS** (2026-07-19) after wrap-bugfix.
chi_on=**0.000**, chi_off=0.430, pop=1.000. All bars met.
First D2 attempt NULL was implementation bug (periodic x wrap bypassed midplane); fixed in physics.apply_midplane_wall; re-run under same bars (not bar retune).

