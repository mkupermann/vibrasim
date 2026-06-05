# EQMOD-4 — Final State: the Understanding Engine (honest synthesis)

The definitive, honest answer to "what have we reached?" — the culmination of the JEP programme (JEP-1..221).
No LLM, no transformer, no pretrained model anywhere. Everything below is established methods, named as such; the
genuine outputs are the WORKING ENGINE, a handful of real CONCEPTUAL findings, and the predict-calibrate DISCIPLINE.

## What it does (Michael's three verbs, end to end, from real prose + perception)
- **LEARN** — `e.read(passage)` extracts FIVE fixed relation types from encyclopedic prose (is-a, part-of, causal,
  spatial-containment, comparison) at ~0.9 recall / high precision, document-scale, cross-domain; revises beliefs
  when a source corrects it; learns entirely novel concepts (proven structural, not lexical); and is **SELF-
  EXTENSIBLE** — auto-induces *new* relation types from recurring patterns in a passage (e.g. 'is capital of'), then
  extracts, queries, and answers natural questions about them ('what is the capital of France?' -> 'Paris').
- **UNDERSTAND** — multi-hop inference over a multi-parent DAG; the full faculty set (Boolean, three-valued,
  quantification, hypothetical, analogy, causal+intervention, probabilistic, temporal, provenance, mereology,
  abduction, diagnosis, planning); the COMPLETE relation-interaction matrix — taxonomy interacts correctly with
  part-of, causal, and comparison, each with its right semantics (parts distribute to subtypes, effects don't) and a
  leak guard; plus QUANTITATIVE understanding ('X has N Y' -> 'how many?'/numeric comparison) and TEMPORAL ordering
  ('X before/after Y', transitive). All domains compose in one engine (a multi-domain integration guard), with
  CONSISTENCY checking over both taxonomy and quantities.
- **COMMUNICATE** — conversational Q&A across ALL domains (is-a, part-of, causal, comparison, temporal, quantitative,
  open relations, enumeration, superlatives); multi-relation English profiles; "why?" explanations of the reasoning
  chain across is-a/part-of/causal/comparison/temporal; source summarization (with honest inconsistency-flagging);
  MULTI-TURN conversational context ("what about X?"); learning-through-dialogue; belief revision.
- **GROUND** — a concept's grounding draws on THREE complementary sources: APPEARANCE from vision (reliable coarse
  categories on real Fashion-MNIST, 0.87), NAMES from language (sharpen the fine distinctions vision blurs, 0.72 vs
  0.54), FUNCTION from observing INTERACTIONS (recovers categories that cross-cut appearance, 1.00 vs 0.50). The full
  developmental loop — perceive -> discover -> name -> read structure -> reason — composes on real images.

## Validated
Property-based SOUND, fuzz ROBUST (0 crashes/6000 adversarial), SCALABLE (1000 concepts), STRUCTURAL not lexical,
a comprehensive end-to-end INTEGRATION test, a multi-domain integration guard, and re-validation of the matured engine. 110 regression tests, every commit gated green. The substrate-relational arc (JEP-232..253) adds 22 pre-registered run-harnesses with locked bars + result.json (substrate-thread convention). REAL-PROSE HARDENING (JEP-227..231, 254..267, all from real-usage QA on FIVE new-domain passages — chemistry, definitions, geography, biology, history — each initially failing 3-5 questions, now answering ~all; cumulative validation: comprehensive all-construction document 16/16=1.00 (JEP-271), fuzz 0 crashes/4000 (JEP-265) -- the extractor now covers the common DECLARATIVE construction space): alphanumeric concepts, is-a-parent open-relation leak, numeric singular/plural + multi-word attributes in capture/comparison/question, usage-learned mass/count countability + bare-subject no-article, '-ous/-less' adjectives (not is-a), adjectival predicates as PROPERTIES, embedded ', such as X,' exemplification, read()-captured ability ('X can/cannot VERB') + singular 'can a X VERB?', PASSIVE causal ('X is caused by Y'), spatial containment ('X is in Y' -> part-of, transitive question routing), mereological verbs ('X contains/consists of Y'), 'does X have Y?' possession (with is-a inheritance), and multi-word verb-phrase temporal ('was signed before'). Consistent residual across all 5 domains: the NER/multi-word-entity wall (mid-sentence proper-noun capitalization, 'World War 2', 'human body' vs 'body') — bounded by the no-pretrained constraint.

## Where the substrate IS in the chain (JEP-232..238 — the relational engine, in the energy substrate)
Michael's recurring question, answered concretely for relational knowledge. The engine's facts had only ever lived
in Python dicts; this arc puts them — and its reasoning — IN the energy-based substrate (`world.energy.EnergyNet`,
a modular Hopfield/contrastive-Hebbian EBM):
- **Store** (232) is-a facts as content-addressable key→value attractors — recall 1.00, partial-cue-robust; capacity
  is SHARP: perfect to ~20 facts/module then a catastrophic Hopfield blackout (heteroassociative, ~0.5/value-unit).
- **Chain** (233) transitive multi-hop inference by iterated retrieval — 1.00 to 3 hops, raw or cleaned (the
  attractor self-corrects each hop within capacity).
- **Type** (234) multiple relation types in one net via VSA Hadamard role-binding — no crosstalk, every type served.
- **Reason from prose** (235 capstone) — `read()` → store → answer multi-hop is_a by relaxation, matching the
  symbolic closure on a battery (tree 1.00; found the multi-parent DAG boundary).
- **DAG** (236 NULL → 237 PASS) — slot-binding stores multiple parents; an ENERGY GATE (trained edge = deep minimum;
  empty slot = shallow) rejects phantom parents with 0 false-accept/reject → multi-parent closure 1.00.
- **Interact** (238) — the signature relation-INTERACTION matrix (part-of × is-a UP, leak guard included) runs by
  composing two content-addressable retrievals — 1.00 vs control 0.33.
- **Online** (239 PARTIAL) — the store is online-learnable one fact at a time with only MILD interference (no
  catastrophic forgetting within capacity; my forgetting prediction was wrong, the additive-Hebb direction I flagged).
- **Noise → the cure** (240 NULL → 241 PASS) — under cue noise, multi-hop chaining COMPOUNDS; per-hop attractor
  CLEANUP is NOT a reliable cure (it can lock in discrete decode errors — sharpens JEP-158); REDUNDANT AGGREGATION
  (independent noisy retrievals + majority vote) IS the regime-independent cure (4-hop 1.00 vs single-path 0.0–0.33).
- **Full engine, robust** (242 PARTIAL → 243 NULL → 244 PASS) — the COMPLETE multi-relation engine (is-a, part-of,
  causal, comparison, temporal, multi-hop each + the interaction) runs on ONE typed substrate net from one prose
  passage, matching the symbolic engine 1.00 on both seeds. The fix arc is the discipline in action: a brittle
  interaction (mis-diagnosed) → aggregation fails (the error was systematic, not random) → the right fix is the
  ENERGY-GATED chain stop (a diagnosed-lesson recurrence: detect "stored vs untrained key" by energy, not value-
  overlap, at EVERY such check — chain-root-stop as well as DAG slots).
- **Boundaries + benefits** (245–249) — the store is MEMORY + DEDUCTIVE closure, NOT inductive generalization (a
  held-out bridge edge breaks the chain; generalization needs proper geometric embeddings, JEP-23–27, not the
  attractor store) (245); the GROUNDED loop closes through the substrate — a noisy perceptual cue cleans up AND
  reasons multi-hop as one energy process (246); capacity scales LINEARLY (~0.5 edges/value-unit, verified) (247);
  the substrate is a relational EBM with TWO native query modes — single-shot ENERGY-scoring of direct-fact
  plausibility (AUC 1.00, 248) and iterated relaxation for transitive closure — and energy gives GRADED, evidence-
  calibrated CONFIDENCE (more support → deeper minimum, Spearman 1.0, 249): a genuine capability BEYOND the binary
  symbolic engine.
So the substrate is the engine's robust relational MEMORY and INFERENCE engine (store/chain/type/DAG/interaction/
full-multi-relation-from-prose), online-learnable, grounded-loop-closing, capacity-VERIFIED linear (~0.5 edges/value-
unit), with native energy-query + graded-confidence modes — and it inherits the programme's core robustness lesson
NATIVELY, with a mapped cure hierarchy: ENERGY-GATE for untrained-key detection, AGGREGATION for independent noise,
codes/capacity for systematic interference, GEOMETRIC EMBEDDINGS for inductive generalization; aggregation, not
cleanup, cures multi-hop compounding under noise. The honest boundary: the attractor store is memory+deduction (not
induction), with no native negation/contradiction (those stay symbolic, tested in JEP-250); the genuine benefit
beyond symbolic is graded plausibility/confidence, not an accuracy win. VALIDATED SOUND at scale across the FULL relation vocabulary
(JEP-251: is-a 0.998 match over 50 random taxonomies × 2 seeds, 0 systematic leaks; JEP-252: is-a/part-of/causal/
comparison/temporal each 1.00 over 30 chains × 2 seeds, 0 systematic AND 0 cross-relation leaks — typed binding
isolates relations at scale; residual = occasional non-systematic retrieval flakes, aggregation-curable) —
paralleling the symbolic engine's JEP-124 soundness.
- **Three-verb loop closed** (253) — the full LEARN→UNDERSTAND→COMMUNICATE loop runs THROUGH the substrate: read
  prose → store → energy-gated multi-hop reasoning → render English STRING-IDENTICAL to the symbolic engine (1.00
  both seeds, incl a depth-5 chain). The substrate is the engine's complete relational stack (memory + inference +
  communication + grounding), no transformer anywhere — the substrate supplies reasoning, the engine's template
  supplies grammar. All established
(Hopfield CAM + iterated associative recall + VSA binding + Hopfield energy as a stored-vs-spurious detector +
ensemble voting), named; NO novelty — the value is the demonstrated end-to-end connection + its measured envelope.
Pattern: docs/patterns/substrate_relational_store.md.

## Genuine conceptual findings (the real intellectual output)
1. **Compounding vs aggregation** is universal across structure-learning, reasoning, and learn-from-prose: chained
   inference compounds errors; redundant aggregation cures it. The compounding EXPONENT is representation-dependent
   (symbolic-independent exponential / continuous-independent √k-averaging / systematic linear).
2. **REDUNDANCY unifies robustness AND generalization** — a single-path tree supports neither, a many-path DAG both.
3. The real-prose parse gate is the **GENRE, not the extractor** (encyclopedic works, dense logic prose doesn't).
4. **Grounding is three-sourced** (appearance/names/function), each at a different granularity; vision and language
   are complementary (coarse vs fine); function needs interaction observation, not appearance.
5. **Abstract concepts** reason symbolically like any taxonomy; only their GROUNDING is special (no perceptual
   referent — learned relationally, as humans do).
6. The engine's relational knowledge AND its reasoning can live **in the energy-based substrate** (Hopfield CAM +
   VSA binding), bounded by a sharp ~20-edge/module capacity cliff; to detect a stored vs a spurious associative
   key, measure the key→value BINDING ENERGY, not the value's cleanliness (in an attractor net the value is always
   clean) — the JEP-236→237 NULL-to-fix lesson.

## The honest frontier (what is NOT reached, and exactly why)
- **REAL embodied perception** — the grounding MECHANISMS are demonstrated, but on toy/synthetic perception
  (prototypes, synthetic affordances/interaction logs). Real rich grounding needs embodied sensors + interaction.
- **A real encyclopedic CORPUS at scale** — `read()` works on encyclopedic prose; testing it on real Wikipedia-scale
  text needs a downloaded corpus (authorization) and hits the NL long-tail (classic patterns can't cover arbitrary
  prose; learned extractors are forbidden).
- **Open-ended / creative GENERATION** — factual generation (profiles, explanations, Q&A) works; open generation is
  blocked under the no-transformer rule.

## Honest assessment vs the goal
This is NOT human-level understanding and NOT novel — it is a comprehensive, validated, substrate-legal FOUNDATION
that does learn/understand/communicate/ground end to end under a hard constraint, with every frontier precisely
characterized as to why it is open and what would unblock it. predict-calibrate 123/153 (80%, converged), converging within
settled domains, no diagnosed lesson recurred; the discipline (pre-registration, honest NULLs, the 12 recurring
error classes) is the transferable deliverable. Guides: docs/UNDERSTANDING_ENGINE.md, docs/EQMOD4_GUIDE.md; patterns:
docs/patterns/; demos: tools/demo_{learn_from_prose,grounded_understanding,full_conversation,full_qa}.py.
