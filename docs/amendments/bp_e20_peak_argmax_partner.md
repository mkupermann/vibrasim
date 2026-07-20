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
*(after)*
