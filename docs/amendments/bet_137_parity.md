# BET-137 — Length generalization: recursive parity the static stack cannot do

Pre-registered: 2026-05-31 (BEFORE the run). Addresses the honest critique of BET-136
(the ring/iteration structure was hand-fit to modular addition). Parity (XOR of an
entire bit sequence) is the canonical function that REQUIRES recurrent memory and
that any bounded-context model fails for long inputs. The real test of systematic
recursion: train the recurrent cell on SHORT exposure, test on LONGER sequences whose
lengths were NEVER seen.

- **recurrent** (substrate dynamics): a 2-state cell (even/odd), state codes E[0],E[1],
  bit codes B[0],B[1]. Learn the transition (state,bit)->next_state implementing XOR
  from the 4 single-step transitions only, by a LOCAL one-step rule (no BPTT, no
  transformer). At test, run the cell over a whole sequence and cleanup the final
  state -> predicted parity.
- **static** (established bounded context): an order-K (K=4) linear readout over the
  last K bits. Provably cannot compute parity of length >> K.

Test set: random bit sequences of lengths 10..20 (NEVER in training, which used only
length<=4 exposure). 200 sequences.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T137a | Recurrence length-generalizes | recurrent acc on len 10..20 >= 0.95 |
| T137b | Static fails to extrapolate | order-K static acc < 0.65 |
| T137c | Clear gap | T137a - T137b >= 0.30 |
| T137d | Trained short, tested long | training exposure length <= 4; test length 10..20 |

PASS = T137a-d. PASS = the substrate's recurrent dynamics, with a purely local rule
and NO length-specific fitting, systematically generalize a recursive computation to
unseen sequence lengths — the unbounded-composition property language needs, that a
bounded-context static stack cannot. Honest scope: parity-by-RNN is textbook; the
contribution is the substrate-native local-only training + the clean static-vs-dynamic
contrast. NULL would bound how far the local-rule recurrence extrapolates.

## RESULT (2026-05-31): NULL — recurrence DRIFTS; it does not length-generalize naively

| computer | acc on len 10..20 | bar |
|----------|-------------------|-----|
| recurrent (naive local-rule cell) | 0.493 | T137a >=0.95 ✗ |
| static (order-4 context) | 0.518 | T137b <0.65 ✓ |
| gap | −0.025 | T137c >=0.30 ✗ |

T137a ✗, T137b ✓, T137c ✗ → **NULL**. The recurrent cell learns the 4-state XOR
transition perfectly, but iterated over 10–20 steps the state code DRIFTS — each
application of the learned map M injects error, it accumulates, the even/odd
representation degrades, and 2-way cleanup falls to chance (0.493).

**This honestly tempers BET-136.** That success leaned on a clean ring + per-step
renormalization to discrete states; general recurrent computation with a naive
local-rule linear cell does NOT automatically length-generalize — error accumulation
kills it. The fix is substrate-native and pre-registered fresh as BET-138: insert the
substrate's CONTENT-ADDRESSABLE ATTRACTOR (energy cleanup) INSIDE the recurrent loop,
snapping the state back onto a clean code every step, so drift cannot accumulate.
Recurrence + attractor error-correction is the real test of whether the substrate's
dynamics give robust unbounded composition.
