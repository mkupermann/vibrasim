# BET-120 — Higher-Order (History-Dependent) Transitions

Pre-registered: 2026-05-31. The wall (BET-114-119) is that PAIRWISE transitions
(next from current only) cannot disambiguate a repeated state (HELLO -> HELOL:
L->L vs L->O). Different mechanism class: make the transition depend on a SHORT
HISTORY — predict s_{t+1} from the pair [s_t, s_{t-1}] (order-2). Then "L after E"
and "L after L" have different contexts and predict differently. Non-transformer,
biologically plausible (temporal context / eligibility trace).

## Mechanism
Order-2 transition T2 (N x 2N): learn T2 += lr * outer(s_{t+1}, [s_t ; s_{t-1}]).
Recall: next = sign(T2 @ [s_t ; s_{t-1}]), cleaned up by the attractor W. First
step pads history with a START pattern.

## Bars
| ID | Criterion | Bar |
|----|-----------|-----|
| T120a | Repeated-char text fixed | 'HELLO' is recalled EXACTLY (the order-1 failure case) |
| T120b | Multi-sequence fixed | S=3 length-4 sequences @ N=200, min content overlap >= 0.90 |
| T120c | Scales | S=5 @ N=200, min content overlap >= 0.85 |

PASS => higher-order context BREAKS the sequence wall without a transformer — a
real step toward the context-dependent prediction language needs. NULL => even
order-2 is insufficient (the wall is deeper).

## RESULT (2026-05-31): PARTIAL — order-2 fixes repeats (HELLO->HELLO), multi-seq needs more

HELLO -> HELLO (T120a PASS): order-2 history disambiguates the repeated L (L-after-E
vs L-after-L). But multi-sequence with Hebbian order-2 T2 still fails (S=3 0.43,
S=5 0.48) — Hebbian outer-product interference. T120a ✓, T120b/c ✗.

The fix is in BET-121: replace the Hebbian outer-product with a LEAST-SQUARES
(projection) fit of the order-2 transition operator. That eliminates interference
exactly and FULLY solves both repeats and many overlapping sequences.
