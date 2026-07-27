# BP-E223 — Pattern-id G12 + free dual hybrid at full C16 budget

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E222 NULL budget-fit; C16 PARTIAL unlock protocol  
**Discipline:** free dual + wall + `ilw_strength_decay_tau=30` at **C16 scale** (N=400 T=1200, 3 seeds × 3 trials). Treat: `firing_eligibility_gate=True` (ambient). Ctrl: gate OFF. Neuron dynamics ON both (required for gate).

## Hypothesis
1. Treat (decay+gate) ordered ≥0.90  
2. Ctrl (decay only) ordered ≥0.90  
3. Treat pop ≥0.80  
4. |treat−ctrl| ≤0.20  

## Bars
B1–B4. Seeds {6551,6561,6571} trials 3. N=400 T=1200. Budget ~40 min, hard cap 80 min.

## Prediction
🔮 LEAN PASS if ambient G12 no-ops and C16-class unlock holds with neuron_dynamics; LEAN NULL if neuron_dynamics or seed shift breaks C16 unlock.

## RESULT
**NULL** (2026-07-26). B1=0.7778 B2=0.7778 B3=1.0 B4=0.0 (n=9).  
Full C16 scale with neuron_dynamics: neither arm reaches 0.90 unlock. Gate ambient is no-op (equal treat/ctrl). Neuron_dynamics may suppress C16-class unlock relative to original C16 (no neuron_dynamics). Hybrid class closed for ambient G12.
