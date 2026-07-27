# BP-E13 — Cross-midplane charge via bridge graph

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E8 cross bridges; BET-105 bridge_charge_prop (existing, gated)

## Hypothesis

After dual ILW + cross bridges (`atom_valence=4`, `r_2=45`), with `bridge_charge_prop_rate=2.0` and `neuron_dynamics_enabled`:

1. Force L-side L4 charge above fire threshold; after T ticks, mean R-side L4 charge increase ≥ **1.0** in ≥ **0.85** trials.  
2. Control valence=0 (no bridges): mean R charge increase ≤ **0.25** in ≥ **0.85** trials (use fraction of trials where ΔR ≤ 0.25 ≥ 0.85).  
3. Dual still has ≥1 cross bridge ≥ **0.90** (treatment arm).

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat: fraction trials Δcharge_R ≥ 1.0 | ≥ **0.85** |
| B2 | No-bridge: fraction trials Δcharge_R ≤ 0.25 | ≥ **0.85** |
| B3 | Treat has cross bridge | ≥ **0.90** |

Seeds {461, 471}, trials 10; N_write=12; T_prop=120. Budget 90s / hard 180s.

## Prediction
🔮 LEAN PASS if firing_events + prop along cross bridges work; miss if neurons never fire or prop_min blocks.

## RESULT
**NULL** (2026-07-20 night). B1=**0.000** (end-state ΔR≥1), B2=1.000, B3=1.000.

### Calibration
🔮 lean PASS — **MISS**. Cross bridges form; prop can raise R charge on fire ticks, but `tau_membrane` decays charge so **end-of-window** ΔR fails. No bar retune.

### Next
E14: **peak** cross charge during prop window (transient transfer), not end-state.
