# G35 — Wall + set readout: clean selective persistent recall (the synthesis)

Pre-registered: 2026-06-02 (BEFORE the run). G33 + G34 compose to a prediction:
- G33: an engineered compartment wall CONTAINS firing to the stim region (259×), i.e. it
  prevents the control-region contamination that G34 identified as the real blocker.
- G34: the strong-bridge engram is PERMANENT (retention 1.00 over 14 000 s), and a set
  -based readout (bridges keyed by atom slot + k_birth) sees it cleanly; the region-mean
  readout that failed earlier was an artifact (weak-bridge churn + region drift).

So combining the wall (selectivity) with the set readout (correct instrument) should give
clean selective persistent recall — even with a tiny core, because persistence is total.
The one risk is G33's write-suppression: the hard position-clamp built a dense boundary
layer. G35 uses a **soft** wall (`compartment_mode='soft'`: reflect velocity, revert the
overshoot only) to remove that confound. G34 showed even |E|=3 strong bridges persist
perfectly, so the wall only needs to let a FEW form in stim while holding control at zero.

## Method
BET-099/100 protocol, two arms, set-based readout (STRONG = 5.0; key = frozenset of
(slot, k_birth)). Wall raised at STIM start, radius 6 on the stim region.
- **LOC + soft-wall** (the test).
- **LOC + no-wall** (matched control = G34 replica: contamination must occur).
At STIM end snapshot E = strong bridges in the stim region, C = strong bridges in the
control region. Track |E ∩ alive-strong| and |C ∩ alive-strong| through POST.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G35a | Engram forms under the wall | \|E\| ≥ 3 at STIM end (wall arm) |
| G35b | Engram persists | \|E ∩ cur\| / \|E\| ≥ 0.5 at the POST horizon (sim ≥ stim_end+2000 s) |
| G35c | Selective (control blank under wall) | \|C ∩ cur\| ≤ 1 AND (\|E ∩ cur\| − \|C ∩ cur\|) ≥ 2 at the horizon |
| G35d | Matched control contaminates | no-wall arm: \|C\| ≥ 2 at STIM end (selectivity is the WALL's doing) |

PASS = G35a–d. PASS = the first clean, selective, persistent, content-bearing memory in
the programme, built only from substrate primitives + an engineered port wall (CONCEPT
§4.8) and read by a turnover-robust set statistic — write by co-firing, contain by the
wall, persist by the bistable well, recall by the set. NULL: if G35a fails the soft wall
still suppresses the write (write/contain tension survives the gentler reflector); if G35c
fails the wall does not stop contamination (route is not vibration transit). Both are valid
findings. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL/partial — soft wall writes cleanly but leaks; tension moves to the wall

| ID | metric | bar | verdict |
|----|--------|-----|---------|
| G35a engram forms under wall | \|E\| = **3** | ≥ 3 | ✓ |
| G35b engram persists | E_persist = **3/3** over 14 000 s | ≥ 0.5 | ✓ |
| G35c selective (control blank) | \|C\| = **3**, C_persist = 3/3 | C≤1, E−C≥2 | ✗ |
| G35d no-wall contaminates | no-wall \|C\| = 3 | ≥ 2 | ✓ |

`wall arm: |E|=3 |C|=3, global_strong=36; no-wall arm: |C|=3, global_strong=13`. Every
strong bridge persists 3/3 over the full POST in both arms.

**Verdict: NULL/partial. Two clean findings:**

1. **The soft wall fixes G33's write-suppression (G35a ✓).** Under the soft reflector the
   stim engram forms (|E|=3) and persists perfectly — confirming the hard position-clamp
   was the culprit in G33b. The wall even densifies the stim region (global_strong 36 vs 13).

2. **But the soft wall does NOT make the memory selective (G35c ✗).** Control ends with
   |C|=3 strong bridges WITH the wall — identical to the no-wall arm (|C|=3), across G34,
   G35-nowall, and G35-wall (same seed). The write/contain tension has simply MOVED to the
   wall: the **clamp** wall contains firing (259×, G33) but suppresses the write; the
   **soft** wall writes cleanly but leaks emissions, so the control region still acquires
   its equivalent persistent core. Containment and write are still anti-correlated.

## Next (G36) — the decisive combination
G33 used the CLAMP wall (proven 259× firing containment → control should go near-blank) but
read it with the WRONG instrument (region-mean, which G34 showed is an artifact). G35 used
the right instrument (set) with the WRONG wall (soft, which leaks). **G36 = clamp wall +
set readout** is the untested cell: strong containment measured by the instrument that can
see a 1–3 bridge engram. If the clamp drives |C|→0 while the set readout still finds |E|≥1
persistent stim bridges, that is clean selective persistent recall. If |C| stays ≈3 even
under 259× containment, then the control core is INTRINSIC (the substrate autonomously
potentiates ~3 bridges per region from its own dynamics, not stim leakage) — which would be
the final, decisive characterization: selective local memory is impossible because the
medium generates equivalent structure everywhere, independent of targeted input.
