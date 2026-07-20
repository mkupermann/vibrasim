# FRONTIER — Belief path (active)

**Charter:** `docs/BELIEF_PATH.md`  
**Discipline:** `docs/DISCIPLINE_SHARP.md`  
**Updated:** 2026-07-20 (night autonomous)

## Live board (night run)

| ID | Verdict | One-line |
|----|---------|----------|
| A1–A2 | PASS | Density → bind |
| B1–B3,B5–B7 | PASS | Molecule content (scoped) |
| C1–C4 | CLOSED PARTIAL | Free dual-inject talent |
| PRIM1-D2 | PASS | Midplane χ=0 |
| PRIM2-D0 | PASS | ILW non-broadcast |
| C5 | NULL | ILW specialises; FREE 0.667 |
| E1 | NULL | Port trace; eq control bias |
| E2 | PASS | Port side trace + clean controls |
| E3 | NULL | Strength ≠ order (closed) |
| E4–E6 | PASS | Write-time storage + overwrite |
| E storage | CLOSED PARTIAL | External-map storage curriculum |
| PRIM3-D0 | PASS | L4 strength decay (recency) |
| E7 | PASS | Order via gap+decay |
| E8 | PASS | Cross-mid bridges (r₂=45,val=4) |
| E9 | PASS | Pair class from bridge endpoints |
| PRIM4-D0 | PASS | Multi-slot ILW |
| E10 | PASS | K=3 multiset port buffer |
| E11 | PASS | Dual exclusive pairs co-resident |
| E12 | PASS | No generative partner (boundary) |
| E13 | NULL | End-state cross charge (decay) |
| E14 | PASS | **Peak** cross-mid charge transfer |
| E15 | NULL | Selective recall fails (all-to-all graph) |
| PRIM5-D0 | PASS | Exclusive pair-link on dual write |
| E16 | **PASS** | Selective L0→R0 charge recall |
| E17 | **PASS** | Selective after decay hold |
| E18 | **NULL** | Charge-weighted end-state partner fails |
| E19 | **NULL** | Bridged end-state argmax fails (membrane) |
| E20 | **PASS** | Bridged + **peak** argmax partner (multi-trial) |
| PRIM6-D0 | **PASS** | `k_latch` holds bridge-prop mark |
| E21 | **PASS** | End-state partner via latch (not membrane) |
| E22 | **NULL** | Table-free map: rewire self-cons vacuous @K=2 |
| E23 | **NULL** | Table-free map: rewire gap still high @K=2 |
| Table-free map K=2 | **CLOSED PARTIAL** | `bp_e22_e23_notable_map_closure.md` |
| C6 | **NULL** | Hybrid attractor+free specs 1.0; free-only 0.778>0.75 ctrl |
| C7 | **NULL** | Scrambled seeds still specialise 0.67; correct 0.78 |
| Attractor+free class | **CLOSED PARTIAL** | `bp_c6_c7_attractor_free_closure.md` |
| E24 | **NULL** | K=3 multi-sample table-free: treat OK; rewire cons 0.63 |
| E25 | **PASS** | Table-free map + **bridge ablation** control |
| E26 | **NULL** | Latch tau=2 half-life bar not met |
| PRIM7-D0 | **NULL** | Sideband cull hurts free spec (0.67 vs off 0.78) |
| E27 | **NULL** | Map curriculum overwrite: A→B leaves 50/50 residual |
| PRIM8-D0 | **PASS** | Pair-link replace (forget old partner) |
| E28 | **PASS** | Curriculum A→B with replace: B=1.0 residual A=0 |
| C8 | **NULL** | Sequential free inject 0.78; sim 0.89 — timing not unlock |
| E29 | **PASS** | Two-hop charge relay L→M→R |
| E30 | **NULL** | Parallel paths + replace ON: 0 bridges (chain kill) |
| E31 | **PASS** | Parallel path isolation with replace OFF |
| E32 | **PASS** | Three-hop relay |
| E33 | **PASS** | Shared mid crosstalk (leak) |
| E34 | **PASS** | Fan-in OR |
| E35 | **PASS** | Diamond redundancy |
| E36 | **PASS** | Four-hop relay |
| E37 | **PASS** | Midplane dual isolated chains |
| E38 | **NULL** | AND-gate absent without prim (OR only) |
| PRIM9-D0 | **PASS** | Coincidence AND (2 firers → mid) |
| PRIM10-D0 | **NULL** | Lateral charge inhibit no exclusive WTA |
| C9 | **NULL** | Stationary free vel=0: no L4 form (pop=0) |
| PRIM11-D0 | **NULL** | XOR: both-clear works; single-L OR end-latch fails |

## What works (engineered port curriculum)

See `docs/patterns/port_circuit_primitives.md` + `coincidence_and_gate.md` — relays, isolation, OR, diamond, **AND**, curriculum, table-free map.

## Boundaries locked

| Boundary | Status |
|----------|--------|
| Free talent @0.90 pure | Still blocked (C1–C9, PRIM7) |
| Stationary free (vel=0) | No bind (C9) |
| Soft lateral inhibit WTA | No exclusive winner (PRIM10) |
| XOR (OR + AND-clear) | NULL PRIM11 — need cleaner inhibit timing/topology |
| Attractor±free hybrid | CLOSED PARTIAL (C6–C7) |
| AND without coincidence prim | No (E38); **with PRIM9 PASS** |
| Order without decay | CLOSED (E3) |
| Generative partner from L alone | No (E12) |
| Selective recall on all-to-all bridges | No (E15) |
| End-state via membrane charge alone | No (E13/E18/E19) — peak or latch |
| Multi-hop + replace ON | No (E30) |

## Next hard only

- Free talent only with mechanism **≠** known free dual classes  
- Inhibition / soft competition beyond hard AND  
- Brain R9 still blocked until C reopen or deeper curriculum

## Do not

Archive tracks · C5 FREE bar retune · K-band farm · E3 bar retune · lab_continuous smoke theater
