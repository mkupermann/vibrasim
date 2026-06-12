# R3 — Composition memory under ACTIVE recall (FINAL iteration of the composition question)

**Authored / FROZEN:** 2026-06-12 · **Status:** pre-registered, not yet run.
**STOPPING RULE (pre-registered, binding as the markers):** this is the **final** iteration of the composition
question. If R3 is NULL or inconclusive, we STOP and conclude that the triple-constraint emergence-preserving
composition does not cleanly support selective memory. **No R4, no further tweak.**

## Why R3 (and why it is not fishing)

R2 returned NULL by the frozen bar, but the NULL was driven by an invalid instrument, not by demonstrated
leakage (see LOGBOOK 2026-06-12). Two setup flaws, both fixed here — and both fixes make the test **harder**, the
hallmark of an honest correction, not a relaxation:

1. **Marker (b) was mathematically incapable of distinguishing A-leak from the B-noise we deliberately inject**
   (`‖vB‖/‖vA‖` compares B's own noise-store to A's store). Dropped. Containment is now measured ONLY against
   B's own noise null (the N3 metric, which already passed in R2): A's activity must not raise B above what B's
   own noise produces.
2. **A was quiescent during recall** (the sink killed A's field-firing), so containment was never stressed — a
   dam tested with no water behind it. Fixed: **A is driven continuously through the recall window** = a genuine,
   sustained active leak source. This is strictly harder for containment.

Store continuity: R3 uses R2's corrected **emergent** store — `v_stored`, written by an atom's own firing AND
spread along live bonds (propagation-permitted), so A→B non-leak must EMERGE from C2 (H₀ partition) + C3 (local
flux-sink), never from a hand gate. NOT a token deposit.

## Protocol (corrected)

Modules A = {10,16,22}, B = {34,40,46}; 22↔34 < r_2 (bottleneck candidate); field reaches (G160). Field active via
emission (`n_emit=8`, `lambda_gen=0`). C2 = constrained `form_bridges` (M=2, union-find, every tick). C3 = local
flux-sink (absorb free vibrations near any alive atom; emergent, no hand-placed boundary; ≥90% efficacy required).

- **WRITE** (`T_WRITE`): drive module A strongly → establish the `v_stored` pattern (`peak = v_stored[A]`).
- **ACTIVE recall** (`T_ACTIVE`): A driven continuously (sustained leak source) AND module B receives random-atom
  noise. Flux sinks + partition operate throughout. Read at end.
- **READ:** `cosine(v_stored[A], peak)`; `‖v_stored[B]‖` vs B's own noise null (N3).

## Frozen markers (write before any code — no post-hoc tuning)

- **M1 (retention):** `cosine(v_stored[A]_end, peak) ≥ 0.70`.
- **M2 (containment, corrected — sole metric):** `‖v_stored[B]‖_MAIN ≤ mean_N3 + 2·SD_N3`, where N3 = the
  noise-only arm (B noise, no A drive). B must be statistically indistinguishable from its own noise null. The
  2·SD multiplier is frozen here.
- **M3 (mechanism-fired, all required):** M3a partition ≥2 components every tick; M3b flux-sink efficacy ≥0.90
  over T_ACTIVE; M3c **A actively driven throughout** (A firing count during T_ACTIVE > 0).

## Negative control (required for a PASS)

**N1 — H₀ partition OFF** (M=1, bonds free), all else identical: A's firing spreads `v_stored` to B via the bond
AND A's field reaches B → expected `‖vB‖_N1 > mean_N3 + 2·SD_N3` (M2 fails). Establishes the test is sensitive.

## Bars and pre-committed interpretation

- **PASS** — M1 ∧ M2 ∧ M3 all true AND N1 fails M2. The triple-constraint emergence-preserving composition
  supports selective memory under active internal dynamics. Deadlock broken on this minimal task.
- **NULL** — M2 false despite M3 true (A's active field raises B above its own noise → leak), OR M1 false.
  **Pre-committed conclusion:** under emergence-preserving rules, the three channel constraints (propagation-
  permitted write, H₀ bond partition, active local flux-sink) do NOT compose to support a minimal selective
  memory; the deadlock is likely inherent to this class of self-assembling substrates. We STOP and write this.
- **Inconclusive** — M3 fails (mechanism/setup error): fix the mechanism, re-run once WITHOUT changing bars; if
  still inconclusive, treated as NULL for the stopping rule.

R1/G159/G160 are unaffected by any R3 outcome (different scopes).

## Reproducibility

Engine `world/` @ main; macOS-arm64, Python 3.13 (`uv run`); seeds {42,7,13}; field ON via emission, lambda_gen=0;
self-contained tool `tools/redesign_r3_composition.py`; bars + stopping rule frozen pre-run; NULL stands.
