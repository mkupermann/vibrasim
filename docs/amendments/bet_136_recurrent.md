# BET-136 — Recurrent dynamics break the modular wall that static composition cannot

Pre-registered: 2026-05-31 (BEFORE the run). Same modular task as BET-133/135 (target
(a+b) mod V, V=12), same held-out bigram split. Two computers on the SAME held-out
pairs:

- **static** (the established stack): one-shot additive map of code(a),code(b) ->
  result (BET-135 form). Expected ~0 (it provably cannot).
- **recurrent** (the substrate as a dynamical computer): learn ONE update operator U
  by a LOCAL one-step delta rule on single successor transitions E[k] -> E[k+1 mod V]
  (no backprop-through-time, no transformer). At test, start from E[a] and APPLY U
  exactly b times (the dynamics run b steps); cleanup the final state -> predicted
  index. The same U serves every (a,b), so iteration composes systematically.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T136a | Recurrence generalizes | recurrent held-out acc (novel pairs) >= 0.85 |
| T136b | Static still fails | static one-shot held-out acc < 0.30 |
| T136c | Clear gap | T136a - T136b >= 0.50 |
| T136d | Operator learned locally, not memorized | U trained ONLY on single-step successors; held-out PAIRS never used in training |

PASS = T136a-d. PASS = the substrate's recurrent dynamics, with a purely local
one-step learning rule, systematically compute an algorithmic function on unseen
inputs that its own static composition stack cannot (0.000) — the first capability in
this project that comes from the substrate's DYNAMICS, not from a borrowed static
method. Honest scope: the model class (iterated operator / FSM) is known; the result
is the substrate-specific demonstration and the local-only training. NULL would show
even recurrence+local-rule doesn't close it.

## RESULT (2026-05-31): PASS — recurrence breaks the wall static composition cannot

| computer | held-out acc (novel pairs) | bar |
|----------|----------------------------|-----|
| **recurrent** (iterated successor, local rule) | **1.000** | T136a >=0.85 ✓ |
| static (one-shot additive) | 0.000 | T136b <0.30 ✓ |
| gap | 1.000 | T136c >=0.50 ✓ |
| U trained on single successors only | yes | T136d ✓ |

T136a–d ✓ → **PASS**. On the SAME held-out bigrams, static composition = 0.000 and
recurrent dynamics = 1.000. The operator U was trained ONLY on single-step successors
(E[k]→E[k+1 mod V]) by a local one-step delta rule — no backprop-through-time, no
transformer, and the held-out PAIRS were never used to fit U. Iterating U exactly b
times from E[a] computes (a+b) mod V for every unseen pair, because the same learned
step composes through time.

**What it means (honest).** The decisive variable for algorithmic generalization is
the COMPUTATIONAL MODE — temporal iteration vs static one-shot map — not the
representation or the readout. This is the first capability in the project that comes
from the substrate's DYNAMICS rather than a borrowed static method. **Honest scope /
provenance:** the model class is a finite-state machine / recurrent computer, and
local recurrent learning has precedents (e-prop, equilibrium prop, RTRL). This is NOT
new mathematics; it is a clean substrate-specific demonstration that recurrence +
local learning solves what the static stack provably cannot, plus a strategic
redirection: language composition should be RECURRENT/temporal, not a static readout.
