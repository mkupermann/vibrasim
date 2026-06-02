# Pattern — Proto-cell homeostasis (emergent membrane + selective channel = regulated interior)

**What it is.** A spontaneously-formed closed membrane (G30) plus the atom-proximity selective
channel (G32) constitutes a proto-cell that maintains AND regulates an interior environment
chemically distinct from the exterior — the defining function of a cell membrane, built only
from substrate primitives + one engineered §4.8 boundary rule.

**The construction.**
1. Rich substrate (G27): broad frequency band (freq_ratio 0.05, tol 0.045), membrane machinery
   (atom_valence=3, fusion_bond_block=2, curvature_k, atom_repulsion_k). A ~110-atom closed
   shell forms (largest bridged component → sphere fit gives centre C, radius R).
2. Selective channel (G32): `membrane_channel_mode='atom'` reflects INCOMPATIBLE free
   vibrations (substrate binding band vs the shell's mean frequency f_mem) at the real atoms,
   tracking the breathing shell. Compatible species pass; foreign species are excluded.

**What it delivers (verified, both seeds).**
- **Homeostasis (G43):** under continuous ambient pressure the interior (r<0.6R) stays
  depleted of foreign species — interior/exterior incompatible concentration ratio 0.00 with
  the channel, ≈1.0 without. A sustained gradient that is the channel's doing, not geometry.
- **Regulation (G44):** perturb the interior with a foreign bolus (~100× the set-point) and it
  RETURNS to depleted (end/peak 0.03 with channel; 0.64 without). Foreign species leak out
  (outbound is unreflected) and the channel blocks re-entry, so the interior self-clears back
  to its set-point. The strong form of homeostasis.

**Why it works where memory did not.** This uses the channel for EXCLUSION (keep foreign out /
let it leak), which the reflective boundary robustly does, and it needs no selective WRITE —
sidestepping the write=broadcast=leak deadlock that defeated the memory programme. Containment
is the substrate's genuine strength; build functions that need containment, not ones that need
a selective broadcast write.

**Honest scope.** Demonstrated for an EXCLUSION gradient (interior kept clear of foreign
species). Not yet shown: distinct interior CHEMISTRY assembling inside (interior molecular
species different from exterior), growth, or division — the next structural steps. The
membrane is engineered-boundary + emergent-internals per the charter; the channel is an added
§4.8 rule, not a pre-existing property.

**Where it applies.** Any "maintain/regulate an interior environment" function: gradient
maintenance, selective uptake/exclusion, homeostatic set-points. See docs/amendments/g30, g32,
g43, g44.
