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

## RESULT (2026-06-02): NULL — the engram won't grow, and persistence is seed-dependent

| seed | \|E\| @ STIM end | \|E\| @ horizon | \|C\| | fire |
|------|------------------|------------------|-------|------|
| 42 | 1 | 1 | 0 | 176× |
| 7 | 6 | 6 | 0 | 175× |
| 99 | 4 | **0 (dissolved)** | 4 | 251× |

G39a ✗ (|E| max 6, never ≥10), G39b ✗ (seed 99 engram dissolved to 0), G39c ✗,
G39d ✓ (containment robust). **Verdict: NULL — scale-via-injection does not work.**

1. **The engram will not grow on demand.** Tripling the injected drive (n=120 vs 40,
   σ=2.5 vs 1.0) left |E| at 1–6 strong bridges. The strong-bridge count is capped by the
   co-firing + bistable dynamics, not by input — you cannot enlarge the engram this way.
2. **Persistence is itself seed-dependent at this scale.** Seed 99's 4 strong bridges
   DISSOLVED to 0 by the horizon — the "retention 1.0" seen on seeds 42/7 (and in G34/G37)
   is NOT universal; on a small stochastic core even persistence is unreliable.
3. Containment remains robust (175–251×) — the only thing that does.

**This closes the scale lever (via injection).** Selective persistent content recall is a
robust NEGATIVE in this plasticity regime: the engram is small (1–6 bridges), stochastic in
both formation and persistence, and cannot be grown by stronger input. The one untested
variant remaining is a fundamentally different substrate — correlation write on the LARGE
G28/G30 ~110-atom lattice (a different formation regime, not more injection) — but the
pattern across G33–G39 (every selective-recall attempt NULL or seed-flukey) indicates
diminishing returns on the recall thread. Decision recorded in LOGBOOK.
