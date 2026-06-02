# G34 — Set-based engram readout: does the written bridge SET physically persist?

Pre-registered: 2026-06-02 (BEFORE the run). G33 isolated the remaining blocker: with the
firing-propagation route cut by an engineered wall, persistent selective recall still
failed because the **region-mean bridge-strength** readout is drowned in bridge-turnover
noise on tiny cores (both regions oscillate 0↔6). The region-mean statistic is itself
suspect — diluted by freshly formed weak bridges and erased when written bridges decay.

This BET replaces the spatial-mean readout with a **set-based engram readout**, the
turnover-robust statistic the programme summary flagged as the open option. A memory is
the persistence of the SPECIFIC structure that was potentiated, not a regional average.

## Method
Run the BET-099/100 correlation-memory protocol, LOC arm, **no wall** (G33 confirmed the
write is strong without it; the wall only suppressed it). At STIM end snapshot the set of
**strong** bridges (b_strength ≥ 5.0). Identify each bridge by a turnover-robust key:
`frozenset({(slot_i, birth_i), (slot_j, birth_j)})` using k_birth, so a reused atom slot
(different birth time) is NOT mistaken for the original — the engram is tracked through
turnover, not by transient slot index. Three sets snapshotted at STIM end:
- **E** = strong bridges with both atoms in the stim region (the engram).
- **C** = strong bridges with both atoms in the control region (unstimulated negative).
- **R** = a random sample of strong bridges from the global pool, size-matched to E (null
  model = generic bridge decay rate).

Over POST, at each checkpoint compute the retention of each set = fraction of its keys
still present among the currently alive strong bridges.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G34a | Engram forms | \|E\| ≥ 5 strong bridges at STIM end |
| G34b | Engram persists | retention(E) ≥ 0.5 at the POST horizon (sim ≥ stim_end+2000 s) |
| G34c | Selective vs unstimulated | retention(E) − retention(C) ≥ 0.3 (mean over the POST window) |
| G34d | Beats the null | retention(E) ≥ 2 × retention(R) at the POST horizon |

PASS = G34a–d. PASS means the engram is a real, persistent, selectively-readable physical
structure — recall works once read with a turnover-robust set statistic, and the earlier
failures were a READOUT artifact (region-mean), not a substrate limit. That would be the
memory milestone. NULL (specifically G34b failing) means the written bridges physically
DISSOLVE under turnover — the engram does not survive the recall horizon on tiny cores —
which is the clean, decisive characterization of the deadlock as substrate turnover, not
readout. Both are real findings. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL/partial — and it OVERTURNS the G33 turnover hypothesis

| metric | value | bar | verdict |
|--------|-------|-----|---------|
| G34a engram forms | \|E\| = **3** | ≥ 5 | ✗ |
| G34b engram persists | retention(E) = **1.00** over the full 14 000 s POST | ≥ 0.5 | ✓ |
| G34c selective vs control | retE − retC = **0.00** | ≥ 0.3 | ✗ |
| G34d beats null | retE = retR = 1.00 | ≥ 2× | ✗ |

`|E|=3, |C|=3, global_strong=13`, and **retE = retC = retR = 1.00 at every one of 25 POST
checkpoints** (6500 → 20000 s); `n_strong` held at 13 the whole time.

**Verdict: NULL/partial — but the finding is the reframe, and it corrects G33.**

1. **Strong bridges are PERFECTLY persistent (G34b ✓, retention 1.00 over 14 000 s).** Once
   a bridge latches strong, the bistable well + anchoring + fusion_bond_block hold it
   indefinitely — `n_strong` is dead constant at 13. There is **no turnover of the strong
   engram at all.**

2. **Honest correction to G33.** G33 attributed the recall failure to "bridge-turnover
   noise eroding the engram." That was WRONG. The strong/written bridges do not turn over
   (G34b). G33's region-mean 0↔6 oscillation was the spatial mean averaging the stable
   strong core with transient WEAK bridges (strength ≈ 1.0) forming/breaking around it,
   plus region-membership drift as atoms move across the fixed x-band — a **readout
   artifact**, precisely what the set-based statistic was built to remove. The set readout
   shows the truth: the engram is stable.

3. **The real blocker is SELECTIVITY, not persistence or turnover.** With no wall, the
   unstimulated control region acquired its OWN equally-persistent strong core (|C| = |E| =
   3), contaminated by stim emissions during STIM. retE − retC = 0 → not selective. The
   memory is permanent but written in BOTH regions.

## What this composes (the path to the solve)
- G33: the engineered wall CONTAINS firing to the stim region (259×) — i.e. it prevents the
  control contamination that G34 just identified as the blocker.
- G34: the engram is PERMANENT (retention 1.00) and the set-based readout SEES it (region
  -mean was the artifact).
Therefore **G35 = wall + set-based readout**: containment stops the control core from
forming (retC → 0) while the stim engram persists (retE → 1.0, proven here) and is read by
set. Expected clean selective persistent recall even with a tiny core, since persistence is
total. The wall's write-suppression (G33b) is the one risk — but G34 shows even |E|=3 strong
bridges persist perfectly, so the wall only needs to let a FEW form in stim while keeping
control at zero. No threshold tuning; bars carried from G34 (set-based) + G33 (containment).
