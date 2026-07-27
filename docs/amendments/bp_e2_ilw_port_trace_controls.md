# BP-E2 — ILW port trace with cleaner controls

**PRE-REGISTERED 2026-07-20 before data**  
**Not** a retune of E1’s 0.60 — **new control definitions**.

## Hypothesis
Same treatment as E1 (one-sided ILW → decode side by strength).  
**C_none:** zero ILW events → decode acc ≤ **0.55** (chance).  
**C_eq:** equal N_write on both sides → mean |S_L−S_R|/(S_L+S_R+ε) ≤ **0.25** (symmetric mass, not a decode bar).

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment decode | ≥ 0.90 |
| B2 | C_none decode | ≤ 0.55 |
| B3 | C_eq relative imbalance mean | ≤ 0.25 |
| B4 | Treatment written side has ≥1 L4 | ≥ 0.85 |

Protocol: same as E1 seeds {211,223} trials 12; N_write=25; T_idle=200.

## RESULT
**PASS** (2026-07-20). treat=1.0, none=0.458, eq_imb=0.0, written=1.0.
