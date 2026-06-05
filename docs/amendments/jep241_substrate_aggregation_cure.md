# JEP-241 — does REDUNDANT AGGREGATION cure substrate multi-hop compounding where cleanup failed?

Pre-registered 2026-06-05 (BEFORE the run). JEP-240 (NULL) showed compounding is real under cue noise and per-hop
attractor CLEANUP is NOT a reliable cure (it can lock in discrete decode errors). The universal insight
(JEP-137/138/140/158) says the robust cure is REDUNDANCY / AGGREGATION. This BET tests that cure natively in the
substrate, completing the conceptual arc: compounding-real → cleanup-fails → AGGREGATION-cures.

## Method (no transformer; per-hop majority-vote aggregation)
- JEP-232 store, is-a chain, KEY-cue bit-flip noise fraction `f` (the JEP-240 regime). At each hop, perform R
  INDEPENDENT noisy retrievals (different random flip masks) and MAJORITY-VOTE the decoded parent; re-clamp the
  voted clean code. Compare to single-path (R=1) raw/cleanup from JEP-240.
- k-hop recall vs depth for R ∈ {1, 3, 7} at a fixed `f` giving single-retrieval single-hop ≈ 0.6–0.85 (so there is
  compounding to cure). Seeds 42 & 7, K=12 facts.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J241a | Aggregation lifts single-hop | R=7 single-hop recall > R=1 single-hop by ≥ 0.10 (both seeds) |
| J241b | Aggregation cures multi-hop | R=7 4-hop recall ≥ 0.70 (both seeds) — vs the ~0.1–0.3 single-path floor of JEP-240 |
| J241c | Monotone in redundancy | 4-hop recall R=7 > R=3 > R=1 (both seeds) — more independent paths, more cure |
| J241d | Aggregation beats cleanup | R=7 4-hop recall > single-path CLEANUP 4-hop recall by ≥ 0.20 (both seeds) |

PASS = J241a–d → redundant aggregation is the robust substrate cure for multi-hop compounding, completing the
universal compounding/aggregation picture natively in the energy substrate. NULL (honest): J241b fails → even
aggregation can't cure at this noise (the per-hop errors are not independent enough, or the chain is too long);
J241c fails → no monotone benefit (a confound). No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS. The R retrievals use INDEPENDENT flip masks, so per-hop majority-vote drives the single-hop error from e
down to ~Binomial-tail(>R/2 wrong) ≪ e — a sharp drop (J241a). That higher per-hop accuracy compounds far more
gently, so R=7 4-hop clears 0.70 (J241b) and recall is monotone in R (J241c). Aggregation beats single-path cleanup
by a wide margin (J241d) because cleanup only de-drifts ONE noisy read while voting suppresses the decode error
itself. This is the substrate-native confirmation of the universal insight (aggregation is the regime-independent
cure, JEP-138/140), now closing the arc the JEP-240 NULL opened. RISK (in-rung): if the noise `f` is so high that a
majority of the R reads are individually wrong (single-hop < 0.5), voting reinforces the wrong answer — keep
single-retrieval single-hop ≳ 0.6 so the vote concentrates on the truth. Established (ensemble/majority voting,
Condorcet, error-correcting redundancy), named; no novelty — the value is closing the conceptual arc in the substrate.

## RESULT (2026-06-05): PASS — all 4 bars; aggregation is the robust substrate cure (closes the JEP-240 arc)

| seed | f | single-hop R1 → R7 | 4-hop R1 / R3 / R7 | single-path cleanup 4-hop |
|------|---|--------------------|--------------------|---------------------------|
| 42 | 0.25 | 0.67 → 1.00 | 0.00 / 0.56 / 1.00 | 0.00 |
| 7  | 0.25 | 0.67 → 1.00 | 0.33 / 0.44 / 1.00 | 0.33 |

- **J241a ✓** — R=7 majority-vote lifts single-hop 0.67 → 1.00 (+0.33): independent-mask voting suppresses the
  per-hop decode error.
- **J241b ✓** — R=7 4-hop recall = **1.00** both seeds (vs the 0.00–0.33 single-path floor of JEP-240): aggregation
  CURES the compounding.
- **J241c ✓** — monotone in redundancy: 4-hop R7 (1.00) > R3 (0.56/0.44) > R1 (0.00/0.33) — more independent paths,
  more cure.
- **J241d ✓** — R=7 4-hop beats single-path CLEANUP 4-hop by ≥ 0.67 (1.00 vs 0.00/0.33): voting suppresses the decode
  ERROR itself, where cleanup only de-drifts one noisy read (and can lock errors in, JEP-240).

**FINDING — the substrate-relational arc's conceptual capstone:** the programme's UNIVERSAL compounding/aggregation
insight (JEP-137/138/140/158) holds NATIVELY in the energy substrate. Within the substrate relational store:
compounding is real (J240b), per-hop CLEANUP is not a reliable cure (JEP-240 NULL — it can lock in discrete errors),
and REDUNDANT AGGREGATION (independent noisy retrievals + majority vote) IS the regime-independent cure (J241, 4-hop
1.00). The 240→241 pair is the discipline working: a NULL diagnosed the cure, the next rung confirmed it. Established
(ensemble/majority voting, Condorcet, error-correcting redundancy), named; no novelty — the value is closing the arc
in the substrate. Verdict: **PASS** (predict-calibrate HIT — all 4 bars as forecast). With JEP-232..240, the
substrate carries the engine's relational MEMORY + INFERENCE (store/chain/type/DAG/interaction/online) AND inherits
the programme's core robustness lesson: aggregation, not cleanup, is the cure for multi-hop compounding under noise.
