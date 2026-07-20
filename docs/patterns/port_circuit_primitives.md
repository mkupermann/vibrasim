# Pattern: Port circuit primitives (engineered graph)

## Source
E29–E37 PASS chain · PRIM5/6/8 · replace doctrine

## Circuit library (honest §4.8)

| Primitive | Result | Notes |
|-----------|--------|--------|
| Two-hop relay | E29 PASS | replace OFF |
| Three-hop | E32 PASS | |
| Four-hop | E36 PASS | |
| Parallel isolation | E31 PASS | distinct mids |
| Shared mid crosstalk | E33 PASS | leaks by design |
| Fan-in OR | E34 PASS | either L → R |
| Diamond redundancy | E35 PASS | survives one mid kill |
| Midplane dual chains | E37 PASS | half-box isolation |
| Curriculum overwrite | E28 PASS | replace ON |
| Table-free map + ablation | E25 PASS | |
| Fan-in **AND** | PRIM9 PASS | coincidence_and + k_coincidence_gate |
| Structural **NOT** | PRIM12 PASS | fire_kill_bridge_radius + emitter |
| **XOR** | E42 PASS | OR path + coincidence Mand + structural kill |
| Retrain after cut | E43 PASS | ILW pair_write rebuilds killed path |
| Soft weaken + full restore | E44 PASS | strength→0 then re-strengthen L–M & M–R |
| Selective soft cut | E45 PASS | I near M1 only; path2 intact |
| Path-switch curriculum | E46 PASS | cut1 → restore1+cut2 multi-trial |
| Graded soft attenuate | E47 PASS | frac=0.5 once keeps; many → silence |
| XOR retrain | E48 PASS | after both-cut, rebuild OR path |
| 3-path soft MUX | E49 PASS | select one of three via soft cut |
| Mid soft + A–B-only restore | E50 NULL | collateral outer-hop damage |
| Mid soft + outer-only restore | E53 NULL | mid hop also damaged |
| Mid soft + full 3-hop restore | E52 PASS | all hops must be rewritten |
| Hard mid r=8 | E51 NULL | endpoints out of radius |
| Hard mid r=12 + full restore | E54 PASS | structural cut recoverable |
| Soft cut + idle no retrain | E55 PASS | silence durable until rewrite |
| Dual 3-hop selective hard kill | E56 PASS | y-sep > kill radius isolates |
| Soft DEMUX shared L → 3 R | E57 PASS | fan-out select (≠ multi-L MUX) |
| Hard 3-path MUX | E58 PASS | hard-kill select + restore |
| Soft 2×2 crossbar | E59 PASS | identity/swap arm select |
| Hard 2×2 crossbar | E60 PASS | hard-kill identity/swap |
| AND-gated L–G–R relay | E61 NULL | G-only still drives R |
| Soft-disable AND input | E62 NULL | L1–M soft cut fails |
| Hard-disable AND input at L1 | E63 PASS | endpoint kill + restore |
| Soft-disable AND input at L1 | E64 PASS | soft endpoint (mid fails E62) |
| (L1∧L2) OR L3 hybrid | E65 PASS | AND + independent OR bypass |
| Soft-cut OR bypass (hybrid) | E66 PASS | AND path remains |
| Soft 2×2 concurrent dual-drive | E67 PASS | both R ON; single-L isolated |
| Soft 2×2 concurrent under swap | E68 PASS | swap map concurrent |
| Soft 2×2 reconfig concurrent | E69 PASS | id↔swap curriculum + concurrent |
| Hard-cut OR bypass (hybrid) | E70 PASS | hard analogue of E66 |
| Soft-cut + restore OR bypass | E71 NULL | L3–R-only restore fails |
| Soft-cut + disarm + restore | E72 PASS | residual emitters were the block |
| Hard-cut + disarm + restore OR | E73 PASS | structural recover OR bypass |
| Hybrid AND soft + disarm restore | E74 PASS | OR bypass unharmed |
| Dual cut + selective AND restore | E75 PASS | bypass stays silent |
| Dual cut + selective OR restore | E76 PASS | AND stays silent |
| Dual cut + full AND+OR restore | E77 PASS | both recover; L1-only gated |
| Hybrid path-switch OR↔AND | E78 PASS | multi-trial curriculum |
| Soft 2×2 dual-cut → identity | E79 PASS | selective restore after total cut |
| Soft 2×2 dual-cut → swap | E80 PASS | selective swap restore |
| Soft 2×2 dual-cut → full restore | E81 PASS | all arms; L0 fan-out |
| Soft 2×2 cut → id → swap | E82 PASS | multi-trial after wipe |
| Soft 2×2 cut → swap → id | E83 PASS | reverse multi-trial |
| Hard 2×2 dual-kill → identity | E84 PASS | structural wipe + restore |
| Hard 2×2 dual-kill → swap | E85 PASS | structural wipe + swap restore |
| Soft DEMUX dual-cut → select | E86 PASS | shared-L wipe + arm restore |
| Soft MUX dual-cut → select | E87 PASS | multi-L wipe + path restore |
| Hard DEMUX dual-kill → select | E88 PASS | structural shared-L wipe |
| Hard MUX dual-kill → select | E89 PASS | multi-L structural wipe |
| Soft MUX dual-cut → full restore | E90 PASS | all paths + isolation |
| Hard MUX dual-kill → full restore | E91 PASS | structural full restore |
| Soft DEMUX dual-cut → full + re-cut | E92 NULL | full OK; re-cut arm0 collaterals |

## Incompatible defaults
- **replace ON** ↔ multi-hop chains (E30)
- **shared mid** ↔ path isolation (E33)

## Not free talent
All above are engineered ports + ILW + bridges + latch. Free dual-inject talent remains blocked (C1–C8, PRIM7).
