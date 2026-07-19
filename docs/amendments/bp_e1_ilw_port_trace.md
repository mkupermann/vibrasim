# BP-E1 — ILW port trace (which side was written)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM2-D0, PRIM1-D2, C5 ILW arm  
**Discipline:** engineered ports honest; not free talent re-open

---

## Hypothesis

**H-E1.** With midplane wall + ILW, a world that receives **N_write** ILW events on **one** side only (L or R, random label), then idle *T_idle*, then a **readout** of mean `k_strength` (or total strength) of level≥4 nodes on L vs R, decodes the written side with accuracy ≥ **0.90**. Control: equal ILW on both sides → decode ≤ **0.60**.

This is **port-local structural memory** (trace of write side), not understanding.

---

## Mechanism
- midplane ON, ilw ON  
- Train: with probability 1/2 write only L (seed_freq 500) N_write times; else only R (seed_freq 5000)  
- Idle T_idle ticks (physics only)  
- Read: S_L = sum strength level≥4 with x&lt;mid; S_R similarly; predict L if S_L > S_R else R  
- Control arm: N_write/2 events each side  

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment decode acc | ≥ 0.90 |
| B2 | Control decode acc | ≤ 0.60 |
| B3 | Treatment both sides have ≥0 nodes allowed; at least written side has ≥1 level≥4 | ≥ 0.85 of trials |

## Protocol
N_write=25, T_idle=200, seeds {211,223}, trials/seed=12, box 80×50×50

## RESULT
**NULL** (2026-07-20). B1=1.000, B2 control=**0.625** (>0.60), B3=1.000.  
Treatment works; equal-write control slightly biased (not chance). No bar retune → E2 with cleaner controls.
