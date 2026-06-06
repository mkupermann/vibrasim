# Pattern — Atom-proximity reflector (gate off the real structure, not a fitted proxy)

**Problem.** You want a boundary rule at an emergent structure (e.g. a membrane shell):
let some things through, turn others back. The obvious implementation fits a smooth
primitive to the structure (least-squares sphere → radius R) and reflects at that surface.

**Why the proxy leaks.** Emergent structures are thick and dynamic. The G30 shell has
σ_r/R ≈ 0.27 — atoms span r ≈ 8–14 around a mean R ≈ 11 — and the fitted R drifts
tick-to-tick as the shell breathes. A single-radius reflector sits at the mean while the
metric/interior boundary sits elsewhere; probes register past the boundary in the annulus
between the two before they are ever reflected. G31 leaked 35 % of incompatible probes
this way despite being strongly selective (gap +0.65).

**Fix.** Reflect off the **actual constituent elements**, not the fitted proxy. Cache the
element *membership* on a slow cadence (the expensive BFS for the largest bridged
component), but read the elements' *current positions* every tick. A test particle is
acted on when it comes within the substrate's own interaction range (`r_2`) of ANY real
element — this automatically covers the full, irregular, breathing thickness. The outer
elements sit beyond the mean radius, so particles are turned back before reaching the
interior. G32 sealed the same shell to leak 0.000 (gap +1.000) with no other change.

**Recipe.**
1. Cache element indices + a stable centre on a recompute cadence; read live positions each tick.
2. Per particle, nearest-element min-image distance < interaction range → "at the boundary".
3. Gate the action with the substrate's OWN compatibility predicate (here the frequency
   binding band relative to the element-set mean) — don't invent a new selectivity test.
4. Only act on inbound particles (radial velocity toward the centre < 0); mirror velocity
   about the outward radial normal and revert position. Move only free particles, never
   the bound elements — keeps the structure stable (verify with a survives-the-rule bar).

**Cost.** O(particles × elements) min-image distances per tick; fine for ~10³ × ~10²
in numpy. Recompute membership infrequently; positions are cheap.

**Where it applies.** Any "gate at an emergent boundary" rule — selective permeability,
adsorption, capture, containment — where the boundary is a real, irregular, moving set of
elements rather than an analytic surface. Established in G31 (NULL, fitted sphere) → G32
(PASS, atom proximity); see docs/amendments/g31_*, g32_*.
