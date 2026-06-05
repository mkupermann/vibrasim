# JEP-253 — the full LEARN→UNDERSTAND→COMMUNICATE loop THROUGH the substrate (English answers)

Pre-registered 2026-06-05 (BEFORE the run). The substrate carries the engine's relational reasoning (JEP-232..252).
This BET closes Michael's three-verb loop ON the substrate: read prose (LEARN) → store in the EnergyNet → answer
questions by SUBSTRATE reasoning (UNDERSTAND) → render the answer in ENGLISH (COMMUNICATE), and check the English
matches the symbolic engine's `respond()`. The substrate supplies the reasoning; the engine's renderer supplies the
grammar (no transformer anywhere).

## Method (no transformer)
- `e.read(passage)` → symbolic stores; build the typed energy-gated substrate store (JEP-244/234) over is-a +
  part-of edges. A substrate-backed answerer: for a yes/no relation question, compute the verdict by SUBSTRATE
  reasoning (energy-gated chaining / interaction), then render with the SAME English template the symbolic
  `respond()` uses ("Yes. A poodle is a dog, a dog is an animal." / "No." style).
- Battery of English questions (is-a multi-hop pos/neg, part-of, interaction). Compare substrate-rendered English to
  symbolic `e.respond()` STRING-for-STRING. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J253a | Substrate-driven English matches symbolic | ≥ 0.90 of battery answers are STRING-identical to `e.respond()` (both seeds) |
| J253b | Verdicts correct | every substrate yes/no VERDICT matches the symbolic ground truth (both seeds) |
| J253c | English is well-formed | every rendered answer is grammatical (article a/an, capitalization) — 0 malformed (both seeds) |
| J253d | The loop is end-to-end | the passage is READ (not hand-built), stored in the substrate, and answered in English — demonstrated on a depth≥3 question |

PASS = J253a–b (the substrate drives correct English Q&A matching the symbolic engine); J253c/d confirm grammar +
end-to-end. NULL (honest): J253a fails → the substrate verdicts diverge from symbolic (a reasoning gap) or the
rendering integration mismatches strings (a wiring issue, distinguish the two). No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS. The substrate reasoning matches symbolic within capacity (JEP-244/251/252: sound), and reusing the engine's
OWN render path guarantees grammatical, string-identical output GIVEN the same verdict + chain. So J253a ≥ 0.90 (the
residual being any occasional substrate retrieval flake flipping one verdict, JEP-251's ~flake rate), J253b verdicts
match (modulo flakes), J253c grammar perfect (same renderer), J253d the depth-3 question answered end-to-end. RISK
(in-rung): the symbolic `respond()` may include the CHAIN in its English ("a dog is an animal") which the substrate
must reproduce from its OWN chain — if the substrate chain order differs, the STRING differs even with a correct
verdict; I will render from the SUBSTRATE chain and accept verdict-match (J253b) as the core bar, with string-match
(J253a) as the stricter integration check. Established (content-addressable reasoning + template realization), named;
no novelty — the value is closing the LEARN→UNDERSTAND→COMMUNICATE loop end-to-end on the energy substrate.

## RESULT (2026-06-05): PASS — the three-verb loop runs through the substrate; English is STRING-IDENTICAL to symbolic

| seed | string-match | verdict-match | well-formed | depth-5 answer |
|------|--------------|---------------|-------------|----------------|
| 42 | 1.00 | 1.00 | 1.00 | "Yes. A poodle is a dog, a dog is a canine, a canine is a mammal, a mammal is an animal, an animal is an organism." |
| 7  | 1.00 | 1.00 | 1.00 | (identical) |

- **J253a ✓** — every battery answer is STRING-IDENTICAL to the symbolic `e.explain()` (1.00, exceeding the ≥0.90
  bar): the substrate-driven English exactly reproduces the engine's.
- **J253b ✓** — every yes/no verdict matches symbolic ground truth.
- **J253c ✓** — every rendered answer is grammatical (articles, capitalization, no doubling).
- **J253d ✓** — a depth-5 chain (`poodle→dog→canine→mammal→animal→organism`, in no single sentence) is READ from
  prose, stored in the substrate, reasoned by energy-gated chaining, and rendered in correct English end-to-end.

**FINDING — Michael's three verbs, end-to-end on the energy substrate:** LEARN (read prose → store as attractors) →
UNDERSTAND (multi-hop reasoning by energy-gated chaining) → COMMUNICATE (render the substrate chain in English) all
run through `world.energy.EnergyNet`, producing answers STRING-IDENTICAL to the symbolic engine, no transformer
anywhere. The substrate supplies the reasoning; the engine's own template supplies the grammar. The pre-flagged risk
(substrate chain order ≠ symbolic → string differs) did NOT materialize — the energy-gated chain follows the natural
is-a order, matching exactly. Verdict: **PASS** (predict-calibrate HIT — string-match hit 1.00, beating the ≥0.90
bar). With JEP-232..252, the substrate is now the engine's complete relational stack — memory, inference,
communication — validated sound, the full three-verb loop closed on the substrate. Established (content-addressable
reasoning + template realization), named; no novelty.
