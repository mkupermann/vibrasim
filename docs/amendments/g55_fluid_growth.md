# G55 — Fluid membrane growth: does turnover enable accretion, or is size homeostatic?

Pre-registered: 2026-06-02 (BEFORE the run). G53/G54 established that bond turnover makes the
membrane FLUID (partial self-repair, stable). Fresh question: does a fluid membrane GROW — accrete
new atoms from the continuous ambient supply and enlarge — where the rigid membrane is size-locked
(no free valence to add atoms)? Either outcome is informative: growth = a remarkable new capability;
size-stable = the fluid membrane has homeostatic SIZE control (turnover balances accretion/loss).

## Method
G30 substrate, lambda_gen on (steady material supply), node_thermal_speed=0.2, edge_closure_k=2.0,
NO wound. Record the largest bridged component size at the start of the growth window (after
settle) and over a long window (500 ticks). Arms: fluid (bond_turnover_rate=0.15) vs rigid (0.0).
Growth ratio = final / start. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G55a | Fluid stays coherent | fluid: never drops below 0.7× start (no dissolution), both seeds |
| G55b | Fluid GROWS | fluid: final/start ≥ 1.2 (accretion), both seeds |
| G55c | Rigid is size-locked | rigid: final/start ≤ 1.1, both seeds |

PASS = G55a–c → the fluid membrane GROWS by accretion while the rigid one is locked: turnover
enables growth, a new cell-precursor capability. NULL: if G55b fails the fluid membrane is
size-STABLE (homeostatic size — turnover balances gain/loss at a set size), itself an interesting
property; if G55a fails turnover dissolves it over long times. Honest either way. No post-hoc tuning.

## RESULT (2026-06-02): NULL/partial — the fluid membrane is SIZE-HOMEOSTATIC (stable, not growing)

| arm | seed | start | final | growth | min fraction |
|-----|------|-------|-------|--------|--------------|
| fluid | 42 | 130 | 142 | 1.09 | 1.00 |
| fluid | 7 | 141 | 141 | 1.00 | 1.00 |
| rigid | both | — | — | 1.00 | — |

G55a ✓ (never drops below start — coherent), G55b ✗ (no growth ≥1.2), G55c ✓ (rigid locked).
**Verdict: NULL on growth — but a clean property emerges: SIZE HOMEOSTASIS.** The fluid membrane
neither grows nor dissolves; bond turnover holds it at a characteristic set-point size (accretion
balances loss). It is a stable dynamic structure, not a growing/dividing one — growth/division
would require a different driver (surplus-forced expansion or a split mechanism), not present here.

**This adds to the fluid-membrane characterization:** turnover gives the membrane FLUIDITY
(partial self-repair, G53/G54) and SIZE HOMEOSTASIS (G55) while remaining stable — a dynamic,
self-maintaining structure. It does not grow or divide. A natural, honest culmination of the
structural thread.
