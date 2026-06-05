# Real-Prose Conversational Brain — Summary (JEP-367 → 394)

A consolidated map of what the substrate can do after the 2026-06-05 arc. Everything below runs on substrate
primitives — durable VSA store, closure consolidation, defeasible reasoning, rule-based normalization — with **no LLM,
no transformer, no pretrained model**. Every step was pre-registered (bars before the run) in `docs/amendments/jepNNN_*`
and logged in `docs/PREDICTION_LOG.md`; misses are recorded as misses.

## What it does now (validated end-to-end)
The substrate **reads realistic factual prose over multiple days and answers it without mistakes inside the captured
domain, abstaining honestly outside.** Integration capstone (JEP-393/394): a factual article read across days →
**Q&A 1.0**, correction held, zero junk, durable consolidation, perfect abstention.

- **Real-prose capture (~90% of a natural article, zero junk):** plurals, relative clauses, conjunctions-of-clauses,
  appositives, "such as" lists, quantifiers, passive voice, definitions, discourse markers/corrections. (JEP-379→392)
- **Reliable reasoning at scale (deep is-a 1.0, negatives 1.0):** transitive multi-hop, inheritance, defeasible
  exceptions/negation — error-free on hundreds of facts at depth 8. (JEP-368→378)
- **Relation types, all queryable:** is-a, part-of ("is X part of Y?"), causal ("what causes X?"), counts ("how many
  wheels…?"), properties ("is a dog warm-blooded?"). (JEP-388→390, 394)
- **Multi-day accumulation:** reads across separate save/load sessions, no forgetting, cross-day multi-hop. (JEP-383)
- **Corrections:** "Actually, a whale is not a fish" overrides an earlier statement (defeasible). (JEP-391)
- **Curiosity:** after reading, "what is not clear to you?" lists genuinely-undefined concepts; teaching one closes the
  gap and unlocks new reasoning. (JEP-392)
- **Honest abstention:** says "I don't know" on anything not taught — never hallucinates. (throughout)

## The engineering spine (the hard-won part)
Michael's "no mistakes" gate exposed that consolidation-naive reasoning collapses at scale (adversarial 0.4). The fix
chain, each pre-registered, with the NULLs that ruled out wrong hypotheses:
- **Closure consolidation** (materialize the transitive closure → single-hop reasoning that doesn't compound per-hop
  error). Dimension is NOT the lever (JEP-369/374 NULL — compounding, not noise).
- **Consolidation-aware analog readout** for closed is-a — the deep floor was a `sign()`-quantization artifact (JEP-377),
  closed by a magnitude-preserving cleanup (JEP-378). Edge reinforcement does NOT work under sign readout (376 NULL).
- New durable APIs: `consolidate_closure(auto_scale)`, `edge_sim_analog`, `closed_relations` (persisted),
  `Conversation.consolidate()`. Pattern: `docs/patterns/closure_consolidation.md`.

## The honest standing boundary
- **Open-domain PhD competence is NOT reachable** without an LLM (the untaught knowledge tail; JEP-362 measured the
  Zipfian asymptote). The reachable target is a **bounded, taught, consolidated domain** — now genuinely error-free.
- **Meta-abstraction does not emerge:** the system applies and learns abstractions and a taught abstraction generalizes
  broadly (big leverage), but it does NOT invent a new *kind* of abstraction unprompted (JEP-363); it does reliably
  DETECT and flag what it can't yet do (JEP-364), so the teacher-seeded library is self-prompting.
- **Minor residual gaps (logged):** adjective+noun relational subjects ("Worn brakes cause accidents"); `gaps()`
  surfaces part-of/causal-referenced concepts (broader than is-a).

## How to use it
`docs/HOW_TO_TALK.md` — `tools/talk.py` (live), `tools/read_to_brain.py` (read over days), `tools/web_gui.py`
(browser). The brain is a durable folder; copy to back up, point `--dir` to continue. Names methods honestly
(VSA/HRR, anti-unification, reservoir, energy/Hopfield are established; "new" reserved for genuine novelty).
