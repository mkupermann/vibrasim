# R2 — Composition memory: does emergence-preserving composition escape the deadlock?

**Authored / FROZEN:** 2026-06-12 · **Status:** pre-registered, no run yet · **Phase:** redesign R2.
**Depends on:** R1 (eligibility store — see reframe below), G159 (H₀ partition), G160 (field flooding → flux sink).
**Design pressure-tested by:** the 2026-06-12 adversarial review (forced redesign of C1 & C3; this doc applies
every accepted fix). **Engine:** self-contained tool (no core-engine edits); reuses the G159 form_bridges veto.

## Reframe of R1 (record integrity — read first)

The R2 adversarial review established that R1's PASS does **not** break D4 (write=leak): `k_eligibility` is
incremented only on the firing atom's own index and never propagates — its non-leak is **hand-coded, not
emergent**. Reading it back is reading *around* the deadlock. R1 stands as a logged building block, but it is
**by-construction**; the redesign has not yet broken D4. R2 is the first test that could.

## The fix that makes it a real test

Replace R1's "store that cannot leak by fiat" with a store whose write is **allowed to propagate**, so that
non-propagation must EMERGE:

- New per-atom variable `v_stored` (managed in the tool; not `k_eligibility`).
- **Write rule (propagation-permitted, local):** when an atom fires, `v_stored[atom] += 1.0` AND for every live
  bond touching it, `v_stored[neighbour] += w_spread · b_strength`. Decays with `tau_store` (slow).
- Non-propagation A→B must then come ONLY from **C2** (A,B are separate bond-components ⇒ no bond path) and
  **C3** (the field that could carry it is absorbed) — never from a hand gate.

## The three constraints (all active simultaneously; field regime, NOT quiet)

- **C1 — write≠propagate store:** `v_stored`, spread-permitted (above).
- **C2 — bond containment (engineered topology, honest label):** constrained `form_bridges` (union-find, keep
  ≥M=2 components), applied EVERY tick (B-noise will try to bridge the cut; the veto must reject it continuously).
- **C3 — local flux sink (emergent):** each free vibration within `absorb_radius` of any atom with
  `k_charge ≥ absorb_charge_threshold` is killed with prob `lambda_absorb·dt`. Region defined by where charged
  atoms ARE (`k_charge`), no hand-placed boundary. **Knife-edge (pre-acknowledged):** the sink couples to the
  field that writes — the D4 trap resurfaces here.
- **Regime:** `neuron_dynamics_enabled=True`, `n_emit>0`, `lambda_gen>0` (do NOT fall back to the quiet
  `lambda_gen=0` regime — that externally disables D2 and makes the test vacuous).

## Phases (write and read SEPARATED)

`T_WRITE` (drive a subset of A) → `T_QUIET` (no drive, autonomous, field+sink active, ≈10 s ≈ 1.7·tau_store) →
`T_RECALL` (noise in B: random B atoms driven). Read at end of T_RECALL, gated on survival through T_QUIET.

## Markers (FROZEN 2026-06-12 — no post-hoc tuning; do NOT retune `lambda_absorb` after seeing M1/M2)

- **M1 — retention beyond passive decay (not the decay curve):** on the originally-stimulated A subset, end of
  T_RECALL: `cosine(v_stored[A_subset], stored_peak) ≥ 0.70` AND survival gate
  `cosine_observed ≥ 0.90 · cosine_baseline` (baseline = contained, no-field, no-noise decay over the identical
  T_QUIET+T_RECALL) AND `‖v_stored[A_subset]‖_end ≥ 0.50·‖·‖_peak`.
- **M2 — containment, gated:** (a) sanity gate `B fired ≥ 2` during T_RECALL (else "over-absorbed" →
  uninformative, NOT a containment PASS); (b) `‖v_stored[B]‖ / ‖v_stored[A_subset]‖ ≤ 0.30` AND
  `≤ mean_N3 + 3·SD_N3` (N3 null distribution; the 3·SD multiplier is frozen here).
- **M3 — mechanism-fired (all required):** M3a partition held ≥2 components at every tick AND =2 at end;
  M3b sink efficacy ≥ 0.90 (fraction of emitted free vibrations removed over T_RECALL, excluding bound);
  M3c A fired the pattern during T_WRITE AND B-noise produced no A-store increment.

## Control arms (pre-registered)

- **N1 — partition OFF** (bonds free), sink ON: expected M2 fails (bond+field merge). Normalizes M2.
- **N2 — partition ON, sink OFF** (`lambda_absorb=0`): isolates whether C3 is necessary. Prediction (G160 ARM C):
  M1 holds, M2 fails (field floods B). If N2 passes M2, C3 is scaffolding → cut it.
- **N3 — noise-only** (no write/A-drive), full containment: B-store null distribution under pure noise.
- **(calibration) BASE — contained, no field, no noise:** the passive-decay baseline for M1's survival gate.

## Bars

- **PASS** — M1 ∧ M2 ∧ M3 all true AND N1 fails as expected. Emergence-preserving composition escapes the
  deadlock class (first time). 
- **NULL (predicted, unanimous panel)** — any of M1/M2 false despite M3 true. Most likely: the D4 trap on the C3
  knife-edge (absorb in the charged region = A's write region ⇒ cannot block the B-flood without starving A's
  write). **Pre-registered conclusion if NULL:** emergence-preserving composition of the three validated breaks
  does NOT escape the deadlock — strong evidence the deadlock is inherent to this substrate class. Does NOT
  invalidate R1/G159/G160 individually.
- **FAIL** — M3 false (mechanism didn't fire): debug, re-run, do not touch bars.

## What R2 tests beyond R1

R1 (idealized, contained, no field) showed a *hand-coded* non-leaking trace persists — by construction. R2 tests
whether selective persistent retention survives **active autonomous dynamics** (live field D2 + competitive
B-noise) when non-propagation is forced to EMERGE from containment (C2+C3) rather than a hand gate, with write
and read separated by a quiet phase. The cosine is not the test; the survival-vs-baseline gate + the B-fired
sanity gate are. This is composition-under-pressure — no prior experiment addressed it.

## Reproducibility

Engine `world/` @ main; macOS-arm64, Python 3.13 (`uv run`); seeds {42,7,13}; field ON, lambda_gen>0; self-contained
tool `tools/redesign_r2_composition.py`; bars frozen pre-run; M3 mandatory; N1 must fail for a PASS; NULL stands.
