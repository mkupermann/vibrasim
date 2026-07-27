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
| Soft DEMUX full + hard re-cut | E93 PASS | hard r=8 local after full |
| Soft DEMUX wide-sep + soft re-cut | E94 PASS | mid dist > soft radius |
| Hard DEMUX full + hard re-cut | E95 PASS | structural shared-L recut |
| Soft MUX full + soft re-cut | E96 NULL | separate-L still mid-collateral |
| Soft MUX wide-sep + soft re-cut | E97 PASS | mid dist > soft radius |
| Soft MUX full + hard re-cut | E98 PASS | hard r=8 local on tight sep |
| Hard MUX full + hard re-cut | E99 PASS | hard multi-L wipe-restore-recut |
| Hard MUX wide + soft re-cut | E100 PASS | soft re-cut after hard wipe |
| Soft 2×2 wide full + re-cut 00 | E101 NULL | fan-out OK; cut00 misses R0 silence |
| Soft 2×2 full + hard re-cut 00 | E102 NULL | hard also fails mid re-cut on fan-out |
| Soft 2×2 endpoint R0 soft cut | E103 NULL | L0 selective OK; shared R0 hits L1 |
| Soft 2×2 cut both into R0 | E104 PASS | all R0 in-edges cut after full restore |
| Soft 2×2 cut identity diag | E105 PASS | full restore then pure swap |
| Soft 2×2 cut swap diag | E106 PASS | full restore then pure identity |
| Soft 2×2 multi-trial diag switch | E107 PASS | swap↔identity after full |
| Hard 2×2 cut identity diag | E108 PASS | hard pure swap after full |
| Hard 2×2 cut swap diag | E109 PASS | hard pure identity after full |
| Soft 2×2 selective restore after R0 dual-cut | E110 NULL | L0 OK; L1→R0 leak |
| Soft 2×2 partial restore after identity-diag | E111 NULL | L0 fanout OK; L1 isolation fails |
| Soft 2×2 dual restore after R0 silence | E112 PASS | both L fanout recovered |
| Hard R0 dual-cut + soft restore 00 | E113 NULL | same L1 leak as E110 |
| Soft 2×2 dual restore after identity-diag | E114 PASS | both cut arms → concurrent |
| Hard R0 dual-cut + dual soft restore | E115 PASS | hard silence recoverable dual |
| Soft 2×2 dual restore after swap-diag | E116 PASS | both cut arms → concurrent |
| Soft 2×2 multi-trial R0 silence cycle | E117 PASS | silence↔dual restore↔silence |
| Hard 2×2 multi-trial R0 silence cycle | E118 PASS | hard silence↔dual soft restore |
| Soft 2×2 split R0 selective restore | E119 PASS | non-shared R0a/R0b L-selective |
| Hard split R0 cut + soft restore 00 | E120 PASS | hard silence L-selective restore |
| Soft split R0 multi-trial selective | E121 PASS | silence↔restore00↔recut00 |
| Hard split R0 multi-trial selective | E122 PASS | hard silence↔restore00↔hard recut |
| Dual 3-hop soft wipe-restore-recut | E123 NULL | wipe-restore OK; soft recut p0 fails |
| Dual 3-hop soft wipe + hard recut p0 | E124 NULL | hard recut after wipe-restore fails |
| Dual 3-hop wide soft wipe-restore-recut | E125 NULL | y-sep=24 soft recut still fails |
| Dual 3-hop hard wipe-restore-hard recut | E126 NULL | hard wipe base same recut fail |
| Dual 3-hop multi-site hard recut after wipe | E127 NULL | multi-hop mids still B3=0 |
| Coincidence AND soft dual wipe + restore | E128 PASS | dual fire recovers after wipe |
| Coincidence AND hard dual wipe + restore | E129 PASS | hard wipe-restore dual ON |
| Coincidence AND multi-trial soft wipe-restore | E130 PASS | wipe↔restore↔wipe↔restore |
| Coincidence AND selective L1 restore after dual wipe | E131 NULL | L1-only already dual ON |
| Coincidence AND multi-trial hard wipe-restore | E132 PASS | hard wipe↔restore cycle |
| Coincidence AND hard dual wipe + selective L1 | E133 PASS | L1-only dual OFF until L2 |
| Coincidence AND soft wipe + L1–M hop-only | E134 NULL | residual L2 still dual ON |
| Coincidence AND multi-trial hard selective re-arm | E135 PASS | L1-only OFF both ON L1-only OFF |
| Coincidence AND hard wipe L2-first selective | E136 PASS | order-symmetric re-arm |
| Hybrid hard dual wipe + selective AND | E137 PASS | hard analogue of E75 |
| Hybrid hard dual wipe + selective OR | E138 PASS | hard analogue of E76 |
| Hybrid hard multi-trial path-switch OR first | E139 PASS | hard E78 OR↔AND↔OR |
| Hybrid hard multi-trial path-switch AND first | E140 PASS | hard E78 AND↔OR↔AND |
| Cascade AND multi-hop soft wipe-restore | E141 PASS | (L1∧L2)→M→A→R |
| Cascade AND multi-hop hard wipe-restore | E142 PASS | hard dual wipe full restore |
| Cascade AND hard selective L1 re-arm | E143 PASS | E133 doctrine on cascade |
| Cascade multi-trial hard selective L1 | E144 PASS | multi-trial cascade re-arm |
| Cascade hard selective L2-first | E145 PASS | order-symmetric cascade |
| Hybrid cascade hard selective AND | E146 PASS | cascade AND + OR bypass |
| Hybrid cascade hard selective OR | E147 PASS | OR restore AND stays off |
| Hybrid cascade multi-trial path-switch OR first | E148 PASS | OR↔cascade AND↔OR |
| Hybrid cascade multi-trial path-switch AND first | E149 PASS | cascade AND↔OR↔AND |
| Dual cascade hard selective path0 | E150 PASS | parallel cascade AND y-sep |
| Dual cascade hard wipe-restore both | E151 PASS | dual wipe full restore |
| Dual cascade multi-trial hard selective p0 | E152 PASS | silence↔restore↔silence |
| Dual cascade hard selective path1 | E153 PASS | path-order symmetry |

## Soft re-cut doctrine (E92–E100)
After full wipe+restore, selective soft re-cut needs **mid distance > soft radius** (E94/E97/E100) or use **hard local kill** (E93/E95/E98/E99). Separate-L alone does not fix soft mid-collateral. See `port_wipe_restore.md`.

## Incompatible defaults
- **replace ON** ↔ multi-hop chains (E30)
- **shared mid** ↔ path isolation (E33)

## Not free talent
All above are engineered ports + ILW + bridges + latch. Free dual-inject talent remains blocked (C1–C8, PRIM7).
