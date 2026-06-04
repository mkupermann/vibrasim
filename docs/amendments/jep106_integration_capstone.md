# JEP-106 — integration capstone: a full conversation exercising the WHOLE engine (and a bug it found)

## Why
A single conversation that uses every capability together (deduction, multi-parent, Boolean, relational, three-
valued, induction, dialogue-learning, correction) is both a deliverable demo (tools/demo_full_conversation.py) and
a real integration test.

## What the demo FOUND (the recurring lesson)
The capstone demo surfaced an integration gap the per-tier tests missed: respond() (the conversational entry point)
routed to explain() but NEVER to ask_bool(), so Boolean-composed questions returned "I don't know" instead of
Yes/No. Per the standing lesson (exercise on natural/integrated usage, not the test-friendly path), fixed respond()
to route connective questions through ask_bool. Added a regression test. 18 tests gated green.

## Result
The full conversation now runs clean: multi-parent ("A poodle is a dog and a pet."), multi-hop deduction with
explanation, Boolean ("...an animal and ...a pet?" -> "Yes."), relational same-bag, three-valued ("I don't know
whether a poodle is a quark."), induction ("Yes - I induced that birds fly."), learning-through-dialogue (gap
identified -> taught -> answered), and correction (whale: fish -> not fish -> mammal). Established methods
throughout, named; no novelty. HONEST: simple controlled/natural language; the hard frontier (real-prose parse,
coreference, unsupervised structure, open generation, rich grounding) remains the multi-year open work.
