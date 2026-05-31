# BET-140 — Capstone: substrate-native unbounded recursive composition

Pre-registered: 2026-05-31 (BEFORE the run). BET-139 showed nonlinearity is the right
axis but per-step error compounds. Make the per-step transition near-exact: fit Wout
by ridge least-squares over the random nonlinear features (= the online RLS solution
the substrate reaches locally), so the in-loop attractor cleanup always corrects each
step. Then per-step ~exact and parity should hold for ANY length.

Cell: next_state = cleanup( Wout @ tanh(R[state;bit]) ), Wout = ridge LSQ on the 4 XOR
transitions, R = substrate random features, cleanup to {E0,E1}. Train = 4 single steps
only. Test lengths 10..20, 50, 100.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T140a | Robust length-gen | acc on len 10..20 >= 0.98 |
| T140b | Far extrapolation | acc on len 50 >= 0.95 |
| T140c | Very far | acc on len 100 >= 0.90 |
| T140d | Nonlinearity needed | linear-feature control on len 10..20 < 0.70 |

PASS = T140a-d. PASS = the assembled substrate-native cell — nonlinear random features
(tanh) for representability + ridge/RLS local readout for a sharp per-step margin +
attractor cleanup for drift-free state — computes a recursive function and generalizes
to arbitrary unseen lengths, trained only on single steps, no BPTT, no transformer.
This is the honest capstone of the dynamics line: unbounded recursive composition from
the substrate's own pieces. (Provenance: an RNN/reservoir cell computing parity is
textbook; the result is the clean substrate-native assembly + local-only training.)

## RESULT (2026-05-31): PASS — unbounded recursive composition, all bars

| length | nonlinear cell | linear control |
|--------|----------------|----------------|
| 10–20 | **1.000** | 0.513 |
| 50 | **1.000** | — |
| 100 | **1.000** | — |

T140a–d ✓ → **PASS**. The assembled substrate-native cell computes parity perfectly at
lengths 10–20, 50, and 100 — trained ONLY on the 4 single-step XOR transitions, local
ridge/RLS fit, no BPTT, no transformer; the linear control is at chance (0.513).

This is the honest capstone of the dynamics line (BET-136→140), and it names exactly
what each piece contributes, derived through the NULLs:
- **recurrence/iteration** (BET-136) → algorithmic composition that static maps can't;
- **nonlinear features** (BET-139) → representability of non-separable steps (XOR;
  the linear cell of BET-137/138 provably can't — Minsky–Papert);
- **sharp per-step readout** (ridge/RLS, BET-140) → kills the error-compounding that
  capped BET-139 at 0.70;
- **attractor cleanup in the loop** → snaps the state to a clean code each step, so it
  stays exact for unbounded length.

Together = drift-free UNBOUNDED recursive composition from the substrate's own pieces.
Provenance is textbook (an RNN/reservoir cell + cleanup computing parity); the value is
the clean substrate-native assembly, the local-only single-step training, and the
honestly-mapped role of each component. No new mathematics claimed.
