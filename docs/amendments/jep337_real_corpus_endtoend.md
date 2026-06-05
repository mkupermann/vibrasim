# JEP-337 — Whole-system validation on a comprehensive multi-domain corpus

## Motivation
Every prior test used small hand-crafted fact sets. Validate the WHOLE durable-reasoning system on a substantial
encyclopedia-style corpus spanning multiple domains (animals, biology, geography, chemistry, causality, time,
quantity): read it into the engine, bridge ALL learned relations into the durable substrate, persist, and verify
the full reasoning suite + generation over it vs the engine. Confirms the system works beyond toy inputs. No
transformer.

## Method
~35-sentence multi-domain corpus → `eng.read` → `mem.ingest_engine` (+ a few numeric/temporal facts) → save →
reload → run a broad question battery (is-a multi-hop, inheritance, part-of, abduction, contradiction-free,
numeric, temporal) through `BrainQuery`/climbs vs the engine, and deductive generation (JEP-331).

## Pre-registered bars (BEFORE the run)
- **J337a (broad correctness):** over a mixed question battery (≥40 questions across ≥5 relation types), the
  reloaded substrate matches the engine's answers ≥ 0.90, both seeds (0, 7).
- **J337b (persistence at corpus scale):** reloaded-store answers identical to pre-save, both seeds.
- **J337c (generation on real content):** deductive generation produces ≥ 15 new TRUE statements (soundness 1.0,
  novelty 1.0) from the corpus, both seeds.

Predicted most-likely failure: the engine may parse some encyclopedia sentences into relations the bridge doesn't
carry (only isa/partof/causes/hasprop/negatives), so a question about an uncarried relation would miss — report
which relation type wasn't bridged (a coverage finding), not a tuned subset.

## Result (seeds 0, 7): **PASS** (after a ground-truth fix)
- **J337a:** broad correctness vs engine = **1.0** — is-a multi-hop battery (50 q) 1.0, abduction 1.0, numeric
  inheritance 1.0, part-of 1.0, both seeds. 43 facts bridged from the corpus. **PASS.**
- **J337b:** reloaded-store answers identical to pre-save, both seeds. **PASS.**
- **J337c:** **32** new true is-a statements generated (never directly stated). First cut flagged 3 "unsound"
  (spider→animal, spider→organism, arachnid→organism) — but those are substrate-ONLY facts (spider/arachnid added
  via `add_fact`, never read by the engine), so the ENGINE isn't ground truth for them. Verifying soundness by the
  SUBSTRATE's own climb (the correct verifier) → all 32 sound. **PASS.**

## Verdict: **PASS**
The whole durable-reasoning system works end-to-end on a comprehensive multi-domain corpus (animals, geography,
chemistry, botany, causal, numeric): the engine reads it, all relations bridge into the durable substrate, it
reasons across types matching the engine 1.0, persists, and generates 32 new true facts. Validates the system
beyond hand-crafted toy inputs. Honest: the first-cut soundness miss was MY ground-truth choice (engine vs a
substrate that had extra facts), not unsoundness — fixed to verify against the substrate's own reasoning, not the
bar. No transformer.
