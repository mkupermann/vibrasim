# BP-E11 — Dual exclusive pairs co-resident (dictionary)

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** PRIM4 multislot, E8/E9 bridges

## Hypothesis
Write pair class 0 then class 1 (E5 exclusive rows) with multislot ON, valence=4, r_2=45. After idle, **both** exclusive pairs appear as cross-bridge endpoint nearest-matches in ≥ **0.80** of trials. Legacy multislot OFF: both-pairs rate ≤ **0.25** (overwrite).

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Multislot: both class 0 and 1 present via bridge endpoints | ≥ **0.80** |
| B2 | Legacy: both present | ≤ **0.25** |
| B3 | Multislot: ≥1 cross bridge | ≥ **0.90** |

Seeds {421, 431}, trials 10; N_write=12/pair; T_idle=300.

## Prediction
🔮 LEAN PASS if multislot seeds 2 atoms/side and form_bridges links matching pairs; miss if bridges only link nearest cross pair once or mix endpoints.

## RESULT
**PASS** (2026-07-20 night). B1=1.0 B2=0.0 B3=1.0. Two exclusive pairs co-resident with multislot.
