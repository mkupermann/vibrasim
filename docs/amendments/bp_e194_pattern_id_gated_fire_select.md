# BP-E194 — Pattern-id gated fire-select (G12 eligibility gate)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 fire-select without pattern_id; G12 firing_eligibility_gate never used in BP runners  
**Discipline:** multi-assoc pair-link train; tag c0/c1 atoms with pattern_id 1/2; probe with `firing_eligibility_gate` + `active_pattern_id` — new multi-trial selective readout primitive class

## Hypothesis
Train c0 (L-lo↔R-hi) and c1 (L-hi↔R-lo) pair-link multislot.  
Tag: L-lo & R-hi → pattern_id=1; L-hi & R-lo → pattern_id=2.  
Gate ON.  

1. active_pattern_id=1; fire L-lo → R-hi select ≥0.80  
2. active_pattern_id=2; fire L-hi → R-lo select ≥0.80  
3. active_pattern_id=1; fire L-hi → R-lo select **fails** ≥0.70 (wrong pattern blocked)  

## Bars
B1 pid1 correct ≥0.80 · B2 pid2 correct ≥0.80 · B3 wrong-pattern fail ≥0.70  

Seeds {5361,5371} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if pattern_id tags stick and gate blocks cross-pattern fire. NULL if ILW atoms untagged or gate ineffective.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. G12 firing_eligibility_gate + pattern_id tags enable correct-arm fire-select and block wrong-pattern L-fire from selecting partner. New multi-trial selective readout class beyond pure freq-matched fire (E171).
