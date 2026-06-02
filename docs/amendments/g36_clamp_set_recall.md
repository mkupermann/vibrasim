# G36 — Clamp wall + set readout: the decisive cell

Pre-registered: 2026-06-02 (BEFORE the run). Four cells of (wall × readout) have been run:
- G33: clamp wall + region-mean readout → NULL (wrong instrument; region-mean is an artifact).
- G34: no wall + set readout → engram permanent but not selective (control core present).
- G35: soft wall + set readout → write clean but wall leaks (|C|=3).
- **G36: clamp wall + set readout → UNTESTED.** The clamp gives the strongest containment
  measured (259× firing, G33); the set readout is the instrument that can see a 1–3 bridge
  engram (G34). This is the cell that could resolve the write/contain tension: strong
  containment should drive the control core toward zero, and the set readout can detect even
  a tiny stim engram (persistence is total, G34, so 1 bridge suffices as content).

## Method
BET-099/100 protocol, single LOC arm, `compartment_mode='clamp'`, wall raised at STIM start
(radius 6 on the stim region). Set-based readout (STRONG=5.0; key = frozenset of (slot,
k_birth)). Tally firing in stim vs control during STIM to confirm containment. At STIM end
snapshot E (stim strong bridges) and C (control strong bridges); track persistence through
POST.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G36a | Engram forms under the clamp | \|E\| ≥ 1 at STIM end |
| G36b | Engram persists | E_persist / \|E\| ≥ 0.5 at the POST horizon (sim ≥ stim_end+2000 s) |
| G36c | Selective (control near-blank) | \|C ∩ cur\| ≤ 1 at the horizon AND (\|E ∩ cur\| − \|C ∩ cur\|) ≥ 1 |
| G36d | Containment active | stim firings ≥ 10× control firings during STIM |

PASS = G36a–d → clean selective persistent recall: the engineered clamp wall contains the
write to the stim region, a tiny permanent engram forms there, control stays blank, read by
the set statistic. The memory milestone of the whole programme. 

Two NULL modes, both decisive: (i) G36a fails (|E|=0) → the clamp suppresses the write
entirely; with soft-leaks (G35) on the other side, the write/contain tension is fundamental
to this reflection mechanism. (ii) G36c fails with |C| ≈ 3 despite G36d containment → the
control core is INTRINSIC (the substrate self-potentiates ~3 bridges/region from its own
dynamics, not stim leakage), so selective local memory is impossible in this medium. No
post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — clamp contains perfectly (259×) but suppresses the write entirely

| ID | metric | bar | verdict |
|----|--------|-----|---------|
| G36a engram forms | \|E\| = **0** | ≥ 1 | ✗ |
| G36b engram persists | — (|E|=0) | ≥ 0.5 | ✗ |
| G36c selective | \|C\| = **0** | C≤1, E−C≥1 | ✗ (E−C = 0) |
| G36d containment active | fire ratio = **259×** | ≥ 10× | ✓ |

`|E|=0 |C|=0 |global_strong|=6`, firing stim=259 ctrl=1. Outcome (i) — the decisive one.

**Verdict: NULL — and it completes the (wall × readout) 2×2 with a clean structural result.**

1. **The clamp contains firing perfectly (259×) yet writes NOTHING (|E|=0).** Intense
   firing in stim (259 events) produces zero strong bridges. The co-firing write needs
   bridged-neighbour atom PAIRS to fire within tau_LTP; the clamp pins every reflected
   vibration to one degenerate shell (r = R·0.999), away from the interior atoms, so the
   internal charge field that drives co-firing pairs is destroyed. Firing without
   co-firing-structure → no potentiation.

2. **The control core is contamination, NOT intrinsic.** |C| = 3 without the clamp
   (G34/G35) but |C| = 0 here — the clamp removed it. So the control's strong bridges came
   from stim emissions reaching control via VIBRATION TRANSIT. The clamp blocks that
   route — but the same route is the write mechanism.

3. **The 2×2 is complete and monotonic — no win cell:**
   | wall \ readout | region-mean | set |
   |---|---|---|
   | none | (artifact) | G34: \|E\|=3 permanent, \|C\|=3 (contaminated) |
   | soft | — | G35: \|E\|=3 writes, \|C\|=3 LEAKS |
   | clamp | G33: 259× contains, write suppressed | G36: 259× contains, \|E\|=0 |

   Containment strength trades off monotonically against write strength. **The emitted
   -vibration field is simultaneously the write substrate and the contamination vehicle —
   the same physical channel — so a reflective spatial wall cannot separate them.**

## One identified defect, one more test (G37)
The clamp's failure has a SPECIFIC cause: it collapses all reflected vibrations onto a
single shell (r = R·0.999), erasing the interior field. Proper SPECULAR reflection
(mirror the radial overshoot: r → 2R − r, keeping the inward speed) would contain fully
(no r > R ever persists) WITHOUT pinning — vibrations stay distributed through the
interior and keep driving co-firing. G37 tests this 'mirror' wall mode. If it writes
(|E|≥1) AND contains (|C|≤1), the tension was an implementation artifact, not fundamental.
If it ALSO fails, the write/contain inseparability is confirmed structural and the arc
closes with that consolidated finding.
