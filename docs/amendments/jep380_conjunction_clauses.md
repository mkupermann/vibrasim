# JEP-380 — Close the JEP-379 gap: conjunction-of-clauses + irregular plurals

## Motivation
JEP-379's one real parse gap: "Salmon are fish, and fish are animals" parsed to ZERO facts. Two causes: (1) the
conjunction-of-clauses form "X are Y, and Z are W" is not split into its two clauses; (2) irregular plurals that don't
end in "s" (salmon, fish, sheep) are missed by the plural is-a rule (which requires a trailing "s"). Fix both in
`_normalize_for_learning` and verify the gap closes end-to-end with no regression. No transformer.

## Method
- Add a conjunction-of-clauses splitter (split on ", and " when BOTH sides are "<NP> are/is <NP>" clauses; the comma
  guards against the conjunction-SUBJECT form "X and Y are Z").
- Add a general "X are Y" rule for single-word objects that also handles irregular plurals (not just `...s are`).
- Re-test: the conjunction extracts both edges; "is a salmon an animal?" answers yes from the real paragraph; the rest
  of JEP-379 still holds; the conversation suite stays green.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the splitter + general rule extract salmon→fish and fish→animal, so "is a salmon an animal?" → yes (multi-
hop after consolidation), without breaking the conjunction-subject form or other parses.

- **J380a (conjunction extracted):** for "Salmon are fish, and fish are animals", BOTH (salmon, isa, fish) and (fish,
  isa, animal) are learned; and a second example ("Sharks are fish, and fish are vertebrates") likewise yields both
  edges, both seeds (0, 7).
- **J380b (gap closed end-to-end):** in the JEP-379 paragraph, "is a salmon an animal?" → yes via `Conversation.say()`,
  both seeds.
- **J380c (no regression):** the conjunction-SUBJECT form still works ("Dogs and cats are carnivores" → dog→carnivore
  AND cat→carnivore); JEP-379's poodle→animal still yes and OOD abstention still 1.0; `pytest -m "not slow"
  tests/test_conversation.py` passes.

If the splitter over-triggers (e.g. mangles "X and Y are Z" or a relative clause), report it. Predicted: clean close.
Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — gap closed, no regression)
- **J380a (conjunction extracted): PASS** — "Salmon are fish, and fish are animals" → BOTH (salmon, isa, fish) and
  (fish, isa, animal); "Sharks are fish, and fish are vertebrates" → both edges. Both seeds.
- **J380b (gap closed end-to-end): PASS** — "is a salmon an animal?" → **yes** via `Conversation.say()` on the real
  paragraph (salmon→fish→animal multi-hop after consolidation). Both seeds.
- **J380c (no regression): PASS** — conjunction-SUBJECT form still works ("Dogs and cats are carnivores" → dog→carnivore
  AND cat→carnivore); poodle→animal still yes; OOD abstention still holds; `tests/test_conversation.py` **10 passed**.
  Both seeds.

**End-to-end confirmation (re-running JEP-379):** in-text accuracy rose **0.75 → 0.875** (facts 9 → 11), and the ONLY
remaining "miss" is `is a sparrow an animal?` — my mislabeled ground truth (the text never states birds are animals, so
the substrate correctly abstains). Every actually-derivable in-text question is now answered correctly; J379a's ≥0.80
bar is now met (0.875), OOD abstention still 1.0.

## Verdict: **PASS — real-prose capture extended; the JEP-379 gap is closed**
Adding the conjunction-of-clauses splitter ("X are Y, and Z are W" → two normalized clauses) and a general "X are Y"
rule (which also catches irregular plurals like salmon/fish/sheep that the trailing-"s" rule missed) closes the one
genuine parse gap from JEP-379, with the conjunction-subject form and all prior parses intact and the suite green. The
substrate now reliably captures and reasons over more of a real encyclopedia paragraph, answering every derivable
question correctly with perfect honest abstention on the rest. Established method (rule-based normalization over
substrate primitives); no transformer.
