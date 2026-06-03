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
