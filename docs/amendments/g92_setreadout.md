# G92 — Set-based readout of the engram (quiet + refractory + consolidation, n=6)

## Pre-registration
G91 left recall on the 0.44 region-mean plateau with a strong write (0.83) and a region-mean-blank
control (uni-post 0.00). Hypothesis: 0.44 is the G34 region-mean dilution artifact — the consolidated
engram is permanent but weak new bridges dilute the region mean. Read the SET of strong bridges
(strength >= 5.0) in the stim vs control region by bridge identity, tracked into POST.
**Bars (locked before run):**
- G92a engram forms: |E(stim)| >= 3 at STIM_END (both seeds)
- G92b engram persists: horizon E_persist >= 0.5·|E| (both seeds)
- G92c selective: ctrl persist <= 1 AND (E_persist − C_persist) >= 2 (both seeds)

## Result
| seed | |E(stim)| | |C(ctrl)| | E_persist (horizon) | C_persist |
|------|----------|-----------|---------------------|-----------|
| 42   | 6        | 1         | 1                   | 1         |
| 7    | 10       | 7         | 2                   | 5         |

G92a True · G92b **False** · G92c **False** → **VERDICT: NULL**

## Finding — the hypothesis is REFUTED, twice over
The 0.44 plateau is NOT (only) a region-mean dilution artifact. The set readout shows two real effects
the region mean hid:
1. **The strong engram bridges DECAY in POST.** Only 1–2 of 6–10 survive at strength >= 5 to the
   horizon. Consolidation (BET-108) re-pins bridge *strength* to `high` every tick, but only while the
   bridge stays ALIVE — so the pin does not explain the loss; something is killing the bridges.
2. **Control is not actually blank at the bridge level.** Seed 7 has 7 strong control bridges, 5 of
   which persist — MORE than the engram (2). Region-mean's "uni-post 0.00" was dilution masking real
   strong control bridges. The set metric is the honest readout; it exposes residual contamination.

Mechanistic lead (G93): `apply_correlation_plasticity` re-pins consolidated strength AFTER
`decay_bridges` and the node-decay calls each tick. A consolidated bridge can still die if its
anchoring ATOMS erode — and in the quiet substrate (free vibrations culled, lambda_gen=0, no
regeneration) the engram atoms have no flux to sustain them. G93 tracks the engram atom set vs the
bridge set through POST to test whether atom erosion is the persistence root.
