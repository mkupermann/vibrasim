# G96 — Membrane-contained maintenance: resolve "maintenance = contamination" by physical isolation

## Pre-registration (locked BEFORE run)
G94 failed because open maintenance flux drifted to control (maintenance = contamination) and a culled
pulse was too weak to sustain the engram atoms. G96 contains the flux: a two-way SEALED vibration
compartment (sphere, mode='seal') around the stim engram. lambda_gen=0 and injection ONLY inside the
seal, so the seal both (a) retains maintenance flux at a higher interior density to feed the engram
atoms, and (b) blocks any flux from drifting out to contaminate control. Control stays blank by
ISOLATION, not by culling.

Setup: box=30, seal centre (7.5,15,15) radius 7 (spans x ~0.5-14.5; control at x=22.5 is outside).
disconnected (boundary=15), refractory (0.5), consolidation (4.0). WARMUP cull+blank once; n=6 write
inside the seal during STIM; n=2 maintenance inside the seal each POST tick. No global culling in POST.
Arms: SEAL (mode='seal') and NOSEAL (mode off) — both with maintenance — to isolate the seal.

**Bars (locked):**
- G96a engram persists (SEAL): stim atom_persist >= 0.6 AND bridge_persist >= 0.5 (both seeds)
- G96b control blank (SEAL)   : control strong-bridge persist <= 1 (both seeds)
- G96c seal is the active ingredient: NOSEAL control strong-bridge persist >= 2 (both seeds) — removing
  the seal lets flux contaminate control (negative control must lose selectivity)

PASS = G96a AND G96b AND G96c -> contained maintenance gives selective persistent memory; the
deadlock's persistence horn is broken by physical isolation. Else NULL/PARTIAL.

## Result
_(pending run)_
