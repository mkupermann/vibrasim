# G171 — association as a bandwidth law: contact points k as the variable

**Status: DRAFT — bars must be committed before any data (D2).**

## 1. The one question (D1)

> Can a deliberately written CROSS-STRUCTURE between two register groups —
> k frozen cross-bond rest lengths, the only inter-register channel this
> substrate permits — reconstruct the partner group's 6-bit content after
> that group's own bonds are removed, and does reconstruction scale with k
> as the valence budget predicts (researcher A's bandwidth law)?

**One-sentence material difference from G154/G161 (researcher C's
condition):** those runs sought recall on stores with no attractor property;
G171 runs on a certified persistent-content substrate (G163–G170) with the
inter-register write channel named, controlled (allocation-order trap
documented) and PARAMETRIZED — the question is no longer "does association
happen" but "how much association fits through k contacts".

## 2. Protocol

Register group A (the cue) and group B (the target) each hold 6 bits,
distributed over m chains per group; bits per chain = 6/m. Free ends per
chain = 2; interiors saturated. **k = 2m cross-contacts** (end-to-end
cross-bonds A_i↔B_i, written under the trap mitigation: strict sequential
allocate-then-consolidate per chain, cross-bonds written last as their own
consolidation phase, full census verification of the intended graph — any
deviation = run INVALID).

Arms: **k=2** (m=1: 6-bit chains), **k=6** (m=3: 2-bit chains),
**k=12** (m=6: 1-bit chains, every carrier an end).

Association test per run: write A, B, cross-structure (census-verified) →
scramble B to uniform AND DELETE all of B's intra-bonds (its own memory is
gone; only the cross-structure and A remain) → pin A's carriers at written
positions → relax 800 quiet ticks → decode B (spacing rule; for m>1 chains
independently) → accuracy vs B's written pattern.

- **SENS-A (researcher C's association sensitivity gate):** the k=12 arm
  doubles as it — with every B-carrier individually cross-anchored, the
  metric MUST demonstrably indicate association (≥ 0.90); if even k=12
  fails, the metric/geometry cannot show association → **INCONCLUSIVE**,
  no class-level conclusion.
- **NEG:** cross-bonds also deleted (B fully unconstrained) → must decode
  at chance (≤ 0.6, < 0.90).
- **SCRAM-X control:** cross-structure written from a DIFFERENT (random)
  B-pattern than decoded against → must be ≤ 0.6 (the cross-structure
  carries THIS pattern, not generic geometry).

8 pattern-pairs × seeds {42, 7, 13} per arm. All standard gates (boundary,
censuses, order-effect metric under the mitigation).

## 3. Pre-registered bars (fixed before any data; D3)

Per-arm accuracy on B's 6 bits (total-bit metric per seed).

- **BANDWIDTH-LAW CONFIRMED:** monotone scaling k=2 < k=6 < k=12 with
  k=12 ≥ 0.90 AND k=2 ≤ 0.75 (the channel, not search, is the limit) on
  ≥ 2/3 seeds, controls clean.
- **ASSOCIATION-FLAT (the honest NULL):** k=12 ≥ 0.90 (gate fires) but NO
  monotone scaling below it — association exists only as full anchoring,
  no graded channel.
- **CLASS-NULL:** accuracy ≈ chance at ALL k INCLUDING k=12 with controls
  clean — researcher C's abort clause MAY then fire (programme decision to
  close the association class), and only then.
- **INCONCLUSIVE:** k=12 < 0.90 while NEG/SCRAM-X behave (metric cannot
  show association here), or any census/boundary gate broken.
- **FAIL:** NEG or SCRAM-X ≥ 0.75 (readout artifact / generic-geometry
  leak), or write censuses invalid.

## 4. Predictions (calibration, before data)

**Derived quantitative curve (sceptic D's condition — from constraint
geometry, not tuning):** unbonded B-interiors stay at scrambled uniform
positions; only spacings adjacent to a cross-anchored carrier are
informative. Working the decode rule through each fragmentation:
- k=2 (m=1): 4 interior spacings decode uniform→0 (50% each); the two
  edge spacings carry only weak aggregate information → **acc ≈ 0.54**.
- k=6 (m=3): per 2-bit chain the first spacing is uniform (50%), the second
  is the anchored-end sum minus uniform — correct in 3 of 4 bit patterns
  (75%) → **acc ≈ 0.63**.
- k=12 (m=6): both carriers of every bit anchored at written positions →
  **acc ≈ 0.95+** (relaxation noise only).
Secondary sub-verdict **QUANT-MATCH:** each arm within ±0.10 of this curve
(reported CONFIRMED/OPEN; does not gate the primary verdict).

**Exposure declaration (sceptic D's objection, recorded):** after the curve
above was derived and written, a TECHNIQUE smoke (one pattern-pair, seed 42,
D8: harness verification only) produced arm accuracies 0.5 / 0.5 / 1.0 and
clean censuses. Those numbers were quoted in a bars-approval request — a
chair mistake, since it previews the outcome; the exposure is hereby part of
the record. Sequence of writing (curve → smoke → this declaration) is
attested by the session log; the primary bars predate both. The registered
run (24 pairs × 3 seeds × 5 arms) retains its evidential status; the smoke's
single pair does not certify anything and is archived as technique data.

- Researcher A's law (registered, now quantified above): success requires
  k ≳ bits-to-complete; at k=2 the failure is FROM BANDWIDTH.
- Chair: BANDWIDTH-LAW CONFIRMED 45%, ASSOCIATION-FLAT 20%,
  INCONCLUSIVE 20%, FAIL 10%, CLASS-NULL 5%.
- Most-likely failure mode: INCONCLUSIVE via k=12 retrieve dynamics — 12
  cross-bonds + pinned A may frustrate B's relaxation (competing
  constraints), keeping k=12 under 0.90 for dynamical, not informational,
  reasons.

## 5. Budget

Harness (groups, fragmentation, cross-write phase, B-bond deletion):
~1 h. Compute: 3 arms × 24 runs + controls ≈ 30 min. Verdict + LOGBOOK +
FRONTIER (D10): 30 min. **Realistic 2.5 h → hard cap 5 h.**

## 6. Out of scope

Retention of associations over idle, bidirectional recall (B→A), m > 6,
kinematics dossier, any claim about G154/G161-style same-register
completion (different question, stays closed).
