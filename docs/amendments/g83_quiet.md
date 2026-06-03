# G83 — Quiet substrate: testing the homogeneous-activity ROOT

Pre-registered: 2026-06-03 (BEFORE the run). G81/G82 showed the substrate's self-activity drowns a
localized input (sanity always fails). Hypothesis: a QUIET substrate (background culled, lambda_gen=0,
but the atom lattice kept for binding nonlinearity) will let the input REGISTER. Same spatial-XOR
setup; free-vibration grid read; background re-culled between trials. Held-out balanced accuracy.
Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| sanity | Quiet substrate registers input | single-input(A) accuracy ≥ 0.70, both seeds |
| G83a | Quiet substrate spatial XOR | held-out balanced accuracy ≥ 0.65, both seeds |

PASS = G83a → a quiet substrate computes spatial XOR: the homogeneous-activity ROOT is confirmed AND
removing it unlocks computation. PARTIAL = sanity passes but XOR fails → root confirmed (quiet
substrate registers input where the active one drowned it) but no nonlinear interaction for XOR.
NULL = even quiet, input doesn't register → the root is elsewhere. Honest either way. No post-hoc
tuning. If the root is confirmed, the path forward for memory/computation is a QUIET/SPARSE substrate
architecture (atoms silent unless driven).

## RESULT (2026-06-03): PARTIAL — ROOT CONFIRMED (quiet substrate registers input perfectly)

| seed | single-input(A) sanity | spatial XOR |
|------|------------------------|-------------|
| 42 | 1.00 | 0.71 |
| 7 | 1.00 | 0.51 |

Sanity = **1.00 both seeds** (vs ≈chance 0.48/0.40 on the ACTIVE substrate, G82). **The
homogeneous-activity ROOT is causally confirmed:** quieting the background makes a localized input
PERFECTLY readable. The substrate's own self-activity was drowning every signal — the single root of
the memory, reservoir, AND computation failures. XOR is borderline (0.71 seed 42, 0.51 seed 7): the
LINEAR input encoding is perfect, but the NONLINEAR interaction (A·B) is weak (inputs at x=8,14 may
not mix enough in 8 ticks).

**Implication (major).** The architectural lever for ALL of it is a QUIET/SPARSE substrate. And the
memory deadlock I concluded "fundamental" (G33-G73) was measured on the ACTIVE substrate where
control is never blank — on a QUIET substrate, control IS blank, so selective memory may be possible.
Next: G84 strengthens the XOR interaction (overlapping inputs) on the quiet substrate; then RETEST
MEMORY on a quiet substrate (the root that blocked it is now removable).
