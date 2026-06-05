# JEP-248 — the EBM query mode: rank fact plausibility by ENERGY (not retrieval)

Pre-registered 2026-06-05 (BEFORE the run). The substrate is an ENERGY-based model; the canonical EBM query is to
score a configuration's PLAUSIBILITY by its energy (low = true). JEP-232..247 used the store via RETRIEVAL (clamp
key, relax value) and used energy as a stored-vs-untrained DETECTOR (237). This BET tests the distinct ENERGY-QUERY
mode: clamp a full candidate fact `concat(X_code, Y_code)` and read its energy — do TRUE facts score lower than FALSE
ones? And does it generalize to transitive (unstored) edges, or only direct ones (the JEP-245 memory boundary)?

## Method (no transformer)
- JEP-232 store, is-a chain c0→…→cn, all DIRECT edges stored. For a candidate (X,Y), energy-query = `net.energy(
  concat(code[X], code[Y]))` (lower = more plausible). Three sets:
  - DIRECT-TRUE: stored edges (ci, ci+1).
  - FALSE: random non-edge pairs (Y not an ancestor of X).
  - TRANSITIVE-TRUE: (ci, cj) with j>i+1 (derivable by closure, NOT stored as a pattern).
- Score separation by AUC (does energy rank DIRECT-TRUE below FALSE?) and check where TRANSITIVE-TRUE energies fall.
  Seeds 42 & 7, K=12 edges.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J248a | Energy separates DIRECT-true from false | AUC(direct-true lower-energy than false) ≥ 0.90 (both seeds) |
| J248b | A threshold classifies direct facts | a single energy cut gives ≥ 0.85 accuracy on {direct-true vs false} (both seeds) |
| J248c | Transitive edges are NOT low-energy (memory boundary) | mean energy(transitive-true) ≥ mean energy(direct-true) + 0.5·(mean false − mean direct-true) — i.e. transitive sits with the FALSE/non-stored side, not the true side (both seeds) |
| J248d | Consistent with retrieval | every fact the energy-query calls true (below the cut) is a direct stored edge (no false-positive transitive), both seeds |

PASS = J248a–c → the substrate supports an EBM energy-query for DIRECT fact plausibility, and (J248c) it does NOT
generalize to transitive edges (only chaining does) — the EBM-query mode is single-shot direct-fact scoring,
reaffirming the JEP-245 memory boundary from the energy side. NULL/finding: if J248c fails (transitive ALSO low
energy), the EBM generalizes beyond stored facts — a positive surprise (record as such). No post-hoc tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J248a/b PASS — a stored edge `concat(X,Y)` IS a trained attractor (deep minimum ~−90, JEP-237 probe), a false
pair is not (shallow ~−40), so energy cleanly separates them (AUC ~1.0, a clean cut). J248c PASS — a transitive pair
(ci,cj), j>i+1, was NEVER stored as a pattern, so its full-pattern energy is shallow (like a false pair) → energy-
query does NOT see it as true; only the CHAIN (iterated retrieval) derives it. J248d PASS (the cut admits only direct
stored edges). NET: the EBM energy-query is a fast single-shot DIRECT-fact plausibility scorer; transitive inference
still requires chaining — the JEP-245 memory boundary, confirmed from the energy side. RISK: a transitive pair that
happens to share code structure could dip in energy — random codes make this unlikely; check the transitive energy
distribution. Established (EBM energy-as-plausibility, Hopfield energy landscape), named; no novelty — the value is
characterizing the substrate's native EBM query mode and its (non-)generalization.

## RESULT (2026-06-05): PASS — energy cleanly scores DIRECT facts; transitive sits with the false set (memory boundary)

| seed | AUC (direct<false) | acc | mean E: direct / false / transitive | cut |
|------|--------------------|-----|-------------------------------------|-----|
| 42 | 1.00 | 1.00 | −89.6 / −39.4 / −44.0 | −64.5 |
| 7  | 1.00 | 1.00 | −89.1 / −39.4 / −45.1 | −64.2 |

- **J248a/b ✓** — a single energy evaluation of `concat(X,Y)` separates true DIRECT edges (deep minima ~−89) from
  false pairs (~−39) at **AUC 1.00 / accuracy 1.00**: the substrate is a native EBM fact-plausibility scorer.
- **J248c ✓** — TRANSITIVE (derivable-but-unstored) edges score ~−44, on the FALSE/non-stored side (not the −89 true
  side): the energy-query does NOT see them as plausible.
- **J248d ✓** — the cut admits ONLY direct stored edges (no transitive false-positives).

**FINDING:** the substrate supports a single-shot EBM ENERGY-QUERY (energy-as-plausibility) that perfectly scores
DIRECT fact plausibility — a query mode distinct from retrieval/chaining, native to the energy-based model. It does
NOT generalize to TRANSITIVE facts (those have high energy, never stored as patterns) — only iterated retrieval
(chaining) derives them. This confirms the JEP-245 memory boundary FROM THE ENERGY SIDE: the substrate stores DIRECT
facts as low-energy attractors (single-shot scorable) and derives transitive ones by chaining (deduction), but does
not generalize to unstated edges. So the substrate offers TWO complementary native query modes — single-shot
energy-scoring for direct facts, iterated relaxation for transitive closure — both established (EBM energy landscape,
Hopfield), named; no novelty. Verdict: **PASS** (predict-calibrate HIT — AUC 1.00, transitive-on-false-side, all as
forecast). This rounds out the substrate-relational arc's characterization: the energy substrate is a relational EBM
with direct-fact energy-scoring + deductive chaining, bounded by the ~20-edge/module capacity and the memory boundary.
