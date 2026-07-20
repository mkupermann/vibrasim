# BP-E23 — Map without scoring table; rewire kills **discriminability**

**PRE-REGISTERED 2026-07-20 before data (night scheduler)**  
**Depends on:** E22 NULL (self-consistency control vacuous at K=2)  
**Not** E22 B3 retune — **new control metric**: rewire must collapse **modal R gap**, not self-consistency

---

## Hypothesis

Same train/readout as E22 (latch partner routes; median L split; no pair table in score).

1. Treat: self-consistency ≥ **0.80**  
2. Treat: modal R relative gap ≥ **0.25**  
3. **Rewire control:** modal R relative gap ≤ **0.15** (partners randomized → groups no longer map to systematically different R; or collapse)

If both L still hit different R by chance after rewire, gap may remain — expect rewire gap distribution near chance; bar is mean gap ≤0.15.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat self-consistency | ≥ **0.80** |
| B2 | Treat modal R gap | ≥ **0.25** |
| B3 | Rewire modal R gap | ≤ **0.15** |

Seeds `{701, 711}`, trials 12. Same protocol as E22. Budget 180s / hard 360s.

## Prediction
🔮 LEAN NULL on B3: with 2 bridges rewired, two L may still attach to two different R → gap stays large. If so, K=2 exclusive graph cannot support this control either → close no-table map class for K=2.

## RESULT
**NULL** (2026-07-20 night scheduler). B1=**0.958**, B2_gap=**0.616**, B3_rewire_gap=**0.348** (fail ≤0.15).

### Calibration
🔮 lean NULL on B3 — **HIT**. Rewire of 2 exclusive edges often still attaches each L to a **different** R → modal gap stays high. K=2 exclusive graph cannot host a defensible table-free rewire control.

### Class close
**No-hidden-scoring-table map under K=2 PRIM5 exclusive pairs: CLOSED PARTIAL.** Treat routing still PASS under table scoring (E20/E21). Table-free defensible controls fail at this cardinality.
