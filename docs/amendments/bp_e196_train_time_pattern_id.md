# BP-E196 — Train-time pattern_id via active_pattern_id (no post-hoc tag)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E194 PASS with post-hoc tag_patterns; G10 allocate_node tags active_pattern_id  
**Discipline:** set `active_pattern_id=1` during c0 dual train, `=2` during c1 train; **no** post-hoc tag_patterns; gate select as E194

## Hypothesis
1. After train-time tagging, active_pattern_id=1 fire L-lo → R-hi ≥0.80  
2. active_pattern_id=2 fire L-hi → R-lo ≥0.80  
3. At least 50% of L-lo atoms have pattern_id=1 after train (tag success) ≥0.80 trials  

## Bars
B1 pid1 select ≥0.80 · B2 pid2 select ≥0.80 · B3 tag rate trials ≥0.80  

Seeds {5421,5431} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN NULL to weak PASS — multislot rewrites may leave mixed pattern_ids on shared ports; post-hoc tag may be load-bearing for E194.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Train-time `active_pattern_id` during c0/c1 dual writes tags L-lo with pid1 sufficiently; G12 gate select works **without** post-hoc tag_patterns.
