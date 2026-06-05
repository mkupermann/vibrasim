# JEP-233 — does the substrate do TRANSITIVE is-a inference by chaining retrievals?

Pre-registered 2026-06-05 (BEFORE the run). JEP-232 showed the substrate (EnergyNet) carries is-a relations as
content-addressable key→value attractors (recall 1.00 to K≈20). But the Understanding Engine's SIGNATURE power is
TRANSITIVE multi-hop inference — is_a(a,c) via a→b→c. This BET asks whether the energy-based substrate supports
that by CHAINING retrievals: retrieve parent(child), present the result as the next key, repeat — walking the
is-a chain through relaxation, not symbolic graph traversal.

## Method (no transformer; iterated Hopfield key→value retrieval, named as such)
- Same store as JEP-232: chain c0→c1→…→cn (is-a), each fact = `concat(code[child], code[parent])`, trained as
  attractors (contrastive-Hebbian). KEY=[0:40], VALUE=[40:80].
- k-HOP retrieval from c0, two re-clamp modes:
  - **decode**: retrieve → decode value to nearest concept code → re-clamp that CLEAN code as the next key (clean-up each hop).
  - **raw**: retrieve → re-clamp the RAW settled value bits as the next key, NO symbolic clean-up between hops
    (the stronger "substrate-only chaining" claim); decode only at the END.
- Correct iff the k-hop result decodes to c_k (the true k-th ancestor). K=12 facts (within capacity), seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J233a | 2-hop transitive inference (decode) | k=2 recall ≥ 0.85 (both seeds) |
| J233b | 3-hop transitive inference (decode) | k=3 recall ≥ 0.85 (both seeds) |
| J233c | Substrate-only chaining survives ≥1 raw hop | raw k=2 recall ≥ 0.70 (both seeds) |
| J233d | Chaining beats an untrained control | untrained net, k=2 (decode) recall ≤ 0.40 (both seeds) |

PASS = J233a–d → the substrate performs transitive is-a inference by iterated retrieval: multi-hop reasoning lives
in the energy-based substrate, not only in the symbolic closure. NULL (honest): J233a/b fail → chaining breaks
(re-clamped value is not a clean key, or hops desync); J233c fails → raw chaining needs symbolic clean-up every
hop (the substrate alone can't chain); J233d fails → the readout chains trivially without trained attractors.
No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 Within capacity single-hop is 1.00 and the settled value slot is a clean ±1 attractor, so DECODE-rechain should
chain cleanly: J233a (k=2) and J233b (k=3) ≥ 0.85, ~1.00. J233d control fails (untrained → first hop is noise →
≤0.40). The open question is RAW chaining: re-clamping the raw value bits (40 units) as the next key feeds a clean-
ish but un-cleaned code; I expect J233c (raw k=2) ≥ 0.70 (the value slot is near-saturated to the attractor), but
raw k=3 may DEGRADE as small per-hop deviations compound (error accumulation across hops — the multi-hop analogue
of error-class 10/JEP-232's capacity calibration). Net prediction: a/b/d PASS, c PASS at k=2; raw k=3 the likely
miss. The substrate does transitive inference by chaining (established iterated associative recall; no novelty) —
robustly with per-hop clean-up, and for a bounded number of hops even without it.

## RESULT (2026-06-05): PASS — all 4 bars; raw chaining MORE robust than predicted

| seed | decode k2 | decode k3 | raw k2 | raw k3 | control k2 |
|------|-----------|-----------|--------|--------|------------|
| 42 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |
| 7  | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |

- **J233a ✓ / J233b ✓** — 2-hop and 3-hop transitive is-a inference by iterated retrieval: **1.00**, both seeds.
- **J233c ✓** — raw chaining (re-clamp the settled value bits, NO symbolic clean-up between hops): **1.00** at k=2.
- **J233d ✓** — untrained control **0.00** at k=2: the trained attractors do the chaining, not the readout.

**CALIBRATION (favorable — my caution was beaten):** I predicted raw **k=3** might DEGRADE from per-hop error
accumulation. It did NOT — raw k=3 = 1.00. Within capacity the settled value slot lands EXACTLY on the attractor
(its sign ≡ the clean code), so re-clamping raw bits is identical to re-clamping the cleaned code: the substrate's
attractor dynamics **self-correct every hop**, so error does not accumulate. Raw ≡ decode within capacity. (The
error-accumulation worry is real only NEAR/above capacity, where single hops are already imperfect — the JEP-232
cliff.) All 4 pre-registered bars passed as predicted → verdict HIT; the extra raw-k3 sub-worry resolved better
than forecast. Honest note: not retuned, just out-performed.

**FINDING:** the energy-based substrate performs the Understanding Engine's SIGNATURE capability — transitive
multi-hop is-a inference — purely through iterated energy relaxation, content-addressably, with NO symbolic graph
traversal and NO per-hop clean-up needed (within capacity). Combined with JEP-232 (the relational store), the
substrate is a complete relational memory + inference engine for is-a: store facts as key→value attractors, walk
the transitive closure by re-clamping. Established (Hopfield CAM + iterated associative recall), named as such; NO
novelty — the value is the demonstrated end-to-end answer to "where is the substrate in the chain?": the
Understanding Engine's relational knowledge AND its multi-hop reasoning can both live IN the substrate, bounded by
the ~20-fact/module capacity cliff. Verdict: **PASS.**
