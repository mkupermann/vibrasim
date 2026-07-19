# BP-E18 — Multi-trial map without external pair table at readout

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Hard learning-shaped claim** — not storage farm

## Hypothesis

**Train** (one persistent world): for T_train episodes, sample class c∈{0,1}, dual pair_write that class (PRIM5).  
**Test readout without pair table:** force-fire a random L atom; predict R partner **freq** as the mean freq of R atoms that receive peak charge (graph routing only). Score correct if predicted R band matches the **true partner of that L atom's band** using the *hidden* map (scoring only; decoder does not look up table — it only uses charge-weighted R freqs).  

Bars:
1. Treatment accuracy ≥ **0.80**  
2. Control: shuffle bridges (rewire random L–R) before test → acc ≤ **0.55**  
3. Both L bands and both R bands present after train ≥ **0.90**

If PASS: exclusive graph + charge implements content-addressable partner without feeding table into decoder loop.  
If NULL: still need external centroids or training insufficient.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Graph charge partner acc | ≥ **0.80** |
| B2 | Rewired control acc | ≤ **0.55** |
| B3 | All four bands present | ≥ **0.90** |

Protocol: seeds {581,591}, trials 10; T_train=8 episodes × N_write=8; multislot+pair_link; valence=0. Budget 200s / hard 400s.

## Prediction
🔮 PASS lean: E16 already shows L0→R0 selectivity; this is the same without naming classes in decoder — only argmax charge on R.

## RESULT
*(after)*
