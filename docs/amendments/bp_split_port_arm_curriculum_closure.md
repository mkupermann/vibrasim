# Split-port arm-selective fire-select curriculum — CLOSED (E177–E183)

**Date:** 2026-07-26  
**Depends on:** Fire-select E171–E176 (`bp_fire_select_curriculum_closure.md`)

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E176 | NULL | Shared-port c0-band kill not arm-selective |
| E177 | PASS | Split ports: hard kill R0 silences c0; c1 survives |
| E178 | PASS | Multi-trial kill/restore arm switch (c0 off → c1 → restore both) |
| E179 | NULL | PRIM8 pair_replace on shared ports does not exclusive-kill prior arm fire-select |
| E180 | PASS | Soft weaken R0 silences c0; c1 survives (soft parity) |
| E181 | PASS | Triple-arm (K=3) fire-select capacity |
| E182 | PASS | Middle-arm kill at K=3 (c1 off; c0+c2 survive) |
| E183 | PASS | Middle kill + restore multi-trial at K=3 |

## Doctrine
1. **Spatial segregation** of association endpoints enables arm-selective bridge surgery (E177).
2. Multi-trial restore of killed arm coexists with intact arm (E178 dual; E183 K=3).
3. **Replace-mode alone** is insufficient for exclusive last-arm fire-select under multislot shared ports (E179).
4. Soft and hard arm-local disruption both work under split ports (E177/E180).
5. Dual-arm doctrine **scales to K=3**: capacity (E181), selective middle kill (E182), kill+restore (E183).
6. Prefer split topology over shared-port replace for selective arm control.

## Do not farm
Re-running E177–E183 bars; E179 retune; residual means / E171–E175.

## Open
- Free talent still CLOSED PARTIAL; K>3 optional only with new question
