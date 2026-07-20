# BP-C8 — Sequential free dual-band talent (time multiplex)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C CLOSED PARTIAL simultaneous dual inject; C5–C7 free paths  
**Discipline:** **new mechanism** = sequential half-box free inject (L then R), not simultaneous dual inject / attractors / sideband cull

---

## Hypothesis

**H-C8.** With midplane ON:

1. **Sequential:** inject L-low free vibs, evolve T_half; then inject R-high free vibs, evolve T_half → `md_L < md_R` on L4 in ≥ **0.90** of trials.  
2. **Simultaneous control:** both halves injected at t=0, evolve T_full=2×T_half → rate ≤ **0.80**.  
3. Sequential both sides populated ≥ **0.80**.  
4. Sequential mean χ ≤ **0.15**.

If PASS: temporal separation unlocks free specialisation simultaneous free cannot.  
If NULL: free dual-band ceiling independent of timing.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Sequential md_L<md_R | ≥0.90 |
| B2 | Simultaneous md_L<md_R | ≤0.80 |
| B3 | Sequential pop | ≥0.80 |
| B4 | Sequential χ | ≤0.15 |

Seeds {931,941,951} trials 3; T_half=500 (T_full=1000). Smoke 1×1 T_half=150.

## Prediction
🔮 LEAN NULL: simultaneous already ~0.67–0.78; sequential may not jump to 0.90.

## RESULT
**NULL** (2026-07-20). B1_seq=**0.778**, B2_sim=**0.889**, B3=1.0, B4_χ=0.  
Sequential does **not** beat 0.90; simultaneous often *stronger*. Time-multiplex free inject is not a free-talent unlock.
