# BP-E19 — Bridged-L probe + argmax-R charge partner (no external table)

**PRE-REGISTERED 2026-07-20 before data (night scheduler)**  
**Depends on:** E18 NULL (charge-weighted continuous readout failed)  
**Discipline:** **not** E18 bar retune — new probe set (bridged L only) + new decode (argmax R charge, not charge-weighted mean freq)

---

## Hypothesis

**H-E19.** After multi-trial PRIM5 dual pair_write of classes {0,1}:

1. Sample an L atom that is an endpoint of ≥1 **cross-mid bridge**.  
2. Force-fire only that atom; after T_prop, take the **R-side L4 with maximum k_charge**.  
3. Its frequency is closer to the true partner of the L atom’s frequency than to the other R band ≥ **0.80** of trials.  
4. Control: rewire cross-bridge R endpoints randomly → same decoder accuracy ≤ **0.55**.  
5. ≥1 bridged L exists after train in ≥ **0.90** trials.

Scoring may use the hidden map; the **decoder loop** only uses graph + charge (no centroid table lookup).

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Bridged-L argmax-R partner acc | ≥ **0.80** |
| B2 | Rewired control acc | ≤ **0.55** |
| B3 | Fraction trials with ≥1 bridged L | ≥ **0.90** |

## Protocol
Seeds `{601, 611}`, trials 12; T_train=6 × N_write=10; multislot+pair_link; valence=0; T_prop=50.  
Budget est 120s / hard 240s.

## Prediction
🔮 **PASS** lean: E16 showed exclusive links route charge; E18 failed by sampling unbridged L and/or weighted mean. Bridged+argmax should recover partner.  
Most-likely miss: rewire control still high if charge never flows (both arms fail differently).

## NOT claimed
Free talent; unsupervised discovery of map without any scoring map; generative partner (E12).

## RESULT
**NULL** (2026-07-20 night scheduler). B1=**0.000**, B2=**0.000**, B3=**1.000**.

### Calibration
🔮 PASS lean — **MISS**. Bridged L exist; exclusive prop does raise partner R charge on fire ticks (diag: R@7000 hits 60), but **end-of-window** argmax sees decayed charge 0 (same membrane pattern as E13). No bar retune.

### Next
E20: **peak-during-window** argmax R freq (transient), not end-state.
