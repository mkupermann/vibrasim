# G33 — Engineered compartment containment resolves the write/contaminate tension

Pre-registered: 2026-06-02 (BEFORE the run). The memory programme (BET-089→102) reached
3/4: persistent lattice ✓, selective write ✓, transient recall ✓, but **clean persistent
selective recall ✗**. Diagnosed root cause (MEMORY_PROGRAMME_SUMMARY): NOT scale and NOT
the learning rule, but **connectivity** — on a homogeneous connected substrate, activity
PERCOLATES out of the stim region (BET-102), and the one knob that contained it (n_emit=0,
BET-100) also killed the write, because **emission is BOTH the write mechanism (co-firing
bridged pairs) AND the contamination mechanism (propagation to control)**. The summary's
prescription: **engineered modular compartments** (CONCEPT §4.8 — ports are ENGINEERED;
internals emerge) so activity cannot percolate.

## What is added (ENGINEERED, charter-sanctioned)
`apply_engineered_compartment(world, dt)` — a new tick step, **no-op when
`compartment_k == 0`** (default). When enabled it reflects every alive free vibration that
is at/beyond a fixed engineered sphere (centre `compartment_centre`, radius
`compartment_radius`) and moving OUTWARD: velocity radial component flipped inward, position
clamped just inside. This is a port wall — it keeps a region's own emissions LOCAL
(co-firing write proceeds at full strength) while preventing them from propagating to the
control region. It does not touch bound atoms, only free vibrations. This is the same
reflection primitive validated in G32, applied at an engineered boundary instead of an
emergent one.

## Protocol
Exactly the BET-099/100 correlation-memory protocol (box 30³, stim region x=7.5, control
x=22.5, WARMUP 3000 s → localized/uniform STIM 3000 s → field cleared → POST to wall
budget; correlation plasticity ON, emission ON). The ONLY addition is an engineered
compartment sphere of radius 6 centred on the stim region (wall at x≤13.5, well short of
control at x≈22.5). Arms:
- **LOC+wall** — localized stim, compartment ON (the test).
- **UNI+wall** — both regions stimulated, compartment ON (negative control: can't fake selectivity).
- **LOC no-wall** — localized stim, compartment OFF = BET-099/100 baseline (matched-wallclock control: percolation must destroy selectivity).

Readout = fraction of checkpoints selective (`stim_mean>3.0 AND ctrl_mean<3.0`), the
noise-robust metric locked in BET-100.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G33a | LOC+wall selective firing | stim firings ≥ 3× control during STIM |
| G33b | LOC+wall selective write | fraction of STIM checkpoints selective ≥ 0.5 |
| G33c | LOC+wall persistent recall | fraction of POST checkpoints (≥ stim_end+2000 s) selective ≥ 0.5 |
| G33d | UNI+wall negative control FAILS | uniform arm POST selective fraction < 0.25 |
| G33e | LOC no-wall matched control FAILS | no-wall LOC POST selective fraction < 0.25 (percolation) |

PASS = G33a–c hold AND G33d, G33e both fail (controls behave). PASS means an engineered
compartment wall resolves the write/contaminate tension and delivers — for the first time
in the programme — clean, persistent, selective recall, confirming the diagnosis that the
blocker was connectivity and the fix is engineered modularity. NULL would mean even
containment of emitted vibrations does not yield persistent selective recall (e.g. the
contamination route is bridge percolation, not vibration transit, so a vibration wall is
insufficient) — a valid finding that further localizes the deadlock. No post-hoc tuning.

## RESULT (2026-06-02): NULL — containment cuts the leak but exposes turnover as the real blocker

| metric | value | bar | verdict |
|--------|-------|-----|---------|
| G33a selective firing (LOC+wall) | **259×** | ≥ 3× | ✓ |
| G33b selective write during STIM | **0.00** | ≥ 0.5 | ✗ |
| G33c persistent recall (POST) | 0.36 | ≥ 0.5 | ✗ |
| G33d UNI+wall control | 0.00 | < 0.25 | ✓ |
| G33e LOC no-wall matched control | **0.44** | < 0.25 | ✗ |

**Verdict: NULL** (G33a,d pass; G33b,c,e fail). Three honest findings:

1. **The wall works as a firing barrier (G33a, 259×).** The engineered compartment cleanly
   cuts the firing-propagation route the summary blamed for percolation — firing is
   contained to the stim region 259:1 (vs the no-wall arm where it leaks). The reflection
   mechanism (validated in G32) does its job at an engineered boundary.

2. **But confinement SUPPRESSES the write (G33b, 0.00).** Under the wall, stim bridges only
   reach ~2.4–3.0 during STIM; the no-wall arm reaches 3.2–6.0. Reflecting every emission
   back into a 6-unit sphere — plus 40 injected vibrations/tick — makes a turbulent,
   over-dense region where atoms/bridges churn (high turnover) instead of latching. The
   containment that stops contamination also stops the co-firing pairs from settling. This
   is a fresh face of the write/contaminate coupling (Pattern 02): cutting propagation by
   reflection inward degrades the write. (Confound noted: the hard position-clamp to
   R·0.999 each tick builds a dense boundary layer; a gentler velocity-only reflector
   (G34) is the clean re-test.)

3. **Recall still fails — and the no-wall control did NOT cleanly flood (G33c 0.36, G33e
   0.44).** In BOTH arms the stim and control region-mean bridge strengths oscillate 0↔6
   across POST. The selectivity isn't destroyed by clean contamination (G33e is ~chance,
   not a flood) — it is **drowned in bridge-turnover noise** on tiny-n cores (n≈3–17 per
   region). This is the SECOND root cause the programme summary listed ("per-bridge state
   erodes under turnover; tiny-population cores give noisy readouts"), now isolated:
   propagation containment is **necessary but not sufficient**; with the leak cut, the
   remaining blocker is turnover, not connectivity.

## What this localizes (honest)
The deadlock has two layers. Layer 1 (propagation/percolation) is addressable by an
engineered wall — G33a proves the route can be cut. Layer 2 (bridge turnover → noisy,
non-persistent region-mean readout on few elements) remains and now dominates. The
region-mean-strength readout is itself part of the problem: it is diluted by freshly
formed weak bridges and erased when written bridges decay. **Next (G34):** (a) a
velocity-only (non-clamping) wall to remove the write-suppression confound, and (b) a
turnover-robust readout — track the SPECIFIC set of bridges potentiated during STIM and
measure THAT set's persistence, instead of a region spatial mean. If recall still fails
with both, the consolidated finding is that selective persistent memory in this substrate
is bounded by bridge turnover on small cores — a structural property requiring either
bond-protection (consolidation, BET-108/109) or a fundamentally different, set-based
engram representation.
