# G151 — Does the G150 CIM finding GENERALIZE to a different hard family (±1 / SK spin glass)?

Pre-registered: 2026-06-05 (BEFORE the run). G150 (PARTIAL) found that the textbook AHC-CIM beats a correct
multi-restart greedy 5/5 and comes within ~0.7% of classical SA — but only on ONE instance family (signed
**Gaussian** spin-glass MAX-CUT, the G146–G150 ensemble). A single family can flatter or punish a solver.
G151 tests whether that result GENERALIZES to the canonical alternative hard family: **±1 (Bernoulli-signed)
weights** — the Sherrington–Kirkpatrick spin glass, the textbook hardest MAX-CUT ensemble. This is a
generalization/robustness check, NOT threshold-chasing: every solver setting (including the CIM-AHC grid) is
FROZEN identical to G150; only the instance distribution changes.

## Method
`W_ij ∈ {−1, +1}` uniform for i<j, symmetric (zero diagonal). `n ∈ {200, 360}`, 5 instances per n,
`rng_seed=2`. Solvers identical to G150:
- **OSC_naive** — G145 phase-only oscillator (best of 5 seeds).
- **CIM (AHC)** — Leleu/Yamamoto amplitude-correction, `J = −W/√n`, best over the FROZEN pre-registered grid
  `ξ∈{0.1,0.3} × β∈{0.1,1.0} × seeds{0,1,2}`, `p_max=2.0, a=1.0, dt=0.05, steps=1500` (all unchanged from G150).
- **SA** — classical Metropolis, 4×1000 sweeps.
- **GRD** — sign-correct greedy, 60 restarts.
- **REF** — best over all + long SA.

## Bars (locked pre-run — mirror G150, frozen)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| G151a | Hard regime present | SA beats GRD on ≥ 4/5 at n=360 |
| G151b | **Does G150 generalize? (decisive)** | classify per below at n=360 |
| G151c | AHC helps here too (sanity) | CIM ≥ OSC_naive on ≥ 3/5 at n=360 |

**G151b classification (pre-registered):**
- **GENERALIZES**: CIM > GRD on ≥ 4/5 AND |mean(CIM − SA)/REF| ≤ 0.01 → the G150 pattern (AHC-CIM beats
  local search and is ≈SA) holds on the ±1 family too → robust, not family-specific.
- **FAMILY-SPECIFIC**: CIM ≤ GRD (wins ≤ 3/5) OR mean(SA − CIM)/REF ≥ 0.02 → the G150 result does not carry
  to ±1 (CIM ties/loses greedy, or falls well behind SA) → it was Gaussian-specific.
- **PARTIAL/MIXED**: otherwise — report as such.

## Verdicts
- **GENERALIZES** → the "properly-engineered physical annealer beats local search, ≈ SA" finding is robust
  across the two canonical hard MAX-CUT ensembles. Strengthens G150's honest, scoped positive (still adjacent
  hardware, not EQMOD; SA still marginally best & simpler).
- **FAMILY-SPECIFIC** → G150 was Gaussian-specific; the physical-annealer edge is fragile across ensembles —
  an important caveat on the scoped positive.

No post-hoc tuning: all solver settings frozen from G150; only the instance family changes. Established methods
(CIM-AHC, SA), named as such.

## RESULT (2026-06-05): GENERALIZES — the G150 pattern holds on ±1 too

| n | SA > GRD | CIM > GRD | CIM ≥ SA (mean gap) | CIM ≥ naive |
|---|----------|-----------|---------------------|-------------|
| 200 | 5/5 | **5/5** | 2/5 (−0.004) | 4/5 |
| 360 | 4/5 | **4/5** | 2/5 (−0.004) | 5/5 |

- **G151a ✓** — SA beats correct greedy (5/5, 4/5): the ±1 hard regime is present.
- **G151b = GENERALIZES** — CIM beats correct greedy 4/5 at n=360 (5/5 at n=200) AND sits within ~0.4% of SA
  (|mean CIM−SA| = 0.004 ≤ 0.01), edging SA on 2/5. Same shape as G150's Gaussian result.
- **G151c ✓** — AHC ≥ naive on 4/5 and 5/5: the correction helps on ±1 too.

**The G146→G151 arc, settled and robust.** Across BOTH canonical hard MAX-CUT ensembles (Gaussian spin-glass
G146–G150; ±1 / SK spin-glass G151), the picture is consistent: G145's *naive* phase-only oscillator is weak
(ties correct greedy, loses to SA) and its "8/8" headline rested on a sign-bugged baseline; but the textbook
**AHC-corrected CIM** (Leleu/Yamamoto) is a *legitimate physical annealer* — it **beats correct local search**
and lands within ~0.4–0.7% of classical SA (a hair behind, occasionally edging it). Robust, not
family-specific. Unchanged caveats keep this honest and scoped: (1) classical **SA is still marginally best
AND far simpler**; (2) CIM-AHC is **established hardware**, named as such — no novelty; (3) it is **NOT the
EQMOD substrate** — EQMOD's own dynamics cannot optimize (G135), so "the EQMOD substrate is computationally
decorative" stands. The honest one-liner: *a correct physical Ising annealer is real and competitive with SA;
EQMOD is not that machine.*
</content>
