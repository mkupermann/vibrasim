# Proto-cell Programme Summary (G30 → G46)

Consolidated end-state of the structural thread pursued after the memory programme was closed
(see MEMORY_PROGRAMME_SUMMARY). Written 2026-06-02.

## Question
Can the substrate build a CELL PRECURSOR — a closed membrane that not only encloses but
REGULATES an interior environment — using only substrate primitives (no LLM), with the
membrane boundary engineered (CONCEPT §4.8) and its internals emergent?

## What was ACHIEVED (each a pre-registered PASS, seeds 42 & 7 unless noted)

1. **Large closed membrane forms (G30).** On the rich substrate (broad non-8% frequency band,
   membrane machinery) a single bridged ~110-atom shell composes (σ_r/R ≈ 0.25, encloses
   ~180–210 interior vibrations) and persists — BET-086's cell precursor at ~5–6× the scale.
2. **Selective permeability in the engine (G32).** The atom-proximity reflector (reflect
   incompatible free vibrations at the real shell atoms within r_2) seals the emergent membrane
   cleanly: compatible cross, incompatible contained (leak 0.000, gap +1.000). Reuses the
   substrate's own frequency-binding band as the gate.
3. **Maintained interior gradient — homeostasis (G43).** Under continuous ambient pressure the
   interior stays depleted of foreign species (interior/exterior incompatible ratio 0.00 with
   the channel, ≈1.0 without). A sustained gradient that is the channel's doing, not geometry.
4. **Active regulation to set-point (G44).** Perturb the interior with a foreign bolus (~100×
   set-point) and it RESTORES the depleted state (end/peak 0.03 with channel; 0.64 without):
   foreign leaks out, the channel blocks re-entry. The strong form of homeostasis.
5. **Interior chemistry exists (G45b).** ~16 bound atoms assemble inside the shell — the
   protected interior is a reaction chamber, not just a sealed bag.

## What it LACKS (honest boundaries — pre-registered NULLs)

- **Interior synthesis is NOT channel-gated, and there is NO channel-coupled metabolism
  (G45c, G49, G50).** Interior assembly is identical with channel ON/OFF AND with active uptake
  (G50: 16.0/16.9 atoms across uptake/plain/off, ratio 1.00). The ~16-atom interior chemistry is
  fixed by local geometry/binding, not driven by nutrient supply or the channel. The channel does
  environmental REGULATION; interior chemistry is an autonomous, saturated background process the
  membrane does not control. (Prevents overclaiming the channel as a metabolism enabler.)
- **No structural self-repair (G46, G47, G48).** A wounded shell does not heal (recovered ≡
  post-wound ≡ control), even with the substrate's wound-targeting mechanism (`edge_closure_k`,
  G47) or with valence commitment relaxed (`fusion_bond_block`=0, G48) — the component never
  regrows (peak ≡ post). **Cause (corrected by G48): positional rigidity + no wound-targeting**,
  NOT valence commitment. G48 refuted the G47 "persistence ⊥ repair" hypothesis: block=0 and
  block=2 behave identically (both persist 1.00, both heal 0.00), so persistence comes from the
  bridge network + curvature/repulsion (independent of fusion_bond_block), and the no-heal is
  because removed atoms leave a gap the rigid remaining shell does not migrate to close and
  untargeted new atoms do not bridge. The membrane is a rigid, stable structure, not a fluid
  self-renewing one. (Honesty note: G47 proposed a trade-off; the G48 confirmatory test
  falsified it — recorded as such.)

## Honest characterization
The substrate builds a **persistent, self-regulating, but non-self-renewing membrane
compartment**: forms → seals selectively → maintains an interior gradient → regulates back to
set-point after disturbance → hosts an autonomous interior chemistry. This is a genuine bottom-up
cell precursor with FUNCTION (homeostasis), distinct from a living cell in two named ways
(no channel-coupled metabolism, no self-repair). Built only from substrate primitives + one
engineered §4.8 boundary rule. No LLM, no transformer.

## Why this thread succeeded where memory did not
Memory needed a SELECTIVE WRITE, and write=broadcast=leak on every channel (the mapped deadlock).
The proto-cell needs only CONTAINMENT/EXCLUSION, which the reflective boundary robustly provides.
Lesson (docs/patterns): build functions on the substrate's genuine strength (containment), not on
a selective broadcast write it cannot do.

## Reusable mechanisms surfaced
- docs/patterns/atom_proximity_reflector.md — gate off the real structure, not a fitted proxy.
- docs/patterns/engineered_port_wall.md — specular reflection for robust activity containment.
- docs/patterns/protocell_homeostasis.md — emergent membrane + selective channel = regulated interior.

## Next directions (open, structural)
- Channel-COUPLED metabolism: make interior assembly depend on selective UPTAKE (a compatible
  "nutrient" the channel concentrates), so G45c becomes channel-gated.
- Self-repair: a wound-targeting rule (edge atoms with free valence attract new atoms) so the
  membrane re-closes — would turn G46 from NULL to a self-renewing membrane.
- Growth / division of the compartment.
