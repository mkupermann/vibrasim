# BP-E176 — Selective c0-arm bridge kill (L-lo/R-hi only); c1 fire-select survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E173/E174 full R kill silences all select; E171/E172 both arms  
**Discipline:** hard-kill emitters only on **c0 band** nodes (L near 500 and R high); not full PORT_R kill

## Hypothesis
Train c0+c1 pair-link.  
1. Pre: fire L-lo selects R-hi ≥0.90  
2. After c0-band hard kill: fire L-lo select **fails** ≥0.70  
3. After c0-band hard kill: fire L-hi still selects R-lo ≥0.80  

Tests association-specific bridge disruption (not whole-port wipe).

## Bars
B1 pre L-lo select ≥0.90 · B2 post L-lo fail ≥0.70 · B3 post L-hi select ≥0.80  

Seeds {4661,4671} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if bridges are slot/band-local. NULL if kill on R-hi also severs c1 paths or L-lo kill not enough.

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=1.0 B3=0.0. C0-band hard kill silences L-lo select but **also** destroys L-hi select. Association-specific arm kill not achieved under this emitter targeting (bridge graph not fully arm-segregated for kill).
