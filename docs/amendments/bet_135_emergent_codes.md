# BET-135 — Do emergent (dynamics-shaped) symbol codes break the modular wall?

Pre-registered: 2026-05-31 (BEFORE the run). The honest novelty test. Every method so
far (VSA, reservoir, RLS — all established) learns only the READOUT over FIXED random
codes, and that provably cannot generalize modular addition (BET-133/134 = 0.000).
The one place the substrate could exceed the textbook stack: let the symbol codes
THEMSELVES emerge from a LOCAL error-correcting rule (no backprop graph, no
transformer), and ask whether that breaks the wall.

Setup: two-word modular task, target index (a+b) mod V, V=12, D=64. Fixed output
codebook O (random). Input codes E[k] are LEARNABLE (start random). Context
c(a,b) = normalize(pos1⊙E[a] + pos2⊙E[b]); pred = W·c; cleanup over O.
LOCAL update (delta / Widrow-Hoff, one linear step — same family as the substrate's
contrastive-Hebbian rule, NOT deep backprop): err = O[(a+b)%V] − pred;
  W   += η · err ⊗ c
  E[a]+= η_e · pos1⊙(Wᵀ err);  E[b]+= η_e · pos2⊙(Wᵀ err)
Trained over repeated online passes; tested on HELD-OUT bigrams (novel pairs).

HONEST framing: the delta rule is itself classical, and structured codes for modular
arithmetic are known (Fourier/HRR, Plate). The genuinely-open question here is purely
empirical and substrate-relevant: can codes EMERGE from a local rule that break a wall
fixed random codes cannot — and does ADDITIVE (bundle) composition even admit a
modular solution, or is the limit the OPERATOR (additive bundle) not the codes?

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T135a | Emergent codes break the wall | learnable-code held-out acc >= 0.85 |
| T135b | Established stack still fails | frozen-random-code (readout-only) held-out < 0.30 |
| T135c | Clear gap | T135a − T135b >= 0.50 |

PASS = T135a-c → emergent representation learning is the substrate's first genuine
edge over the fixed-code textbook stack. NULL (T135a fails) is equally informative: if
even learnable codes can't make ADDITIVE composition do modular arithmetic, the wall
is the OPERATOR — pointing to multiplicative binding (circular convolution) as the
necessary next primitive. Either way the result is honest and sharp.

## RESULT
## RESULT (2026-05-31): NULL — the wall is the OPERATOR, not the representation

| metric | value | bar |
|--------|-------|-----|
| learnable-code held-out acc | 0.000 | T135a >=0.85 ✗ |
| frozen-random (readout only) | 0.000 | T135b <0.30 ✓ |
| gap | 0.000 | T135c >=0.50 ✗ |

T135a ✗, T135b ✓, T135c ✗ → **NULL**, and the pre-registered diagnosis fires exactly.
Learning the codes by a local rule did NOT help — both are 0.000. Reason, provable:
additive (bundle) composition gives pred(a,b) = W·(pos1⊙E[a] + pos2⊙E[b]) =
M1·E[a] + M2·E[b] — additive/SEPARABLE in the two slots. Selecting O[(a+b) mod V]
from g(a)+h(b) under nearest-neighbour is not achievable for arbitrary modular
structure for ANY codes. So representation learning cannot break this wall; the
binding OPERATOR does.

**Honest bearing on the novelty question.** I attempted the one plausibly-novel lever
(emergent, dynamics-shaped codes). It NULLed, and the cause is a KNOWN VSA fact:
binding two fillers multiplicatively needs CIRCULAR CONVOLUTION (Plate's HRR, 1995),
not additive bundling. There is no new mathematics hiding here — the existing
operators already define the boundary. Next (BET-136, explicitly NOT claimed as
novel): switch the two-word binding to circular convolution + Fourier-structured
codes and confirm modular generalization returns — validating the operator diagnosis
with established machinery.
