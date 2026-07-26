# Split-port arm-selective fire-select curriculum — CLOSED (E177–E179)

**Date:** 2026-07-26  
**Depends on:** Fire-select E171–E176 (`bp_fire_select_curriculum_closure.md`)

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E176 | NULL | Shared-port c0-band kill not arm-selective |
| E177 | PASS | Split ports: hard kill R0 silences c0; c1 survives |
| E178 | PASS | Multi-trial kill/restore arm switch (c0 off → c1 → restore both) |
| E179 | NULL | PRIM8 pair_replace on shared ports does not exclusive-kill prior arm fire-select |

## Doctrine
1. **Spatial segregation** of association endpoints enables arm-selective bridge surgery (E177).
2. Multi-trial restore of killed arm coexists with intact arm (E178).
3. **Replace-mode alone** is insufficient for exclusive last-arm fire-select under multislot shared ports (E179).
4. Prefer split topology over shared-port replace for selective arm control.

## Do not farm
Re-running E177–E178 bars; E179 retune; residual means / E171–E175.

## Open
- Soft-kill split-port arm selectivity (parity with hard E177)
- Free talent still CLOSED PARTIAL
