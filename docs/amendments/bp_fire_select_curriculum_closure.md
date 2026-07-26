# Fire-select residual curriculum — CLOSED (E171–E176)

**Date:** 2026-07-26  
**Scope:** Map-free multi-assoc **selective** residual under fire/bridge readout (not residual means).

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E169 | NULL | L-only rewrite means do not select partner |
| E170 | NULL | Pair-link + L-only means still fail select |
| E171 | PASS | Freq-matched L fire → R partner latch (pair-link ON) |
| E172 | PASS | Multi-trial A→B→A fire select same world |
| E173 | PASS | Hard R bridge kill silences; restore returns |
| E174 | PASS | Soft R weaken silences; restore returns |
| E175 | NULL | No pair-link → no fire-select (B1=B2=B3=0) |
| E176 | NULL | C0-band kill silences L-lo but also L-hi (no arm-selective kill) |
| E177 | PASS | Split-port arm-selective hard kill (c0 off, c1 on) |
| E178 | PASS | Multi-trial split-port arm switch kill/restore |
| E179 | NULL | Pair-replace not exclusive for prior-arm fire-select |

## Doctrine
1. **Capacity residual ≠ selective residual** (E162–E168 vs E169/E170).
2. **Fire + pair-link bridges + latch** enable selective residual (E171).
3. Multi-trial fire select durable without retrain (E172).
4. Select is **bridge-dependent**: soft/hard R disruption silence prop; restore returns (E173/E174).
5. Pair-link is **necessary** (E175).
6. Association-specific kill on **shared** ports fails (E176 NULL).
7. **Spatial split ports** enable arm-selective kill (E177) and multi-trial switch (E178).
8. PRIM8 replace alone ≠ exclusive last-arm fire-select (E179 NULL).

See also `bp_split_port_arm_curriculum_closure.md`.

## Patterns
`docs/patterns/port_multi_trial_association_residual.md`

## Do not farm
Re-running E171–E178 bars; residual means; full-port kill variants without new question.

## Open / next hard
- Soft-kill split-port arm selectivity (optional parity)
- Free talent still CLOSED PARTIAL (C16); free dual still blocked
- Brain R9 still blocked until free talent or deeper honest curriculum
