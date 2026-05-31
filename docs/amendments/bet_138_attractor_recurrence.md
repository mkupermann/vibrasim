# BET-138 — Attractor-stabilized recurrence: drift-free unbounded composition

Pre-registered: 2026-05-31 (BEFORE the run). BET-137 NULL: a naive local-rule
recurrent cell drifts and fails to length-generalize parity (0.493). Fix, fully
substrate-native: put the substrate's CONTENT-ADDRESSABLE ATTRACTOR (energy/cleanup
to the nearest clean state code) INSIDE the recurrent loop, so each step snaps the
state back onto a discrete code and error cannot accumulate.

Same parity task and protocol as BET-137 (train the XOR cell on the 4 single-step
transitions by a local rule; test on lengths 10..20 never trained). Single change:
after each transition step, CLEAN UP the state to the nearer of {E[even], E[odd]}
before the next step (the attractor as in-loop error correction).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T138a | Drift fixed, length-generalizes | attractor-recurrent acc on len 10..20 >= 0.95 |
| T138b | The attractor is what fixed it | naive (no in-loop cleanup) stays < 0.65 |
| T138c | Clear gap | T138a - T138b >= 0.30 |
| T138d | Extends far | acc on len 50 (way beyond training) >= 0.90 |

PASS = T138a-d. PASS = recurrence + the substrate's attractor cleanup gives DRIFT-FREE
unbounded composition: a recursive computation, trained only on single steps by a
local rule, generalizes to arbitrary unseen lengths. That is a genuine substrate
mechanism (in-loop attractor error-correction) the static stack lacks, and the honest
core of the project's "compose without bound" goal. NULL would show cleanup is not
enough and bound the reachable length.

## RESULT (2026-05-31): NULL — falsifies my own "drift" diagnosis; the cell can't do XOR at all

| computer | acc len 10..20 | len 50 | bar |
|----------|----------------|--------|-----|
| attractor-recurrent | 0.493 | 0.527 | T138a >=0.95 ✗, T138d >=0.90 ✗ |
| naive (no cleanup) | 0.493 | — | T138b <0.65 ✓ |
| gap | 0.000 | | T138c >=0.30 ✗ |

T138a ✗, T138b ✓, T138c ✗, T138d ✗ → **NULL**, and it FALSIFIES the BET-137 "drift"
hypothesis: per-step attractor cleanup changed NOTHING (0.493 either way). If drift
were the cause, snapping the state to a clean code each step would have fixed it.

Correct diagnosis (honest, my earlier guess was wrong): the recurrent cell is LINEAR,
and parity/XOR is the canonical NON-linearly-separable function (Minsky–Papert 1969).
The four transitions ([E0;B0]→E0, [E1;B1]→E0, [E0;B1]→E1, [E1;B0]→E1) are XOR — a
LINEAR map cannot fit them, so the cell is wrong even one step from a clean state, and
no amount of cleanup or iteration helps. The missing ingredient is NONLINEARITY in the
transition — which the substrate supplies (tanh / random nonlinear features). -> BET-139:
a nonlinear (random-feature) recurrent cell + in-loop cleanup. This also retro-explains
BET-136: modular-successor IS linearly representable (a permutation/rotation), so the
linear cell worked there; parity is not, so it failed here.
