# G93 — Is the persistence blocker ATOM EROSION? (ROOT test)

## Pre-registration
G92's set readout showed consolidated/strong engram bridges decay in POST even though consolidation
re-pins bridge STRENGTH to `high` every tick. The pin only holds while the bridge stays ALIVE; a
bridge dies if its anchoring atoms die. In the quiet substrate (free vibrations culled during STIM,
lambda_gen=0, no regeneration) the engram atoms have no flux to sustain them. Track, through POST,
the engram ATOM set (level>=4 nodes in stim region at STIM_END) and the strong-bridge set.
**Bars (locked before run):**
- G93a atoms erode: atom_persist(horizon) < 0.6 (both seeds) → confirms erosion
- G93b bridges die with atoms: bridge_persist <= atom_persist + 0.1 (both seeds) → bridges track atoms

## Result
| seed | atoms |A|→persist | atom_persist | bridges |B|→persist | bridge_persist |
|------|-------------------|--------------|---------------------|----------------|
| 42   | 23 → 6            | 0.26         | 6 → 0               | 0.00           |
| 7    | 27 → 7            | 0.26         | 10 → 2              | 0.20           |

G93a True · G93b True → **ROOT CONFIRMED**

## Finding — the persistence blocker is ATOM EROSION, not bridge decay
Both seeds: the engram atoms lose ~74% of their members by horizon (persist 0.26), and the bridges
die with (or faster than) their atoms. Consolidation re-pins bridge *strength* but cannot keep a
bridge alive once its level>=4 anchoring atoms erode under `decay_unstable_nodes` /
`decay_high_level_nodes` — and in the quiet substrate there is no vibration flux to sustain those
atoms after STIM injection stops.

This resolves the entire 0.44-recall plateau that has dogged the memory programme since G66:
- selective WRITE — solved (G89/G91, strong selective write, contamination controllable)
- persistent RECALL — blocked HERE, at the atom layer, not the bridge layer

**The fix is structural, not a tuning knob:** the substrate must be quiet GLOBALLY (so the control
region stays blank — no self-activity to drown signal, the G83 root) but MAINTAINED LOCALLY (so the
engram atoms keep their flux and survive). That is exactly a proto-cell membrane's function — a local
container that retains vibration flux — which unifies the proto-cell thread (G30–G46) with the memory
thread. G94 tests localized maintenance: feed the stim region a minimal local flux through POST while
the control region stays culled, and check that the engram persists AND control stays blank.
