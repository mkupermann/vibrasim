# BET-102 — The Scale Test: Adequate Separation + Integration Time

Pre-registered: 2026-05-31 (BEFORE any run). Directly tests the falsifiable
consolidated claim of BET-099→101: clean long-horizon selective recall fails
because write (emission reaching bridged neighbours) and leak (emission reaching
control) are geometrically inseparable when neighbour-distance ≈ control-distance
and charge decays in ~1 step.

## Hypothesis

If the substrate gives (1) enough spatial room that control-distance ≫
neighbour-distance AND (2) a long enough charge-integration window that SLOW
emission can still write to near neighbours, then local emission separates write
from leak and the selective persistent memory passes. If it still fails, the
limit is deeper than scale.

## Regime (coherent, pre-committed)

- **Bigger box: 50³** (was 30³). Stim/control at 0.25/0.75 → x=12.5 / 37.5,
  periodic separation 25 (≫ r_2=10). Neighbours stay within r_2≈10; control is
  25 away.
- **Longer integration: tau_membrane = 2.0 s** (4 steps, was 0.5). Charge
  persists long enough that slow emission can accumulate at a neighbour and
  co-fire.
- **Moderate local emission: emit_speed = 6.0** (3 units/step). Reaches a ≤10-unit
  neighbour within the 4-step window; the 25-unit control needs ~8 steps →
  vibration consumed/charge decayed before it can latch control.
- More vibrations to fill the bigger box: n_initial 1800, soft_cap 2000,
  n_vibrations_max 8192. Persistence (fusion_bond_block=3), anchoring,
  correlation plasticity, neuron_dynamics all as BET-099. n_emit=8.

## Acceptance bars (locked pre-run — BET-100/101 metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| T102a | Selective firing (gate) | stim firings >= 3× control during STIM |
| T102b | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| T102c | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| T102d | Negative control FAILS | uniform arm: fraction of those POST checkpoints selective < 0.25 |

PASS = T102a–c hold AND T102d. PASS → scale/geometry WAS the limit; the
correlation-memory mechanism is sound given adequate separation + integration.
NULL → the limit is deeper than scale; record as the programme's end-state.

This is the LAST regime experiment of the memory programme either way — PASS
confirms the mechanism, NULL confirms the deeper limit; no further tuning.

## RESULT

_(to be filled after the run — PASS / FAIL / NULL with evidence)_
