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

## Doctrine
1. **Capacity residual ≠ selective residual** (E162–E168 vs E169/E170).
2. **Fire + pair-link bridges + latch** enable selective residual (E171).
3. Multi-trial fire select durable without retrain (E172).
4. Select is **bridge-dependent**: soft/hard R disruption silence prop; restore returns (E173/E174).
5. Pair-link is **necessary** (E175).
6. Association-specific (c0-only) bridge kill **not** achieved with simple band-endpoint emitters (E176 NULL).

## Patterns
`docs/patterns/port_multi_trial_association_residual.md`

## Do not farm
Re-running E171–E174 bars; residual means; full-port kill variants without new question.

## Open / next hard
- Arm-selective bridge surgery with finer targeting or replace-mode pair links
- Free talent still CLOSED PARTIAL (C16); free dual still blocked
- Brain R9 still blocked until free talent or deeper honest curriculum
