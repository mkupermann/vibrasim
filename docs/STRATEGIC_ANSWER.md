# Can this project be "human-like AI without an LLM"? — the definitive, evidence-based answer

Written 2026-06-03 after a long autonomous run that tested every part of the question with pre-registered
experiments and controls. Honest verdicts; established methods named as such.

## Short answer
**No — not human-like AI.** But the project has two real, honest assets and one clearly-bounded toolkit.

## The evidence (each a pre-registered experiment, both seeds)
1. **The physical substrate cannot LEARN.** Full plasticity (STDP+BTSP+correlation+bistable+propagation),
   80 A→B pairings, proper readout → NO association forms (G132 NULL; G131 inconclusive readout).
2. **The physical substrate has NO computational advantage.** As a nonlinear feature map it is NOISE on
   algebra (G133, R²=−0.49) and weak+inconsistent on geometry (G134); as an analog optimizer it fails
   (G135, atoms collapse not relax). A trivial random-feature ELM beats it everywhere, and being a serial
   Python sim it makes nothing FASTER. Its `SubstrateReservoir` is literally a numpy random matrix — the
   physics is unused.
3. **The no-LLM COGNITION stack is bigram-level on REAL language.** VSA+reservoir+RLS got 90–100% on
   TEMPLATED micro-languages (BET-130/132) but on real text it matches a bigram (0.52 vs 0.48) and gets
   WORSE with more context (G136/G136b). It captures nothing beyond the previous word on open language.

## What the project genuinely IS (no inflation)
- **A no-LLM MEMORY** — matter-position storage: store/recall bits → text → words, selective + persistent
  (maintained), the session's real breakthrough. A data store, used by classical ML for cognition.
- **A bounded no-LLM SYMBOLIC/STATISTICAL toolkit** — works on STRUCTURED/FORMAL domains: templated
  language, recursive composition (parity to length 100), retrieval-QA, rule-based code synthesis
  (BET-140–143 PASS). Real and useful for FORMAL tasks; NOT open natural language; NOT understanding.
- **A conceptual model** of physical/analog spatial computation — valuable as theory and as an analog-
  HARDWARE design target (where parallel physics is genuinely free/fast), unreachable as a software speedup.

## Why "human-like" is out of reach here
Human-like language needs open-domain understanding/generalization. The physics can't learn; the classical
no-LLM methods plateau at local statistics on real text — which is exactly the gap transformers/LLMs were
built to cross. No mix of these pieces crosses it; that is an established result, not a missing experiment.

## The only paths that could change this (each a real decision, not an experiment)
- **Allow an LLM/transformer** (drop the charter constraint) — then the substrate is a peripheral.
- **Build analog HARDWARE** — to realize the substrate's only potential edge (parallel spatial compute).
- **Accept the bounded niche** — a no-LLM memory + formal-language toolkit, honestly scoped.

The deliverable here is an honest map of what is and isn't reachable — which the charter calls the goal:
"developing a deadlock-breaking process, not necessarily succeeding at the simulation."
