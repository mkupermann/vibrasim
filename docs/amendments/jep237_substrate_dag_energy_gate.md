# JEP-237 — close the DAG retrieval: detect trained edges by key→value BINDING ENERGY

Pre-registered 2026-06-05 (BEFORE the run). JEP-236 showed slot-binding STORES multiple parents but a value-overlap
threshold cannot tell a trained slot from an empty one (the value slot always relaxes to a stored attractor → every
empty slot injects a false parent). The diagnosis (JEP-236 calibration, error-class 3): detect whether the (key,
value) PAIR is a stored attractor via its settled ENERGY, not the value's cleanliness. A pre-run probe confirmed a
clean, large gap: trained edges settle at energy ≈ −89…−93, spurious slots at ≈ −22…−47.

## Method (no transformer; same JEP-236 slot-binding + an ENERGY GATE)
- Identical store to JEP-236 (each edge `child ⊙ slot_i → parent_i`).
- At store time, record the energies of the explicitly STORED training patterns → `E_med = median`.
- ACCEPT a slot retrieval iff its settled energy ≤ `0.7 × E_med` (a deep attractor = a trained edge). The factor and
  the reference are derived from the TRAINING patterns only — NOT from the spurious-slot energies (no post-hoc peek).
- DAG is_a = BFS over energy-gated multi-parent retrieval. MAXDEG = 3. Multi-parent taxonomy from prose. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J237a | Multi-parent recovered, no phantoms | a 2-parent node returns EXACTLY its parents; a 1-parent node returns EXACTLY one (both seeds) |
| J237b | DAG transitive closure matches symbolic | gated substrate DAG is_a vs symbolic ≥ 0.90 (both seeds) — closes JEP-236's 0.64–0.68 |
| J237c | Above an untrained control | untrained net: match ≤ 0.60 (both seeds) |
| J237d | Gate separates cleanly | every trained edge accepted AND every empty slot rejected (0 false-accept / 0 false-reject, both seeds) |

PASS = J237a–d → the energy gate closes the DAG boundary: the substrate holds the engine's multi-parent taxonomy and
reasons over it correctly. NULL (honest): J237b/d fail → the gap is run-dependent and the fixed 0.7×median doesn't
generalize across seeds/topologies (then the gate needs a per-node relative rule). No post-hoc threshold tuning —
the 0.7×median rule is locked here.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J237d PASS — the probe showed a wide gap (trained ≤ −89, spurious ≥ −47); 0.7 × E_med (E_med ≈ −90 → cut ≈ −63)
sits squarely in the gap, accepting all trained (≤ −89) and rejecting all spurious (≥ −47), 0 errors. Hence J237a
PASS (clean parent sets), J237b PASS (≥ 0.90, ~1.00 — the closure now matches symbolic), J237c control fails.
RISK: a 3-parent node fills all slots (no spurious to reject — fine) and deeper/denser taxonomies could shrink the
gap; if a spurious slot ever settles near −63 the fixed cut would misfire (then a per-node gap-cut is the fallback,
noted for JEP-238 if needed). This is the energy-gated completion of JEP-236; established (Hopfield energy as a
stored-vs-spurious detector), named; no novelty — it closes the J235d/J236 boundary so the substrate holds the
engine's ACTUAL DAG taxonomy and reasons over it.

## RESULT (2026-06-05): PASS — all 4 bars; the energy gate closes the DAG boundary cleanly

| seed | poodle parents | cat parents | DAG match | control | gate cut (median) | false-accept / reject |
|------|----------------|-------------|-----------|---------|-------------------|------------------------|
| 42 | dog, pet | pet | 1.00 | 0.50 | −63.7 (−90.9) | 0 / 0 |
| 7  | dog, pet | pet | 1.00 | 0.50 | −63.2 (−90.3) | 0 / 0 |

- **J237a ✓** — exact parent sets: `poodle → {dog, pet}`, `cat → {pet}` — no phantom parents.
- **J237b ✓** — gated substrate DAG is_a matches the symbolic closure **1.00** (was 0.64–0.68 in JEP-236), both seeds.
- **J237c ✓** — untrained control 0.50.
- **J237d ✓** — the gate makes **0 false-accepts and 0 false-rejects**: every trained edge accepted, every empty slot
  rejected. The cut (0.7 × median ≈ −63) lands squarely in the trained(−90)/spurious(−47) gap, exactly as the
  pre-run probe forecast.

**FINDING:** the DAG boundary (JEP-235d / JEP-236) is closed. The detector that works is the **key→value BINDING
ENERGY**, not value cleanliness — in an attractor net the value is always clean, but only a TRAINED (key,value) pair
is a DEEP minimum. With the gate, the substrate holds the Understanding Engine's ACTUAL multi-parent DAG taxonomy
(`parents: dict[str, set]`) and reproduces its transitive closure through energy relaxation. The relational-substrate
arc is now complete for both trees AND DAGs (within the ~20-edge capacity). Established (slot-binding + Hopfield
energy as a stored-vs-spurious detector + BFS closure), named; no novelty — the value is closing the boundary
end-to-end. Verdict: **PASS** (predict-calibrate HIT — gate-separation, clean sets, and 1.00 closure all as
forecast). Methodological win: a NULL (236) diagnosed into a checkable mechanism (energy discriminates) that the
next rung confirmed — the predict-calibrate loop working as intended.
