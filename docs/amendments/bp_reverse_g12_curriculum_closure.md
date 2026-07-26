# Reverse fire-select under G12 — CLOSED PASS (E205–E208)

**Date:** 2026-07-26  
**Depends on:** E171 forward fire-select; E203–E204 reverse native (pair-link, not G6/G13)  
**Pattern:** `docs/patterns/pattern_id_gated_fire_select.md`

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E203 | NULL | Reverse works; G13 bidir not load-bearing |
| E204 | NULL | Reverse works G6 OFF; pair-link + charge prop native |
| E205 | PASS | Reverse under G12 gate (correct + wrong-pattern block) |
| E206 | PASS | Reverse multi-trial switch 1→2→1 |
| E207 | PASS | Train-time tags suffice (no post-hoc) |
| E208 | PASS | Long-idle T=400 durable |

## Doctrine

1. Reverse R→L fire-select is pair-link + bridge_charge_prop native (not G6/G13).
2. G12 gate applies symmetrically to reverse firing (R-side tags).
3. Multi-trial switch, train-time tags, and long-idle match forward path durability.

## Do not farm

Re-running E205–E208 bars without a new reverse question (e.g. reverse soft-kill arm surgery).

## Open

- Reverse soft-kill / split-port reverse surgery
- Pattern_id + free dual hybrid
