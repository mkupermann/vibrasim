# G82 — Instantaneous spatial XOR, proper readout (free-vibration grid)

Pre-registered: 2026-06-03 (BEFORE the run). Fixes G81's confound (atom-charge state didn't encode
input). Read FREE-VIBRATION density per 3x3x3 grid — injected vibrations sit where placed, so the
state reliably encodes the input (sanity should pass). Two CLOSE input regions (x=8, x=14) so their
vibrations meet and bind in the middle → the middle bin reflects A*B, the interaction feature XOR
needs. Raw binding substrate (no channel). Held-out balanced accuracy, 240 trials, seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| sanity | Single input readable | reading input A alone ≥ 0.65, both seeds (state encodes input) |
| G82a | Instantaneous spatial XOR | held-out balanced accuracy ≥ 0.65, both seeds |

PASS = G82a → the memoryless substrate computes instantaneous spatial XOR (nonlinear multi-input
logic from binding interaction). NULL with sanity PASS = inputs readable but XOR not → the substrate
reads inputs but cannot combine them nonlinearly into a separable representation (LINEAR-only spatial
computation). INCONCLUSIVE if sanity fails again. Honest either way. No post-hoc tuning.

## RESULT (2026-06-03): INCONCLUSIVE — input drowned by the substrate's self-activity (the ROOT)

| seed | spatial XOR | single-input(A) sanity |
|------|-------------|------------------------|
| 42 | 0.56 | 0.48 |
| 7 | 0.52 | 0.40 |

Sanity FAILED again — even the free-vibration grid doesn't encode which input was driven. The reason
is the deep ROOT: the substrate's HOMOGENEOUS SELF-ACTIVITY (300+ ambient vibrations + a churning
lattice) drowns the localized injected input. The same root that blocks everything: memory (control
never blank), reservoir (no clean state-encoding), and now multi-input computation (input doesn't
register). It also explains why the PROTO-CELL computations (G75/G76) DID work — the channel PROTECTS
the interior, a QUIET low-background region where the input stands out. Decisive next test (G83): a
QUIET substrate (minimal background activity) should let the input register (sanity pass) and could
unlock memory/computation. The homogeneous-activity root is the single lever.
