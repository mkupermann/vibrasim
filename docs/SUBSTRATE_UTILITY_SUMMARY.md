# Substrate computational utility — the evidence-based answer (G133–G135)

## The question
Across several user prompts: is there a task/mix where the PHYSICAL substrate genuinely works better or
faster than ordinary methods (so it earns a place in an AI system, with ML used only elsewhere)?

## What was tested (pre-registered, both seeds, controls)
| niche | experiment | result |
|-------|-----------|--------|
| Nonlinear feature provider (algebra) | G133 — physical state as reservoir vs abstract ELM | **NULL** — physical R2 = −0.49/−0.40 (worse than the mean); ELM wins |
| Nonlinear feature provider (geometry) | G134 — proximity detection, balanced | **NULL** — physical weak+inconsistent (+0.04 / −0.13); trivial ELM wins both |
| Physical optimizer (layout) | G135 — relax clustered atoms to even spacing | **NULL** — atoms collapse, no relaxation |

## The honest conclusion
In THIS simulation the substrate has **no demonstrated computational advantage** — not as a feature map,
not for geometry, not as an analog optimizer. It does not beat a trivial random-feature baseline anywhere,
and being a serial Python physics sim, it makes nothing FASTER (numpy always wins on wall-clock).

The substrate's genuine, demonstrated value is exactly two things, and no more:
1. **MEMORY + I/O** — matter-position storage (the session breakthrough): a real no-LLM data store, used
   BY classical ML for everything cognitive.
2. **A conceptual model** of physical/analog spatial computation — valuable as theory and as a HARDWARE
   design target. The "parallel analog geometry is free/fast" advantage is REAL in built hardware and
   UNREACHABLE in simulation.

## Implication for "human-AI without LLM"
The cognition (EQMOD-2: VSA + reservoir/ELM + RLS) is classical ML that runs on an abstract random matrix
— it does NOT use the physics (G133; world/reservoir.py is `rng.normal`). So the working no-LLM language
behavior is established statistical ML; the substrate's only honest role in it is as the memory store.
A "mix where the substrate carries real compute" was searched for with controls and not found here; the
path that could realize it is analog HARDWARE, a different undertaking than this simulator.
