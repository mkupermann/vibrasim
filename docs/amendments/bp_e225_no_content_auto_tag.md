# BP-E225 — No content auto-tag without active_pattern_id (emergent auto-tag negative)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E196 train-time tag; E197 tags load-bearing; substrate allocate tags via active_pattern_id only  
**Discipline:** dual ILW train with **ambient** active_pattern_id=0 always; no post-hoc tag. Pre-register that tags stay zero and wrong-arm block fails; post-hoc tag restores block.

## Hypothesis
1. After ambient train: fraction L4 with k_pattern_id≠0 ≤0.05  
2. Gate ON active_pattern_id=2; fire L-lo → R-hi still selects (wrong-arm **not** blocked) ≥0.70  
3. Post-hoc both-end tags; active_pattern_id=2; fire L-lo → R-hi select **fails** ≥0.70  

## Bars
B1 tag fraction ≤0.05 · B2 wrong-arm still selects ≥0.70 · B3 post-hoc wrong fail ≥0.70  

Seeds {6641,6651} trials 6. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS. Substrate does not invent pattern_ids from content; tags require active_pattern_id at allocate or post-hoc script.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Ambient train yields no non-zero tags; wrong-arm still selects under gate; post-hoc tags restore wrong-arm block. Emergent content auto-tag absent without active_pattern_id / engineered post-hoc.
