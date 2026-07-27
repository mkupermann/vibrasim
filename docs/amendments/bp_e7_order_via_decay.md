# BP-E7 — Write order via strength decay (new channel)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM3-D0 (must PASS first or E7 records FAIL/blocked)  
**Not** a retune of E3’s 0.85 on equal-mass; **new mechanism** = gap + decay.

---

## Hypothesis

**H-E7.** With midplane+ILW and `ilw_strength_decay_tau=2.0`:

1. Write side A only (N_write), idle **T_gap**, write side B only (N_write), idle T_short.  
2. Strength decode of which side is stronger recovers **B (last)** ≥ **0.85**.  
3. Control **no-decay** (tau=0), same sequence: last-decode accuracy ≤ **0.60** (E3 regime).  
4. Control **equal dual write** with tau=2.0, no gap asymmetry: relative imbalance ≤ **0.25**.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment last-decode acc | ≥ **0.85** |
| B2 | No-decay control last-decode acc | ≤ **0.60** |
| B3 | Equal-write + decay imbalance mean | ≤ **0.25** |

## Protocol
Seeds {321, 331}, trials 10; N_write=15; T_gap=400; T_short=50; mid=40. Budget 90s / hard 180s.

## Prediction
🔮 PASS if PRIM3 works: gap wipes older mass; no-decay control ~0.5; equal ~0.  
Most-likely miss: T_gap too short / tau too long → B1 fails; or no-decay still biased → B2 fails.

## RESULT
**PASS** (2026-07-20). B1_treat=**1.000**, B2_no_decay=**0.450**, B3_eq_imb=**0.000**.

### Calibration
🔮 predicted PASS — **HIT**. Gap+PRIM3 decay recovers last side; no-decay ~chance (E3); equal balanced.

### Scope
Order channel is **engineered strength leak + temporal gap**, not free emergence. E3 boundary stands for tau=0.
