# Free dual talent NULL farm — formal closure (C27–C41 + C26)

**Date:** 2026-07-26  
**Depends on:** C16 CLOSED PARTIAL (ilw_strength_decay + wall seed-set unlock); C1–C15 earlier closed  
**Discipline:** After C27–C41, **stop farming free dual mechanism knobs** that are variants of inject+wall+single-config-toggle without a new substrate primitive.

## Verdicts (this farm)

| ID | Mechanism | Verdict | Note |
|----|-----------|---------|------|
| C26 | charge_latch_tau free dual | **FAILED** | hard-cap overrun |
| C27 | short pair_decay | NULL | |
| C28 | short triad_decay | NULL | |
| C29 | asymmetric L/R speed | NULL | |
| C30 | atom_repulsion_k | NULL | hurts |
| C31 | n_emit | NULL | |
| C32 | elevated r_1 | NULL | 0.75 ordered |
| C33 | PRIM7 sideband cull | NULL | pop collapse |
| C34 | elevated r_2 | NULL | pop collapse |
| C35 | lambda_gen | NULL | |
| C36 | tight freq_tolerance | NULL | pop collapse |
| C37 | slow global speed | NULL | |
| C38 | corr_plasticity | NULL | pop collapse |
| C39 | compartment_boundary | NULL | |
| C40 | lambda_dec | NULL | |
| C41 | asymmetric N_SIDE | NULL | treat worse |

## Doctrine

1. **C16** remains a free dual partial unlock: `ilw_strength_decay_tau` + midplane wall (seed-set).
2. Single-knob free dual inject+wall **variants in this table (C27–C41) do not unlock** ordered ≥0.90.
3. **C42 budget-fit PASS then C43 NULL:** wider `freq_tolerance=0.08` does **not** robustly unlock free dual at larger N (B1=0.67). Fragile seed-set signal; not a locked class.
4. Further free dual work: new primitive **not** in C27–C41 table and not silent bar retune of C16/C42/C43.

## Do not farm

pair/triad decay · speed asym/slow · atom_repulsion · n_emit · r_1/r_2 · sideband cull · lambda_gen/dec · **tight** freq_tol · corr_plasticity · compartment · N_SIDE asymmetry · latch-tau retry without design change

## Open

- **C42 wide freq_tol** free dual — replicate larger N (C43).
- Engineered port multi-trial curricula (E162–E193) closed separately — not free dual.
