# BET-128 — Code normalization removes the high-D overfit collapse

Pre-registered: 2026-05-31 (BEFORE the run). Fresh from BET-127's NULL: analog code
norm grows as |code|^2 ∝ D, so with fixed ridge λ the online readout is
under-regularized at high D and overfits the 54 training pairs (accuracy peaked at
D=1024=0.889 then fell). Fix: L2-normalize each code to unit norm before the
readout, making feature scale D-independent.

Same comparison task, systematic held-out split, analog bundle, online linear RLS,
3 seeds/D, sweep D in {256,512,1024,2048,4096,8192}.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T128a | Collapse gone | normalized largest-D acc >= 0.85 (vs unnormalized 0.787) |
| T128b | Stable scaling | normalized acc non-decreasing across D (allow one <=0.03 dip) |
| T128c | High ceiling | best-D normalized acc >= 0.88 |
| T128d | Still compositional | no-binding normalized control at largest D < 0.65 |

PASS = T128a-d. PASS = the high-D decline was a normalization artifact and
SYSTEMATIC generalization is robust and high across scale — systematic
symbolic-combination generalization SOLVED on the substrate (analog VSA + online
normalized linear readout, no transformer). NULL = overfit is not the cause and a
deeper limit remains.

## RESULT (2026-05-31): NULL — normalization changes nothing; the bottleneck is #training compositions

| D | normalized held-out acc |
|---|-------------------------|
| 256 | 0.824 |
| 512 | 0.861 |
| **1024** | **0.898** |
| 2048 | 0.815 |
| 4096 | 0.769 |
| 8192 | 0.787 |
| no-binding control (D=8192) | 0.343 |

T128a ✗ (0.787), T128b ✗ (2 dips), T128c ✓ (0.898), T128d ✓ → **NULL**.

The curve is essentially IDENTICAL to unnormalized BET-127 (peak 0.898 at D=1024,
same high-D decline). So feature-norm/overfit was NOT the cause — REFUTED. With the
training set fixed at 54 pairs, raising D adds parameters without adding evidence;
the readout cannot pin down the structured weight W=w_l⊙role_l−w_r⊙role_r from too
few compositions, so high-D generalization erodes. The governing resource is the
NUMBER OF TRAINING COMPOSITIONS seen, not dimension and not normalization.

Best systematic held-out accuracy across BET-126/127/128 is ~0.90 at D≈1024 — the
substrate DOES generalize a relation to novel symbol combinations (controls always
collapse), online, no transformer. -> BET-129 tests the real lever directly: hold
D=1024, sweep the number of training compositions; predict held-out accuracy climbs
toward ~1.0 as more compositions are seen (a curriculum / sample-complexity law).
