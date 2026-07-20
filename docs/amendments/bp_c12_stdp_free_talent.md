# BP-C12 — Free dual talent with STDP (new mechanism)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C1–C11 closed dual-inject / BTSP classes  
**Discipline:** not band retune — **stdp_enabled** on free dual inject (new Hebbian class)

## Hypothesis
Dual regional free inject (C1b density: N=400/side, r_2=28, midplane wall).  
**Treatment:** `stdp_enabled=True`, `neuron_dynamics_enabled=True`.  
**Control:** same, `stdp_enabled=False`, neuron dynamics ON.

STDP co-firing should tighten within-region decade structure past the 0.78 ceiling.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | STDP ON: mean_decade_L < mean_decade_R ∧ both n≥1 | ≥0.90 |
| B2 | STDP OFF control same measure | ≤0.80 |
| B3 | STDP ON both regions populated | ≥0.80 |
| B4 | STDP ON − control success | ≥0.15 |

Seeds {1831,1841,1851} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN NULL (same firing scarcity that nullified BTSP C11). Maps STDP free class.

## RESULT
**NULL** (2026-07-20). B1=0.778 B2=0.889 B3=1.0 B4=−0.11.  
STDP free dual does not beat control; control slightly higher. STDP class closed for free dual talent unlock.
