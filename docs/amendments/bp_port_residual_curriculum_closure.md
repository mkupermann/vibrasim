# Port multi-trial association residual curriculum — CLOSED PASS (E162–E168)

**Date:** 2026-07-26  
**Scope:** Engineered §4.8 ILW ports; multi-trial learning scored **without** baked class map in readout.  
**Not:** generative partner-from-L (E12 still No); free dual talent (still CLOSED PARTIAL C16 family).

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E162 | PASS | Simultaneous dual multi-trial → R residual after L-only; control no partner |
| E163 | PASS | Multislot OFF c0→c1 last-write residual reconfig |
| E164 | PASS | Soft R-port kill does not clear residual |
| E165 | PASS | Hard R-port kill does not clear residual |
| E166 | PASS | Multislot ON multi-assoc capacity (both R bands retained) |
| E167 | PASS | Temporal-gap L→gap→R residual (not simultaneous-only) |
| E168 | PASS | Write-order L-first vs R-first residual order-blind (Δ=0) |

## Doctrine
1. Residual = **content co-presence** after multi-trial dual (or sequential gap) train + L-only probe.
2. Multislot OFF → last-write residual reconfig; multislot ON → multi-assoc capacity.
3. Soft/hard port kill leaves residual (E155/E156-class durability).
4. Temporal separation and write order do not gate residual formation under these bars.
5. Still **not** generative recall of partner after R wipe-and-no-restore (E12).

## Pattern
`docs/patterns/port_multi_trial_association_residual.md`

## Do not farm
Further residual kill/order/gap variants without a **new** scientific question (e.g. true partner generation, map-free multi-class discrimination beyond means, free talent).

## Next hard
- Free talent: mechanism ≠ dual-inject / decay-tau / port-seed / scaffold / latch-tau / BTSP / STDP / dream / bridge (all tried).
- Or map-free multi-class **discrimination** residual (probe L selects which R band) — harder than co-presence.
