# JEP-302 — Durable taught FACTS: sentence-teaching survives restart (knowledge side of the GUI)

## Motivation
JEP-295 made taught *letters* (perceptual exemplars) durable. But when Michael teaches by SENTENCE in the GUI
("This is a dog. A dog is a mammal."), the facts go into a transient `UnderstandingEngine` that vanishes on close.
Complete the brain's persistence: store the taught prose with the durable memory, AND bridge it into the substrate
store, so taught knowledge survives close+reopen and is reasoned over — both by the engine (replayed) and natively
by the substrate (JEP-298/300/301). No transformer.

## Method
`SubstrateMemory` gains a `sentences` corpus (the prose taught), persisted in `meta.json`; `ingest_engine(eng)`
bridges the engine's learned relations into the directed substrate store; `rebuild_engine()` replays the corpus
into a fresh `UnderstandingEngine`. The GUI's sentence path appends the sentence, re-reads it, bridges it, and
saves; on launch it rebuilds the engine from the stored corpus.

## Pre-registered bars (BEFORE the run)
- **J302a (engine knowledge persists):** teach K sentences → save → load into a FRESH `SubstrateMemory` →
  `rebuild_engine()` answers a held-out question set (is-a multi-hop + has_property + negatives) identically to the
  original engine, ≥ 0.95, both seeds (0, 7).
- **J302b (substrate knowledge persists):** after the same reload, the SUBSTRATE store (engine discarded) answers
  the is-a queries ≥ 0.90 (the JEP-299 path), both seeds — taught facts are durable on BOTH substrates.
- **J302c (GUI wiring):** `tools.teach_gui` imports and a headless teach→save→reload of the sentence path
  reproduces the taught facts (no Tk window).
- **No-regression:** JEP-295 persistence + 123 understanding tests still green.

Predicted most-likely failure: replaying the corpus is order-sensitive or some `read()` side-effect isn't captured
by sentences alone, so the rebuilt engine diverges. If J302a < 0.95, report which construction didn't round-trip
(a corpus-completeness finding), don't patch the score.

## Result (seeds 0, 7): **PASS**
- **J302a:** rebuilt engine (from stored prose) matches the original engine = **1.000** (is-a multi-hop +
  has_property), both seeds. **PASS.**
- **J302b:** substrate store (engine discarded) answers is-a vs original engine = **1.000**, both seeds. **PASS.**
- **J302c:** `tools.teach_gui` imports; headless sentence round-trip reproduces facts. **PASS.**
- **No-regression:** JEP-295 persistence PASS; 123 understanding tests green. **PASS.**
- Demo after restart: `poodle is animal` = True (engine AND substrate), `poodle can bark` = True (3 sentences
  never co-stated; 7 sentences total persisted).

## Verdict: **PASS**
Facts taught by sentence are now durable: the GUI stores the prose with the brain folder and bridges it into the
substrate, so on reopen the reasoning engine is rebuilt from the corpus AND the substrate holds the facts natively
— both answer correctly. Together with JEP-295 (durable letters) the teaching tool's whole memory — percepts AND
knowledge — survives close+reopen and grows across sessions. Honest scope: persistence is via faithful corpus
replay (the prose is the durable record) + the VSA bridge; direct method-call teaching (tell/add_rule) outside
`read()` is not captured, only sentence `read()` is.

