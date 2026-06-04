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

## Result — PASS (full reasoning+generation stack)
| | result |
|--|--------|
| bare-LLM city accuracy | 0.00 (guesses "New York City" — no private knowledge) |
| grounded multi-hop accuracy | **1.00** |
| examples | bare "New York City" -> grounded "Alice works in Zogby." / "Bob works in Quenville." |

**VERDICT: PASS.** The geometric layer chains private facts (person->team->city) and supplies them to the
0.5B generator, which answers correctly (1.00), while the bare LLM — lacking the private knowledge —
confabulates a generic city (0.00). The complete stack works on the PC: geometric multi-hop reasoning over a
private, updatable store -> grounded generation, producing correct answers the LLM alone cannot, without
hallucination. This is the programme's capstone: a grounded reasoning+QA assistant (tools/grounded_qa.py)
that reasons over your own facts and grounds an LLM's generation in them.
