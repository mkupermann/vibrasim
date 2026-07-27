# BP-E190 — Triple-hop content cascade fire-select (L→M→A→R dual path)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E186 two-hop cascade PASS  
**Discipline:** four-node cascade per path with content freqs; fire L selects R; dual spatial paths

## Hypothesis
Path0 y=15: L0–M0–A0–R0 freqs 300→800→2000→6000.  
Path1 y=35: L1–M1–A1–R1 freqs 6000→2500→900→350.  
Pair-link train all hops multi-trial.  

1. Fire L0 → R0 select (R0≥1, R0>R1) ≥0.80  
2. Fire L1 → R1 select ≥0.80  
3. Both ≥0.70  

## Bars
B1 path0 ≥0.80 · B2 path1 ≥0.80 · B3 both ≥0.70  

Seeds {5121,5131} trials 8. Budget ~24 min, hard cap 48 min.

## Prediction
🔮 LEAN PASS if two-hop doctrine scales to three hops. NULL if extra hop attenuates latch below bar.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Triple-hop L→M→A→R content cascade fire-select scales from two-hop (E186); dual paths both select.
