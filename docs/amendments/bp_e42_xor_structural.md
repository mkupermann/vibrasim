# BP-E42 — XOR from OR + structural kill (PRIM9+12)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9 AND PASS; PRIM12 structural NOT PASS; latch-clear XOR CLOSED

## Hypothesis
- OR: L1–Mor–R, L2–Mor–R  
- AND: L1,L2 → Mand (coincidence); Mand is kill-bridge emitter covering Mor/R  

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Fire L1 only: end R ≥1.0 | ≥0.85 |
| B2 | Fire L2 only: end R ≥1.0 | ≥0.85 |
| B3 | Fire both: after dual phase, n_bridges dropped vs train **and** fire L1 again end R ≤0.25 | ≥0.85 |

Seeds {1311,1321} trials 10.

## Prediction
🔮 PASS lean: single L lights R; both triggers Mand cut, subsequent L silent.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0.  
XOR: single L lights R; both L → Mand cuts bridges → subsequent L silent.
