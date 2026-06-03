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

## The no-LLM toolkit's PRECISE boundary (G137)
It generalizes relations that are LINEAR in per-symbol features (comparison v[i]>v[j], weighted votes —
BET-130/132). It is at CHANCE on NONLINEAR composition (modular sum / XOR-like — G137) and bigram-level on
open language (G136). So the niche is "linearly-composable structured relations + retrieval + rule-based
synthesis," not open language. (Also: tasks whose answer depends only on the previous token are
bigram-trivial and prove nothing — a caveat for reading the BET headline numbers.)

## Why "human-like" is out of reach here
Human-like language needs open-domain understanding and NONLINEAR/contextual generalization. The physics
can't learn; the classical no-LLM readout is linear, so it plateaus at local statistics / linear
composition. That is exactly the gap transformers cross; no mix of these pieces crosses it — an established
result, not a missing experiment.

## On building HARDWARE (the one path that could give the substrate a real edge)
Honest: you CAN build a parallel hardware version (FPGA/ASIC running the EQMOD update rules with each
spatial cell as a processing element, updating simultaneously — the physics that is serial in Python
becomes parallel in silicon). BUT it would be FAST AT NOTHING USEFUL: G133–G135 proved the physics computes
no useful function (memory only). A fast implementation of an empty computation is still empty. The real,
established analog-computing substrates that DO compute useful things are DIFFERENT from EQMOD's physics:
memristor crossbars (O(1) analog matrix-vector products), coupled-oscillator / Ising machines (combinatorial
optimization — the closest match to EQMOD's "vibrations"), and reaction-diffusion chemical computers
(spatial/geometry problems). Pursue those if the goal is physical computation; EQMOD-specific hardware is
not justified by any computational result here.

## The only paths that could change this (each a real decision, not an experiment)
- **Allow an LLM/transformer** (drop the charter constraint) — then the substrate is a peripheral.
- **Build analog HARDWARE** — to realize the substrate's only potential edge (parallel spatial compute).
- **Accept the bounded niche** — a no-LLM memory + formal-language toolkit, honestly scoped.

## The buildable no-LLM physical-AI stack (demonstrated, G138–G143) — and its honest ceiling
The oscillator/Ising/Boltzmann family (NOT EQMOD's physics) is a complete, buildable, no-LLM primitive set,
each shown with working reference code:
- **Optimize** — Ising/MAX-CUT, optimal on small graphs, scales competitively (G138/G139).
- **Recall** — Hopfield content-addressable memory from noisy cues (G140).
- **Learn** — Boltzmann machine learns a distribution unsupervised (G141, corr error 0.018).
- **Generate** — RBM generates valid NOVEL bars-and-stripes (systematic generative generalization, G142).
**Ceiling (G143):** depth (DBN) does NOT extend it on these tasks — it is BOUNDED to small/structured
problems and does not scale by depth toward open-domain/human-level. The route that scaled is the
transformer; the charter excludes it. So: a real no-LLM AI stack exists and is buildable, but it is bounded
well below human-level, and it runs on the Ising/Boltzmann paradigm — not on EQMOD.

## On "this has no value"
The EQMOD substrate's computational value: honestly near zero (proven, even allowing an LLM). The WORK'S
value is not zero: (1) a definitively-mapped negative + the matter-position memory finding; (2) a rigorous
honest process (50+ pre-registered experiments, 7 self-corrections); (3) a working, evidence-backed redirect
to the genuinely useful no-LLM physical paradigm. Disappointing relative to "the substrate becomes a mind,"
real relative to "know exactly what's reachable and what to build instead."

The deliverable here is an honest map of what is and isn't reachable — which the charter calls the goal:
"developing a deadlock-breaking process, not necessarily succeeding at the simulation."
