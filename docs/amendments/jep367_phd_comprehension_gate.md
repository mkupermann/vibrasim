# JEP-367 — The comprehension gate: can it answer English with no mistakes at PhD level?

## Motivation
Michael set a gate before any "generate functions for abstractions" work: **make sure the substrate understands
English and answers with no mistakes at PhD level.** This must be MEASURED, not asserted. I build a graded
comprehension benchmark across four difficulty tiers and report exactly where the substrate is error-free and where
mistakes begin — honestly, because the whole programme's value is an honest boundary. No transformer.

The honest hypothesis from JEP-362/365: the substrate can be error-free *within a taught, bounded domain using
supported reasoning operators*, but cannot be error-free on *open-domain* PhD English (which needs untaught world
knowledge and reasoning operators the substrate doesn't have). This experiment puts numbers on that.

## Method (the real deployed brain: SubstrateMemory + BrainQuery)
Teach a coherent, self-contained knowledge base (a small biology/physics domain). Then test four tiers:
- **T1 — taught recall:** direct facts taught verbatim (is-a, property, has-N).
- **T2 — composable reasoning:** multi-hop transitive is-a, inherited properties, defeasible exceptions (answers NOT
  stored directly, but derivable by supported operators over taught facts).
- **T3 — cross-relation reasoning:** abduction ("why?"), analogy, open-relation who/what — still over the taught
  domain, using supported operators.
- **T4 — open-domain PhD:** questions whose answers were never taught AND/OR require reasoning operators the substrate
  lacks (quantitative/mathematical inference, counterfactual, synthesis of untaught world knowledge). This is the
  "understand English in general at PhD level" tier.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: **T1–T3 near-perfect on the taught domain; T4 near-zero.** The substrate is error-free within a bounded
taught domain with supported operators, and fails open-domain PhD comprehension — so the gate "no mistakes at PhD
level (open-domain)" is NOT achievable under the no-LLM rule; a bounded, fully-taught PhD *subdomain* is the reachable
version.

- **T1 (taught recall):** accuracy ≥ 0.95, both seeds (0, 7).
- **T2 (composable reasoning):** accuracy ≥ 0.90, both seeds.
- **T3 (cross-relation reasoning):** accuracy ≥ 0.80, both seeds.
- **T4 (open-domain PhD):** accuracy < 0.20, both seeds (the wall). If T4 ≥ 0.20 it would be a surprise — report it.

Verdict logic: the honest answer to the gate is the per-tier profile. "No mistakes at PhD level" is achievable ONLY in
the sense of T1–T3 over a *taught bounded domain*; T4 (open-domain) is the wall. I predict exactly that profile. Either
way the numbers are the finding. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — the profile is exactly as predicted)
- **T1 taught recall: 1.0** — every directly-taught fact recalled (is-a, has-N legs, property). Both seeds.
- **T2 composable reasoning: 1.0** — multi-hop is-a (poodle→animal, 3 hops), inherited properties (poodle can bark;
  poodle is warmblooded via dog→mammal), defeasible exceptions (penguin can't fly though birds can), negation (whale
  is NOT a fish): all correct, none stored directly. Both seeds.
- **T3 cross-relation reasoning: 1.0** — abduction ("why cancer?" → smoking; "why flood?" → rain), open-relation
  ("who domesticated the dog?" → humans; "what did humans domesticate?" → dog). Both seeds.
- **T4 open-domain PhD: answer 0.0, hallucinate 0.0, abstain 1.0** — quicksort complexity, superconductivity cause,
  who-wrote-relativity, carbon's electrons, "what is entropy": the substrate produced the correct PhD answer for
  **none** (it was never taught them and lacks the operators), but it **abstained on every one (returned "I don't
  know") and hallucinated zero false answers.** Both seeds.

## Verdict: **PASS — the honest answer to the gate, with numbers**
Inside a **taught, bounded domain**, the substrate is **error-free** (T1–T3 = 1.0): it recalls taught facts, reasons
multi-hop with inheritance/exceptions/negation, and does abduction and open-relation Q&A — no mistakes. On
**open-domain PhD** questions (T4) it cannot answer (0.0), because the answers were never taught and the required
operators (quantitative, world-synthesis) aren't in the substrate. Crucially it **does not lie**: it abstains ("I
don't know") rather than hallucinating — zero false answers.

So "answer English with no mistakes at PhD level" resolves into two different claims:
1. **Achievable:** error-free Q&A *within a fully-taught bounded domain*, plus an honest "I don't know" outside it.
   The substrate already does this at 1.0 on the test domain, and *never* asserts a falsehood (a property LLMs lack).
2. **NOT achievable (no-LLM):** open-domain PhD competence — answering arbitrary PhD questions correctly — because
   that needs the whole untaught knowledge tail (JEP-362) and operators the substrate doesn't have.

The reachable form of Michael's gate is therefore: **pick a bounded PhD subdomain and teach it exhaustively** (cost
scales per construction/fact TYPE, JEP-365, with composition free, JEP-366) → error-free Q&A there, with honest
abstention outside. That is a real, buildable milestone; "no mistakes on all PhD English" is not. No transformer.
