# BP-E166 — Multislot ON multi-assoc residual capacity (c0+c1 both on R)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E157 multislot K=3 capacity; E158/E159 multislot ON reconfig fails; E162–E163 residual  
**Discipline:** sequential c0 then c1 dual train under multislot ON; score **presence** of both R bands after L-only (no baked map)

## Hypothesis
`ilw_multislot_enabled=True`.  
c0: L=500, R=5000 · c1: L=5000, R=500.  
N_train=12 each dual; then L-only at F_LO; idle.  

1. Treatment: R has ≥1 high-freq structure (f≥F_MID) ≥0.80  
2. Treatment: R has ≥1 low-freq structure (f<F_MID) ≥0.80  
3. Control c0-only: R high present AND R low **absent** ≥0.80  

Tests multi-association residual capacity (both partners co-present) vs single-assoc control.

## Bars
B1 treat R high ≥0.80 · B2 treat R low ≥0.80 · B3 ctrl high-only ≥0.80  

Seeds {4441,4451} trials 8. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS if multislot retains both R bands after sequential train (E157 class). NULL if last-write erases first under residual scoring.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Multislot ON retains both R high and R low bands after c0→c1 sequential train + L-only; c0-only control has high without low. Multi-assoc residual capacity closed under multislot.
