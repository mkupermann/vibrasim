# JEP-423 — LLM-parent teaches a coherent topic; substrate answers complex multi-relation questions

## Motivation
Validate the deliverable (LLM-as-parent teaching) at a richer scale than JEP-416: a coherent real topic (the Solar
System) with a dense web of is-a, attributes, properties, and relations. The LLM teacher distills ~40 faithful facts;
the substrate (no LLM) must answer COMPLEX questions spanning multiple relation types and multi-hop reasoning. This is
the concrete capability Michael will use — taught knowledge, reliably queried. No transformer in the substrate.

## Method
Teach a distilled Solar-System knowledge graph (planets, the Sun, moons; is-a taxonomy + attributes like "the largest
planet", part-of like moons, properties, relations) via `Conversation`. Then ask a fixed set of complex questions
(multi-hop is-a, attributes, properties, counts, relations) and verify correctness, zero junk, persistence.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J423a (taught cleanly):** ≥ 35 facts stored with ZERO junk (no multi-word/function-word entities), both seeds (0, 7).
- **J423b (complex Q&A):** ≥ 0.90 accuracy on a fixed ~12-question set spanning is-a multi-hop, attributes, properties,
  and "what is the largest planet?"-style superlatives, both seeds.
- **J423c (clean + durable):** junk rate 0.0; the knowledge persists across save/load; `pytest -m "not slow"
  tests/test_conversation.py` passes.

If complex Q&A misses, report which relation type fails. Predicted PASS — the deliverable validated at topic scale.
Bars fixed; no retuning. No transformer in the substrate.

## Result (seeds 0, 7): **PARTIAL** — exposed real substrate limits on natural topic knowledge (honest finding)
- **J423a (taught cleanly): NOT met** — 32 facts (target 35), 0 junk. Some facts lost: "The Milky Way is a galaxy"
  (multi-word PROPER NOUN "Milky Way" rejected by the junk guard); a few superlatives stored only the is-a part.
- **J423b (complex Q&A): NOT met — 0.5.** Storage is largely correct (planet→body via head extraction; "is earth a
  body?"→Yes works), but the QUESTIONS fail on:
  1. **multi-word class in the question** — "is Earth a celestial body?" isn't normalized to head "body" (storage does
     this, the query parser doesn't), so the question doesn't match;
  2. **superlative queries** — "what is the largest planet?" has no handler (the "largest" is dropped at storage, only
     jupiter→planet kept);
  3. **proper-noun morphology** — "Mars has two moons" stores (**mar**, has_moons, 2): `_singular` over-strips the
     proper noun "Mars"→"mar", so "how many moons does Mars have?" misses;
  4. **multi-word proper noun** — "Milky Way" rejected entirely.
- **J423c: NOT met** — junk 0 and OOD abstention OK, but persistence check failed on the lost facts; suite green.

## Verdict: **PARTIAL — honest finding: the substrate struggles with multi-word terms, proper nouns, and superlatives**
Teaching a real topic (not a tidy synthetic taxonomy) surfaced genuine limitations: multi-word classes are handled at
STORAGE (head extraction) but not in QUESTIONS; multi-word PROPER NOUNS ("Milky Way") are rejected by the junk guard;
proper nouns ending in "s" are wrongly singularized (Mars→mar); and superlative queries ("largest planet") have no
handler. These are real gaps for natural knowledge — to be fixed (JEP-424). The LLM-as-parent can partly work around
them (single-token names), but the cleaner path is to fix the query-side head extraction, superlative storage/query,
and proper-noun morphology. Honest PARTIAL; bars not moved. No transformer.
