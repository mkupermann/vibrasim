# Cascade reverse fire-select curriculum — CLOSED PASS (E214–E218)

**Date:** 2026-07-26  
**Depends on:** E186 cascade forward; reverse pair-link native E203–E204  
**Pattern:** `docs/patterns/pattern_id_gated_fire_select.md`

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E214 | PASS | Dual cascade reverse R→L multi-hop both paths |
| E215 | PASS | Cascade reverse under G12 gate + wrong-pattern block |
| E216 | PASS | Multi-trial switch 1→2→1 reverse cascade under G12 |
| E217 | PASS | Soft mid-kill M0 silences reverse p0; p1 survives |
| E218 | PASS | Long-idle T=400 durable reverse cascade |
| E219 | PASS | Soft mid-kill then retrain-restore reverse p0 |
| E220 | PASS | Hard mid-kill M0 silences reverse p0; p1 survives |
| E221 | PASS | Hard mid-kill then retrain-restore reverse p0 |

## Doctrine

1. Multi-hop reverse is pair-link + charge prop native (same as single-hop reverse).
2. G12 gate applies to cascade reverse firing.
3. Soft mid-hop kill is path-selective on reverse too.
4. Durability matches forward cascade long-idle class.
5. Soft mid-kill is retrainable (E219).

## Do not farm

Re-running E214–E219 bars without a new cascade reverse scientific question.
