# BP-E21 — End-state partner via charge latch (PRIM6)

**PRE-REGISTERED 2026-07-20 before data (night scheduler)**  
**Depends on:** PRIM6-D0 (run after / with same commit train)  
**Not** E19 bar retune — readout channel is **`k_latch`**, not end `k_charge`

---

## Hypothesis

Multi-trial PRIM5 train; bridged-L probe; force-fire L with periodic drive during T_prop then **extra idle T_end=40 without re-drive**.  
Decode partner as freq of R atom with max **`k_latch`** (end-state). Accuracy ≥ **0.80**.  
Control: latch OFF → end-state argmax on `k_charge` acc ≤ **0.55** (E19 regime).  
Bridged L present ≥ **0.90**.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Latch ON: end latch-argmax partner acc | ≥ **0.80** |
| B2 | Latch OFF: end charge-argmax acc | ≤ **0.55** |
| B3 | Bridged L present (treat) | ≥ **0.90** |

Seeds `{661, 671}`, trials 12. Budget 150s / hard 300s.

## Prediction
🔮 PASS if PRIM6 holds latch through T_end.

## RESULT
*(after)*
