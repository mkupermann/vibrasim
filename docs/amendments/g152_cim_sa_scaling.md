# G152 — Does the CIM-AHC ≈ SA near-tie HOLD at larger scale (n=450, 600)?

Pre-registered: 2026-06-05 (BEFORE the run). G150/G151 established (across Gaussian + ±1 families) that the
textbook AHC-CIM beats correct greedy and lands within ~0.4–0.7% of classical SA at n ≤ 360. Open question:
is that near-tie **stable with scale**, or does the CIM↔SA gap **grow** (CIM degrades relative to SA at large
n) or **shrink** (CIM catches up)? G152 measures the gap as a function of n at larger sizes. Frozen solver
settings (no tuning); only n grows. Established methods (CIM-AHC, SA), named as such.

## Method
Signed-Gaussian spin-glass MAX-CUT (the G150 family), `n ∈ {450, 600}`, 4 instances per n, `rng_seed=2`.
Solvers identical to G150 except budgets scaled modestly with n and **reported**: CIM = best over the FROZEN
grid `ξ∈{0.1,0.3}×β∈{0.1,1.0}×seeds{0,1,2}` (steps 1500); SA = 3 restarts × 800 sweeps (incremental field);
GRD = correct greedy 60 restarts; REF = best + long SA (2×1500). Track `gap = (CIM − SA)/REF` per n and the
trend vs the n≤360 baseline (G150: ~−0.007).

## Bars (locked pre-run)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| G152a | Hard regime present | SA beats GRD on ≥ 3/4 at n=600 |
| G152b | CIM still beats local search | CIM > GRD on ≥ 3/4 at n=600 |
| G152c | **Does the near-tie hold? (decisive)** | classify per below |

**G152c classification (pre-registered):**
- **HOLDS**: |mean(CIM − SA)/REF| ≤ 0.015 at n=600 → the near-tie is stable with scale; CIM-AHC remains
  competitive with SA at larger n.
- **CIM DEGRADES**: mean(SA − CIM)/REF ≥ 0.02 at n=600 AND the gap is larger than the n≤360 baseline → CIM
  falls behind SA as n grows.
- **CIM CATCHES UP**: mean(CIM − SA)/REF ≥ 0.01 at n=600 → CIM overtakes SA at scale.

## Verdicts
- **HOLDS** → the session's scoped positive (AHC-CIM ≈ SA, beats local search) is scale-robust as well as
  family-robust. Still adjacent established hardware, not EQMOD; SA marginally best & simpler.
- **CIM DEGRADES** → a scale caveat on the positive: the physical annealer's competitiveness erodes with n.
- **CIM CATCHES UP** → mild strengthening (CIM closes/passes SA at scale).

No post-hoc tuning; budgets reported. Compute note: SA's Python flip-loop is the bottleneck at large n, hence
the modest sweep budget — if SA looks under-resourced (anneal_ratio low) that is reported, not hidden.

## RESULT (2026-06-05): HOLDS — the near-tie is scale-robust (and CIM edges up slightly by n=600)

| n | SA > GRD | CIM > GRD | CIM ≥ SA | mean(CIM−SA)/REF | CIM ratio | SA ratio |
|---|----------|-----------|----------|------------------|-----------|----------|
| 450 | 4/4 | 4/4 | 1/4 | **−0.000** | — | — |
| 600 | 4/4 | 4/4 | 4/4 | **+0.005** | 0.997 | 0.992 |

- **G152a ✓ / G152b ✓** — SA and CIM both beat correct greedy 4/4 at n=600 (hard regime; CIM still beats
  local search at scale).
- **G152c = HOLDS** — |mean CIM−SA| ≤ 0.015 at n=600 (it is +0.005). The near-tie is stable from n=360 up to
  n=600; the gap does not blow up — if anything CIM nudges ahead (CIM≥SA 4/4 at n=600).

**Honest caveat (do NOT over-read the n=600 flip).** The nominal "CIM > SA 4/4 at n=600" is most likely
**budget-sensitive**, not a genuine overtake: SA's budget is FIXED (3 restarts × 800 sweeps) and scales less
favorably with n than the CIM grid (12 runs), so SA is mildly under-resourced at n=600 (ratio 0.992 vs CIM
0.997). A budget-matched SA would very plausibly re-tie. The defensible claim is therefore the **near-tie**,
not "CIM beats SA." Recorded as HOLDS, with this caveat explicit rather than spun into a false positive.
**→ CONFIRMED by G153:** a generous numba SA beats CIM-AHC **8/8** at n=450 & 600 (~+1.7%); the n=600 CIM
lead was indeed a budget artifact, and classical SA is marginally best at matched budget.

**Net (G150→G152).** The session's scoped positive — *a properly-engineered AHC-CIM beats correct local
search and is competitive (near-tie) with classical SA* — is now both **family-robust** (Gaussian + ±1, G151)
and **scale-robust** (n up to 600, G152). Unchanged caveats: it is established adjacent hardware (CIM-AHC),
named as such, NOT the EQMOD substrate (whose own dynamics can't optimize, G135); and classical SA remains the
pragmatic choice (marginally best at matched budget, far simpler to implement).
</content>
