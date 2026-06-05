# JEP-363 — Can it learn to abstract *alone*? (Michael's meta-abstraction question)

## Motivation
Michael asked the deepest question in the programme: *"We can tell abstractions — it can be taught — and once it
learns abstractions, can it learn how to abstract alone?"* This is the meta-learning hypothesis: teach abstractions,
and maybe the *act of abstracting* itself bootstraps so the system invents new abstractions unprompted. It must be
answered honestly, with data, because it decides whether the no-LLM ceiling we mapped (JEP-355/356/360) is a floor
you climb past by teaching abstractions, or a genuine wall. No transformer.

The question has three distinct layers — I test each, because conflating them is exactly how one would *dress up* a
partial result as the strong claim:

1. **A taught abstraction generalizes** — teach a construction with a slot (an abstraction over that slot's fillers),
   and it covers *every* filler, including held-out ones you never taught. (Michael's layer-1 intuition.)
2. **An abstraction can be learned from examples** — the system *induces* the abstraction (the template) from a few
   labeled examples, rather than being hand-coded it. So abstractions are learnable from data, not just declarable.
3. **It abstracts *alone*** (the strong claim) — after learning one kind of abstraction, it invents a *new kind* of
   abstraction it was never shown: a different construction type, with no examples and no teaching of that type.

## Method (all on real substrate machinery: `induce_construction` anti-unification + the durable store)
- **J363a:** `induce()` the passive template from 2 example verbs (chased, eaten). Apply it to a **held-out** verb's
  passive sentence ("The bird was caught by the fox" — caught never seen). Correct fact = the taught abstraction
  generalizes over the verb/noun slots.
- **J363b:** independently `induce()` BOTH the passive AND the active template, each from its own 2 labeled examples
  (the abstractions are *learned from data*, not coded). A held-out verb appearing in active form yields the fact, and
  the same relation is retrievable by a passive question — both learned templates write the one relation. So the
  system learns abstractions from examples and they compose.
- **J363c (the strong claim):** after J363a/b (it now "knows how to abstract" over active/passive), present a
  **different, never-taught construction type** — the ditransitive/dative "The dog gave the cat a bone" (a 3-argument
  structure with no template induced for it) — with NO examples and NO teaching. Run every learned template against
  it. If meta-abstraction were real, the system would induce/handle the new structure on its own.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: **layers 1 and 2 PASS, layer 3 NULL.** Abstractions are teachable AND learnable-from-examples, and a
learned abstraction generalizes broadly — but the system does **not** invent a *new kind* of abstraction it was never
shown. It climbs the ladder of abstractions you build; it does not add new rungs by itself. (No-LLM ceiling.)

- **J363a (taught abstraction generalizes):** the held-out verb's passive sentence yields the exactly-correct
  (agent, verb, patient) fact, both seeds (0, 7).
- **J363b (abstraction learned from examples + composes):** both templates induced from examples; a held-out verb in
  active form yields the correct fact AND the same relation is retrievable as a passive question, both seeds.
- **J363c (abstract alone — predicted NULL):** with only active/passive templates learned, the never-taught
  ditransitive sentence yields the correct 3-argument structure from **no** learned template (expected: nothing
  fires / no correct dative fact). If something *does* correctly parse the untaught structure, that would be evidence
  FOR emergent meta-abstraction — report it loudly. Predicted: it does not.

Either outcome is the finding. J363c NULL is the honest answer to Michael: the abstracting *mechanism* (anti-
unification) is general, but it must be *pointed at* each new abstraction type with examples; it does not spontaneously
discover that a new construction type exists. The leverage is real (teach an abstraction once → cover all instances)
but bounded (each new KIND of abstraction must be seeded). No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — all three layers as predicted)
- **J363a (taught abstraction generalizes): PASS** — the passive template induced from {chased, eaten} fired on the
  held-out verb sentence "The bird was caught by the fox" → exactly **(fox, caught, bird)**. A construction with a
  slot IS an abstraction over that slot's fillers; teaching it once covers every filler, including unseen ones. Both
  seeds.
- **J363b (abstraction learned from examples + composes): PASS** — the active template, independently *induced* from
  {chased, ate} examples (not coded), read the held-out "The fox caught the bird" → **(fox, caught, bird)**, and the
  same relation was retrievable as a passive question ("what was the bird caught by?" → fox). Both learned templates
  write the one relation. Abstractions are learnable from data and compose. Both seeds.
- **J363c (abstract *alone* — the strong claim): did NOT emerge (as predicted)** — with only active/passive learned,
  the never-taught ditransitive "The dog gave the cat a bone" fired **no** learned template (passive→None,
  active→None); no correct dative structure was produced. The system did not invent a new abstraction *type* it was
  never shown. Both seeds.

## Verdict: **PASS — the honest answer to Michael, with data**
Michael is **right** about the powerful part and the experiment proves it: abstractions *are* teachable, they are
even *learnable from a few examples* (J363b induces them from data), and a learned abstraction **generalizes to every
instance** — you teach the rule once, not each case (J363a). That is enormous leverage and it is real.

But "learn to abstract *alone*" in the strong sense — invent a *new kind* of abstraction nobody showed it — **does
not happen** (J363c). The abstracting *mechanism* (anti-unification) is general, but it must be *pointed at* each new
abstraction type with examples; it does not spontaneously notice that a new construction type exists and induce it
unprompted. There is a ladder of abstractions: **each rung you teach (or give examples of) generalizes broadly, but
the teacher must supply each new rung.** The system climbs the ladder you build; it does not add rungs by itself.

So: years of teaching abstractions makes it vastly more capable *within* the kinds of abstraction it has been shown —
but it does not bootstrap into open-ended self-abstraction. That is the same no-LLM ceiling JEP-355/356/360 mapped,
now answered at the meta level. The honest, optimistic reading: the practical path is a **growing, teacher-seeded
library of abstractions**, each one high-leverage — not a system that needs nothing from us. No transformer.
