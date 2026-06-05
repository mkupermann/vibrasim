# JEP-324 — Ask-the-brain in the teaching GUI (the interactive full loop)

## Motivation
JEP-322 gave a query interface + CLI. Wire it into `tools/teach_gui.py` so Michael can teach by sentence AND then
ASK the brain questions in the same window — closing the loop interactively (teach → reason → answer), all over the
durable store. No transformer.

## Method
A module-level `answer_question(sm, q)` = `BrainQuery(sm).ask(q)` (testable without Tk), and a GUI "Ask:" box that
calls it against the GUI's live `SubstrateMemory` (which already holds sentence-taught facts via JEP-302). The
BrainQuery is rebuilt per question so it sees freshly taught facts.

## Pre-registered bars (BEFORE the run)
- **J324a (answer path correct, headless):** after teaching a few sentences into a `SubstrateMemory` (via the GUI's
  `learn_sentence` path), `answer_question(sm, q)` answers "is a poodle an animal?", "what causes cancer?",
  "can a penguin fly?" matching ground truth, both seeds (0, 7).
- **J324b (GUI wiring):** `tools.teach_gui` imports with the ask box; `answer_question` importable; no Tk window on
  import.
- **No-regression:** substrate test gate still green; 123 understanding tests green.

Predicted most-likely failure: the GUI's `learn_sentence` bridges via `ingest_engine`, which re-adds ALL engine
relations each call → duplicate facts in the store; duplicates just strengthen the same binding (harmless) but if
they shift the gate, an answer could flip. If J324a misses, report whether de-duping the bridge is needed.

## Result (seeds 0, 7): **PASS** (after completing the bridge)
- **First cut:** "can a penguin fly?"→True (wrong) and "what causes cancer?"→[] (empty). Root cause = `ingest_engine`
  (the GUI's `learn_sentence` bridge) only carried positive isa/partof/causes/hasprop — it dropped NEGATIVE facts
  (not_properties, neg_isa) and the inverse causal edge, so exceptions and abduction had no data. The standalone
  experiments added those by hand; the GUI path didn't.
- **Fixed** `ingest_engine` to also bridge `not_properties`→not_hasprop, `neg_isa`→not_isa, and the inverse
  `caused_by` edge — idempotent (skips facts already present, addressing the predicted duplicate-bloat).
  - **J324a:** after teaching 7 sentences, `answer_question` gives poodle→animal **True**, penguin fly **False**
    (exception), causes cancer **['smoking']** (abduction), both seeds. **PASS.**
  - **J324b:** `tools.teach_gui` imports with the Ask box; `answer_question` importable; no Tk on import. **PASS.**
- **No-regression:** 133 tests green; JEP-302 and JEP-322 still PASS.

## Verdict: **PASS**
The teaching GUI now closes the loop interactively: teach by sentence, then type a question in the "Ask:" box and
the brain answers from the durable store (is-a, exceptions, abduction). The fix also made the GUI-taught store
COMPLETE (negatives + causal inverse), so exceptions and "why?" work end-user — a real capability gain, not just
UI. Honest: the bug was an incomplete bridge, not the substrate; the predicted duplicate-bloat was pre-empted with
a dedup guard.

