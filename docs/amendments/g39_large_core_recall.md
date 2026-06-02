# G39 — Scale test: does a LARGE engram core make selective recall robust?

Pre-registered: 2026-06-02 (BEFORE the run). G38 isolated the remaining blocker: on n≈3
strong-bridge cores, WHICH bridges latch is stochastic, so selective recall did not
replicate across seeds even with robust firing containment (mirror wall) and a correct
set readout. The indicated lever is SCALE — a larger engram so latching noise averages out.

## Method
The G37/G38 mirror-wall + set-readout protocol, but with an ENLARGED stim core: injection
`n=120, sigma=2.5` (vs 40 / 1.0) and a larger measurement region `half=5` (vs 3), all still
inside the radius-6 compartment wall. Seeds {42, 7, 99}. Set readout (STRONG=5.0, key =
slot+k_birth). Per seed: |E|, |C|, persistence at horizon, firing ratio.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G39a | Large engram forms, every seed | \|E\| ≥ 10 at STIM end |
| G39b | Engram persists, every seed | E_persist / \|E\| ≥ 0.5 at the POST horizon (sim ≥ stim_end+2000 s) |
| G39c | Selective AND replicates | (\|E∩cur\| − \|C∩cur\|) ≥ 0.5·\|E\| at horizon, EVERY seed |
| G39d | Containment active, every seed | stim firings ≥ 10× control firings during STIM |

PASS = G39a–d for ALL THREE seeds → scale resolves the latching noise: robust, selective,
persistent, content-bearing memory on a large engineered-compartment core. THIS would be
the memory milestone (robust, not single-seed). On PASS: write the docs/patterns entry and
update MEMORY_PROGRAMME_SUMMARY to record the SOLVE.

NULL: if |E| stays small (G39a fails) the substrate cannot grow the engram on demand; if
|E| is large but G39c still fails per-seed, latching noise is NOT averaged out by scale and
the deadlock is deeper than core size. Either is reported honestly; no milestone on a
partial. No post-hoc threshold tuning.
