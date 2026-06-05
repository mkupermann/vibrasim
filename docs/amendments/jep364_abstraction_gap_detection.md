# JEP-364 — Detecting the missing rung: can it flag a structure it has no abstraction for?

## Motivation
JEP-363 showed the system does NOT invent a new abstraction type alone. The next honest question: can it at least
*notice* when an input fits NONE of its learned abstractions, and flag THAT one for teaching? If yes, the teacher-
seeded library becomes **self-prompting** — the system points at its own missing rungs ("I can't parse this kind of
sentence — teach me"), the teacher supplies one example-set, and the gap closes. That is the practical loop that makes
a growing abstraction library tractable: you don't guess what to teach; the system tells you. No transformer.

This is detection (knowing what it can't do), explicitly NOT invention (J363c showed invention doesn't emerge). The
distinction is the whole point: a system that knows the boundary of its competence is honest and teachable even though
it can't cross the boundary alone.

## Method (real substrate machinery: `induce_construction` + a coverage check)
The system holds a set of LEARNED templates (active + passive, induced from examples). "Covered" = at least one
learned template yields a fact from the sentence; "uncovered/flagged" = no learned template fires.
- **J364a (detection):** stream a held-out ACTIVE sentence (covered by a learned template) and a never-taught
  DITRANSITIVE sentence ("The dog gave the cat a bone"). The system must flag the ditransitive as uncovered and NOT
  flag the active one (no false alarm on a structure it does know).
- **J364b (the gap closes once taught):** supply 2 labeled examples of the ditransitive; `induce()` the new template;
  re-run coverage — the previously-flagged sentence is now covered and yields the correct core fact (dog, gave, bone).
- **J364c (detection ≠ invention, honest control):** BEFORE teaching, confirm the system cannot itself produce the
  correct ditransitive fact (consistent with J363c) — it flags the gap but does not fill it unaided.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: **detection works (J364a/b PASS), invention does not (J364c confirms the gap pre-teaching).** The system
reliably identifies inputs no abstraction covers and closes the gap from one taught example-set — but cannot fill the
gap before teaching. The self-prompting loop is real; the autonomy of inventing the abstraction is not.

- **J364a (flag the unknown, spare the known):** ditransitive flagged uncovered AND active sentence NOT flagged, both
  seeds (0, 7).
- **J364b (taught → covered):** after inducing the ditransitive template from 2 examples, the flagged sentence is
  covered and yields exactly (dog, gave, bone), both seeds.
- **J364c (honest control):** pre-teaching, no learned template yields the correct ditransitive fact, both seeds.

Either outcome is the finding. If detection itself fails (flags a known structure, or misses the unknown), report it —
that would mean the library can't even self-prompt, a harder limit. Predicted: detection works cleanly. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — all three bars)
- **J364a (flag the unknown, spare the known): PASS** — the never-taught ditransitive "The dog gave the cat a bone"
  was flagged uncovered (no learned template fired), while the held-out active "The fox caught the bird" was correctly
  NOT flagged (it matches a known abstraction). No false alarm. Both seeds.
- **J364b (taught → covered + generalizes): PASS** — given 2 labeled ditransitive examples, `induce()` built the new
  template; the flagged sentence became covered and yielded exactly **(dog, gave, bone)**, AND the new abstraction
  generalized to a held-out dative "The man gave the dog a stick" → **(man, gave, stick)**. One example-set closes the
  gap for the whole construction type. Both seeds.
- **J364c (honest control): PASS** — before teaching, no learned template produced the correct ditransitive fact: the
  system flags the gap but does not fill it unaided (consistent with J363c). Both seeds.

## Verdict: **PASS — the teacher-seeded library is self-prompting**
The system reliably **detects** when an input fits none of its learned abstractions and flags exactly that one
(without false-alarming on structures it does know), then **closes the gap from a single taught example-set** and
generalizes the new abstraction to held-out fillers. This is the practical loop that makes a growing abstraction
library tractable: you don't have to guess what to teach — the system points at its own missing rungs ("I can't parse
this kind of sentence — show me"), you supply one example-set, and the rung is added and covers all its instances.

The honest division of labor, now complete across JEP-363/364: **detection works, invention does not.** The system
knows the boundary of its competence and asks across it; it cannot cross it alone. That is exactly the right shape for
a teachable system under the no-LLM rule — and it directly answers the practical worry behind Michael's question: a
substrate that can't abstract *alone* is still highly usable if it can tell you precisely which abstraction it needs
next. Composes JEP-358 (detect-and-ask) + JEP-357 (induce-from-examples) at the construction-TYPE level. No transformer.
