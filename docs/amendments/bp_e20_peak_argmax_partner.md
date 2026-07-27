# BP-E20 — Peak-during-window argmax-R partner (bridged L)

**PRE-REGISTERED 2026-07-20 before data (night scheduler)**  
**Depends on:** E19 NULL (end-state argmax)  
**Not** E19 bar retune — new metric: track **peak** charge per R atom during prop, then argmax on peaks.

---

## Hypothesis

Same train as E19 (multi-trial PRIM5 pairs). Bridged-L probe. During T_prop, maintain running peak `k_charge` per R L4. Decode partner as freq of R atom with highest **peak** charge. Accuracy ≥ **0.80**. Rewire control ≤ **0.55**. Bridged L present ≥ **0.90**.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Peak-argmax partner acc | ≥ **0.80** |
| B2 | Rewire control acc | ≤ **0.55** |
| B3 | ≥1 bridged L | ≥ **0.90** |

Seeds `{621, 631}`, trials 12; same train as E19. Budget 120s / hard 240s.

## Prediction
🔮 **PASS** — diagnosis shows partner R peak 60 vs other 0 on fire ticks.

## RESULT
**PASS** (2026-07-20 night scheduler). B1=**1.000**, B2_rewire=**0.542** (≤0.55), B3=**1.000**.

### Calibration
🔮 predicted PASS — **HIT**. Peak-during-window argmax recovers exclusive partner; rewire control near chance (marginal 0.542, still under bar).

### Scope
Content-addressable partner via **bridged L + peak charge routing** works under multi-trial PRIM5 train. End-state readouts (E18/E19) fail under membrane decay; peak readouts (E14/E20) work. Engineered graph, not free learning.
