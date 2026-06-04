# GEO-35 — Multi-hop grounded generation: geometric chaining feeds the generator

## Motivation
GEO-34 grounded single-fact generation. The full stack is multi-hop: a question whose answer requires
CHAINING facts the bare LLM does not know (private store). The geometric layer chains (person->team->city,
GEO-16/31), supplies the chain's facts to the generator, which produces the grounded answer. Tests reasoning
+ generation together, and that grounding supplies knowledge the LLM lacks.

## Pre-registration (locked BEFORE run)
- Private mini-KB: 8 employees, "<P> is on the <Team> team." + "The <Team> team is based in <City>." (private
  cities the LLM cannot know).
- Question: "Which city does <P> work in?" Answer = via P->Team->City (2 hops).
- (a) BARE LLM (no context): cannot know -> should be wrong/guess. accuracy on the private city.
- (b) GROUNDED: geometric layer chains P->Team->City, supplies both facts as context -> generator answers.
  accuracy on the private city.
- Bars: grounded >= 0.8 AND bare <= 0.2 (grounding supplies knowledge + correct chaining the LLM lacks).
  Report a couple of example generations.

PASS if grounded multi-hop generation works and the bare LLM cannot. NULL/PARTIAL otherwise.
