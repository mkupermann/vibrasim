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
| arm     | seed | atoms→persist | atom_persist | bridges→persist | bridge_persist | ctrl_persist |
|---------|------|---------------|--------------|-----------------|----------------|--------------|
| SEAL    | 42   | 12 → 3        | 0.25         | 0 → 0           | 0.00           | 0            |
| SEAL    | 7    | 31 → 10       | 0.32         | 9 → 3           | 0.33           | 4            |
| NOSEAL  | 42   | 12 → 3        | 0.25         | 0 → 0           | 0.00           | 0            |
| NOSEAL  | 7    | 31 → 10       | 0.32         | 9 → 3           | 0.33           | 4            |

G96a False · G96b False · G96c False → **VERDICT: NULL**

## Finding — the vibration seal is INERT; contamination is not a vibration channel
The decisive observation is that **SEAL and NOSEAL are byte-identical for both seeds** — the seal
changed nothing. Two mechanisms explain this and re-confirm earlier results:
1. `inject_tight` creates FROZEN vibrations (vel=0). `_reflect_at_sphere` reflects vibrations by their
   outbound radial VELOCITY; a frozen vibration never moves outward, so the seal never acts on it. The
   maintenance flux is positional, not ballistic — the vibration wall has nothing to reflect.
2. The contamination that does reach control (seed 7, ctrl=4, present WITH and WITHOUT the seal) cannot
   be a free-vibration channel — a vibration seal would have blocked it. It travels by the charge field
   / bridge graph, exactly the close-range coupling channel identified in G42. A vibration wall is the
   wrong tool for it.

Independently, the write is seed-unstable: seed 42 forms NO strong bridges (engram never consolidates),
seed 7 forms 9. This is intrinsic write variance, not a seal effect.

So contained maintenance via a vibration seal cannot give selective persistent memory: the isolation
tool is inert against the actual (charge/bridge) coupling, and the write itself is unreliable. Combined
with G94 (non-selective by count) and G95 (no exploitable topology), the bridge-memory persistence horn
is closed on every tool tried — culling, refractory, consolidation, maintenance, topology, and physical
sealing. The next valuable move is NOT a 10th memory variant but a different frontier (see LOGBOOK).
