# BP-E40 — NOT gate via zero-latch emitter

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM11 primitive (exists); PRIM11-D0 XOR NULL (complex topology)  
**Discipline:** **not** XOR re-farm — isolated **NOT**: path on unless inhibitor fires

## Hypothesis
Path L–M–R (replace OFF). Inhibitor node I tagged `k_zero_latch_emitter=1`, `fire_zero_latch_radius` covers R.
Measure **end** R latch after T_prop:

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Fire L only: end R ≥1.0 | ≥0.90 |
| B2 | Fire L + I: end R ≤0.25 | ≥0.90 |
| B3 | Fire I only: end R ≤0.25 | ≥0.90 |

Seeds {1251,1261} trials 10.

## Prediction
🔮 PASS lean: simpler than XOR; L path uncontested unless I fires after/with L.

## RESULT
**NULL** (2026-07-20). B1=**1.0**, B2=**0.0**, B3=**1.0**.  
L alone ON; I alone OFF; concurrent L+I fails to hold R off (path re-latches after clear).
