# Pattern: the rest-length register (PRIM14)

## Source
PRIM14-D2 PASS · G163 PASS · G164 PASS (clean) · traps from D1 (NULL) and
G162 (FAIL). Summary: docs/REGISTER_PROGRAMME_SUMMARY.md.

## Design rules (all load-bearing, all learned the hard way)

1. **Encode in rest lengths, not occupancy.** Bits = per-bond rest lengths
   (bit 0 = 6.5, bit 1 = 10.5 at r_2 = 12). Occupancy registers make PRIM14
   orthogonal (G161: stored spacing = global equilibrium → no effect).
2. **Respect the measured formation window.** Bonds form below distance 12
   (sharp cutoff at r_2). Every non-consecutive pairwise distance must exceed
   it — SHORT+SHORT ≥ 12 — or skip bonds rewrite the register graph at write
   time (G162 FAIL).
3. **Close the write channel during ANY read-out** (valence saturation or a
   formation freeze) and VERIFY it by bond census pre/post. Formation-frozen
   rest lengths store whatever geometry is held during measurement
   (measurement-write coupling, D1).
4. **Scramble to the encoding midpoint** (8.5) — maximum ignorance, inside
   the attractor basin (2 units per bond). Far displacement leaves the basin
   (G161: displace-14 → nothing funnels back).
5. **Retrieval needs one position anchor** (pin carrier 0); a free-boundary
   chain then settles every bond at its own rest length.
6. **Verify agitation is real** when claiming retention: perturbation floor
   (RMS ≥ pre-registered threshold vs the quiet baseline), and know that
   `node_thermal_speed` is allocation-time only — ongoing agitation must be
   injected as velocity kicks (G164 erratum).
7. **Gates that made the claims defensible:** attribution arm (global r_eq at
   identical dynamics must decode at chance), no-bond arm, write census,
   rebonding count = 0, total-bit accuracy metric (threshold granularity).

## Scope honesty
Engineered write; single-anchor retrieval; 6 bits demonstrated; legacy
substrate only (Flux lacks node kinematics / mechanical bonds). Association
from partial cues is NOT this pattern and remains closed (G154, G161).
