# PRIM7 — Midplane spectral filter (free-vib band gate)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C6–C7 attractor class CLOSED; free dual inject ceiling  
**Discipline:** new primitive default OFF — not C5/C6/C7 bar retune

## Primitive
`midplane_sideband_cull_enabled: bool = False`  
`midplane_gate_f_mid: float = 1581.14`  

After midplane wall each tick: **kill** free vibs with wrong-side band:
- left (x < mid) and freq ≥ gate → absorb  
- right (x ≥ mid) and freq < gate → absorb  

Engineered spectral purification of each half (honest §4.8). Default OFF.

## PRIM7-D0 bars (free dual inject + midplane)
| ID | Criterion | thr |
|----|-----------|-----|
| G1 | Cull ON: md_L<md_R rate | ≥ **0.90** |
| G2 | Cull OFF: md_L<md_R rate | ≤ **0.80** |
| G3 | Cull ON: both sides pop | ≥ **0.80** |
| G4 | Cull ON mean χ | ≤ **0.15** |

Seeds {841,851,861} trials 3; T=1000. Smoke 1×1 T=250.

## Prediction
🔮 LEAN PASS: purifying free field should push decade separation over 0.90; off stays C5-like ~0.67.

## RESULT
**NULL** (2026-07-20). G1_cull_on=**0.667**, G2_off=**0.778**, G3=1.0, G4_χ=0.  
Cull **hurts** free specialisation vs wall-only. Spectral purification of free field does not unlock 0.90 talent.
