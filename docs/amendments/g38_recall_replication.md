# G38 — Multi-seed replication of the G37 selective-persistent-recall result

Pre-registered: 2026-06-02 (BEFORE the run). G37 passed all four recall bars on seed 42
(specular mirror wall + set readout: |E|=3, |C|=1, fire 321×, persistence 1.0). Discipline
requires this replicate across independent seeds, with the matched no-wall control failing
each time, BEFORE it is called the memory milestone. This BET runs the mirror-wall arm and
the no-wall control arm for seeds {42, 7, 99}.

## Method
For each seed, two arms (BET-099/100 protocol, set readout, firing tally):
- **mirror**: `compartment_mode='mirror'`, wall raised at STIM start (the G37 condition).
- **no-wall**: `compartment_k=0` (matched-wallclock negative control).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G38a | Mirror writes a persistent engram, every seed | each seed: \|E\| ≥ 1 AND E_persist/\|E\| ≥ 0.5 at horizon AND fire ratio ≥ 10× |
| G38b | Mirror is selective, every seed | each seed: \|C ∩ cur\| ≤ 1 at horizon AND (\|E ∩ cur\| − \|C ∩ cur\|) ≥ 1 |
| G38c | No-wall control fails selectivity, every seed | each seed: no-wall \|C\| ≥ 2 at STIM end (contamination present without the wall) |

PASS = G38a, G38b, G38c hold for ALL THREE seeds → the result is robust: clean selective
persistent recall via substrate primitives + an engineered §4.8 port wall + set readout,
and the wall is demonstrably necessary (no-wall contaminates every seed). This is the
memory milestone of the BET-089→G38 programme; on PASS, write the docs/patterns entry and
update MEMORY_PROGRAMME_SUMMARY to record the SOLVE.

NULL: if any seed fails G38a/b, the recall is seed-dependent (report which and why); if
G38c fails (no-wall does NOT contaminate some seed), the wall is not always necessary and
the selectivity claim weakens. Either is reported honestly; no milestone claim on a partial.
No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — G37 was seed-dependent; NO milestone

| seed | mirror \|E\| | mirror \|C\| (horizon) | fire ratio | no-wall \|C\| |
|------|------------|------------------------|------------|---------------|
| 42 | 3 | 1 (selective) | 321× | 3 |
| 7 | 3 | **3 (NOT selective)** | 304× | **0** |
| 99 | **0 (no engram)** | 0 | 330× | 0 |

G38a ✗ (seed 99 |E|=0), G38b ✗ (seed 7 |C|=3, non-selective), G38c ✗ (seeds 7 & 99 no-wall
|C|=0, no contamination). **Verdict: NULL. The G37 PASS does not replicate — it was a
seed-42 coincidence.**

**Honest reading.**
- **Firing containment is robust** — the engineered specular mirror wall contains firing
  300–330× on EVERY seed. That mechanism works reliably.
- **Selective persistent recall is NOT robust.** At the n≈3 strong-bridge scale, which
  bridges latch is **stochastic**: the engram fails to form on seed 99, the control latches
  3 bridges despite the wall on seed 7, and the no-wall "contamination" that the G33–G37
  story relied on is itself inconsistent (absent on seeds 7 & 99). The single-seed G37
  result fell within this noise.
- The earlier G33–G37 narrative (build on seed 42) over-fit one seed. Caught by the
  pre-registered multi-seed gate — which is exactly its purpose.

**Consolidated finding (G33–G38).** With an engineered port wall we can now reliably
CONTAIN firing (new, robust capability) and we confirmed strong bridges PERSIST (retention
1.0) and that a set-based readout is the correct instrument. But selective *content* recall
is still bounded by **stochastic latching on a tiny core** — the same scale limit the
memory-programme summary reached, now isolated cleanly (containment is no longer the gap;
core size / latching noise is). The indicated next lever is SCALE: write the engram on a
LARGE persistent core (the G28/G30 ~110-atom lattice) so that which-bridges-latch noise
averages out, and re-test selectivity across seeds. No milestone is claimed.
