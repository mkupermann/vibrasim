# Pattern-id G12 gated fire-select curriculum — CLOSED PASS (E194–E197)

**Date:** 2026-07-26  
**Depends on:** E171 fire-select (freq-matched, no pattern_id); G10/G12 substrate primitives  
**Pattern:** `docs/patterns/pattern_id_gated_fire_select.md`

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E194 | PASS | Correct-arm select + wrong-arm fail under G12 gate with tagged pids |
| E195 | PASS | Multi-trial switch pid1→pid2→pid1 without retrain |
| E196 | PASS | Train-time `active_pattern_id` tags suffice (no post-hoc tag) |
| E197 | PASS | Tags load-bearing for **wrong-arm block** only; ambient allows positive select |
| E198 | NULL | Soft-kill wrong arm on **shared** PORT_R spills; kills pid1 too |
| E199 | PASS | Soft-kill on **split** R1 silences pid2; pid1 survives (fix E198) |

## Doctrine

1. G12 `firing_eligibility_gate` + non-zero `k_pattern_id` enables **wrong-pattern suppression**.
2. Ambient (pid=0) still fires under gate → **positive fire-select works without tags** (E171 path + ambient).
3. Multi-trial switch of `active_pattern_id` is durable without retrain.
4. Train-time tagging via `active_pattern_id` during ILW works on shared multislot ports.
5. Engineered pattern_id curriculum is required for exclusive arm isolation under the gate.
6. Soft-kill wrong-arm is arm-selective only with **split ports** (E199); shared R soft kill spills (E198).

## Distinct from

- Residual co-presence E162–E168 (no fire/gate)
- Mean selective residual NULL E169–E170
- Split-port spatial surgery E177–E183
- Content cascade E186–E193

## Do not farm

Re-running E194–E197 bars without new pattern_id scientific question (e.g. free dual hybrid, emergent auto-tag).

## Open

- Pattern_id + free dual hybrid
- Emergent auto-tag without engineered `active_pattern_id`
- Free dual still C16 PARTIAL only robust class
