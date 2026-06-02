# G37 — Specular mirror wall: does proper reflection write AND contain?

> **RETRACTED as a milestone (see G38).** The seed-42 PASS below did NOT replicate: G38
> (seeds 42/7/99) showed the selective engram is seed-dependent (|E|=0 on seed 99, control
> non-selective on seed 7). What IS robust is firing CONTAINMENT (300–330× every seed); the
> selective-recall PASS was within the tiny-core latching noise. No milestone. Kept below
> for the honest record.

Pre-registered: 2026-06-02 (BEFORE the run). G36 showed the clamp wall contains firing
259× but writes nothing (|E|=0) because it collapses every reflected vibration onto one
degenerate shell (r = R·0.999), erasing the interior charge field that drives co-firing.
G35's soft wall writes (|E|=3) but leaks (|C|=3). The identified defect is specific:
neither reflector is a proper specular barrier.

`compartment_mode='mirror'` mirrors the radial overshoot about the wall (r → 2R − r,
inward velocity), so a vibration that crosses to r=6.5 returns to r=5.5 — fully contained
(no r > R persists) yet distributed through the interior, where it keeps driving co-firing.
This is the one mechanism that could write AND contain.

## Method
Identical to G36 (BET-099/100 protocol, single LOC arm, set readout, firing tally) with
`compartment_mode='mirror'`.

## Bars (locked pre-run — same as G36)
| ID | Criterion | Bar |
|----|-----------|-----|
| G37a | Engram forms under the mirror wall | \|E\| ≥ 1 at STIM end |
| G37b | Engram persists | E_persist / \|E\| ≥ 0.5 at the POST horizon (sim ≥ stim_end+2000 s) |
| G37c | Selective (control near-blank) | \|C ∩ cur\| ≤ 1 at horizon AND (\|E ∩ cur\| − \|C ∩ cur\|) ≥ 1 |
| G37d | Containment active | stim firings ≥ 10× control firings during STIM |

PASS = G37a–d → clean selective persistent recall; the write/contain tension was an
implementation artifact of degenerate reflection, resolved by a proper specular wall.
The memory milestone. NULL (write suppressed OR control still contaminated) → the tension
is structural: even ideal reflection cannot separate the write field from the contamination
field because they are the same emitted vibrations. That closes the wall arc with the
consolidated finding. No post-hoc threshold tuning.

## RESULT (2026-06-02): PASS (seed 42) — multi-seed replication pending (G38)

| ID | metric | bar | verdict |
|----|--------|-----|---------|
| G37a engram forms | \|E\| = **3** | ≥ 1 | ✓ |
| G37b engram persists | E_persist = **3/3** over 14 000 s | ≥ 0.5 | ✓ |
| G37c selective | \|C\| = **1**, E−C = **2** | C≤1, E−C≥1 | ✓ |
| G37d containment | fire ratio = **321×** (ctrl fired 0) | ≥ 10× | ✓ |

`|E|=3 |C|=1 |global_strong|=14`, firing stim=321 ctrl=0; E and C persist exactly (3/3,
1/1) at all 28 POST checkpoints to 20 000 s.

**Verdict: PASS on the pre-registered bars (seed 42).** The specular mirror wall both
WRITES (|E|=3, the interior co-firing field survives because vibrations are mirrored
inward, not pinned to a shell) and CONTAINS (321× firing ratio, control fires 0 times),
so the stim engram forms, persists, and is selective against a near-blank control. The
write/contain tension that ran through G33–G36 was an artifact of degenerate reflection
(clamp pinned to one shell → no write; soft leaked → contamination); proper specular
reflection resolves it.

**Honest scope / what this is and is NOT.**
- It IS: selective (E−C=2; control fired 0×), persistent (retention 1.0 over 14 000 s),
  content-bearing in the minimal sense (a specific 3-bridge engram tracked by identity),
  built only from substrate primitives + an engineered §4.8 port wall + a turnover-robust
  set readout. The matched no-wall control (G34/G35) FAILS selectivity (|C|=3), as required.
- It is NOT yet robust: this is ONE seed (42; the whole G33–G37 arc used seed 42). The
  engram is tiny (3 bridges). |C|=1 is one residual control bridge (control fired 0×, so
  it is not firing-contamination, but it must be characterised).
- Before this is elevated to "the memory milestone" in MEMORY_PROGRAMME_SUMMARY, it must
  replicate across independent seeds with the matched no-wall control failing each time.
  **G38 runs seeds {42, 7, 99}** with the no-wall control per seed. Only if it holds will
  the milestone claim, the pattern entry, and the summary update be written. NULL on
  replication → seed-dependent, reported as such.
