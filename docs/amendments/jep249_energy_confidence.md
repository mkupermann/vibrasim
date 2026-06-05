# JEP-249 — energy as graded CONFIDENCE: does fact support modulate energy? (a benefit beyond binary symbolic)

Pre-registered 2026-06-05 (BEFORE the run). JEP-248 used energy to score DIRECT-fact plausibility (binary: deep
attractor vs shallow). This BET asks whether energy is GRADED by SUPPORT — does restating a fact more often (more
sources / more evidence) deepen its attractor (lower energy), giving a CALIBRATED CONFIDENCE the binary symbolic
engine lacks? Connects the EBM energy landscape to the redundancy/aggregation theme (more support → stronger).

## Method (no transformer)
- JEP-232 store. Build a fact set where edges have VARYING support: edge i is restated `s_i` times in the training
  pattern list (s_i ∈ {1, 2, 3, 5, 8}). Train (contrastive-Hebbian; a repeated pattern gets more updates/epoch).
- Measure each edge's energy `net.energy(concat(X,Y))`. Test whether energy DECREASES monotonically with support s_i.
  All edges remain recalled (support is about CONFIDENCE, not correctness). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J249a | Support lowers energy (graded confidence) | Spearman(support, −energy) ≥ 0.80 (more support → lower energy), both seeds |
| J249b | Distinguishable extremes | mean energy(s=8) < mean energy(s=1) by a clear margin (≥ 10% of the s=1 magnitude), both seeds |
| J249c | All facts still TRUE | every edge (any support) is still recalled correctly (support modulates confidence, not correctness), both seeds |
| J249d | Monotone, not noise | energy is non-increasing across the support levels {1,2,3,5,8} at the group-mean level (allowing one inversion), both seeds |

PASS = J249a–c → the substrate gives GRADED confidence: a fact's energy encodes how well-supported it is, a
calibrated signal the binary symbolic engine lacks. NULL/finding: if J249a fails (no monotone relation), repetition
does not modulate attractor depth here (energy is ~binary stored/not) — then confidence is not free from frequency.
No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J249a/b/d PASS — a pattern repeated s times receives ~s× the contrastive-Hebbian weight updates per epoch, so its
attractor basin DEEPENS with s → energy decreases monotonically with support (Spearman ≥ 0.8). J249c PASS — even
s=1 is within capacity (few facts), so all are recalled; support only deepens, never breaks, the attractor. NET: the
substrate provides graded, frequency-calibrated confidence (more sources/restatements → lower energy → higher
confidence) — a genuine capability beyond the binary symbolic engine, and the EBM-native form of the redundancy
principle. RISK (in-rung): contrastive-Hebbian normalizes W (symmetrize + zero-diagonal) each step, which could CAP
the depth gain so s=5 vs s=8 saturate — if the top levels flatten, J249a still holds (monotone over the range) but
note the saturation. Established (Hebbian frequency effects, EBM energy = log-plausibility, confidence calibration),
named; no novelty — the value is showing the substrate's graded-confidence capability and tying it to redundancy.

## RESULT (2026-06-05): PASS — energy is GRADED by support; the substrate gives calibrated confidence (beyond binary symbolic)

| seed | support 1→8 | energy (s=1,2,3,5,8) | Spearman(support,−E) | margin s1→s8 | inversions |
|------|-------------|----------------------|----------------------|--------------|------------|
| 42 | | −92.7, −100.6, −104.4, −109.2, −116.8 | 1.00 | 0.259 | 0 |
| 7  | | −91.1, −99.4, −104.7, −109.9, −116.6 | 1.00 | 0.280 | 0 |

- **J249a ✓** — energy decreases monotonically with support, **Spearman 1.00** both seeds (more restatements/sources →
  deeper attractor → lower energy).
- **J249b ✓** — the extremes are clearly distinguishable: s=8 is 26–28% deeper than s=1.
- **J249c ✓** — every edge (any support) is still correctly recalled — support modulates CONFIDENCE, not correctness.
- **J249d ✓** — perfectly monotone (0 inversions); the pre-flagged W-normalization SATURATION did NOT appear (energy
  kept dropping s=5→s=8: −109→−117).

**FINDING — a genuine substrate BENEFIT over the binary symbolic engine:** the energy substrate gives GRADED,
EVIDENCE-CALIBRATED CONFIDENCE. A fact restated more often (more sources / more evidence) sits in a DEEPER energy
minimum, so its energy is a continuous confidence signal — `energy ≈ −(log-plausibility scaled by support)`. The
symbolic engine answers True/False; the substrate additionally answers HOW STRONGLY-supported, for free, as the
EBM-native form of the redundancy principle (more support → stronger). This is a concrete answer to "what does the
energy substrate offer beyond the dict?": not an accuracy win (JEP-246 framing holds), but a NEW capability — graded
confidence from evidence accumulation. Established (Hebbian frequency effects, EBM energy = log-plausibility,
confidence calibration), named; no novelty in method. Verdict: **PASS** (predict-calibrate HIT — monotone, Spearman
1.0, no saturation, all as forecast). Combined with the energy-query (248), the substrate is a relational EBM whose
energy encodes BOTH fact plausibility (true/false, 248) AND fact support (graded confidence, 249).
