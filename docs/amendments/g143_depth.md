# G143 — Does DEPTH extend the no-LLM physical paradigm? (RBM vs DBN)

## Result (bars-and-stripes 5x5, 60% train)
| model | valid generated | novel-valid (held-out) |
|-------|-----------------|------------------------|
| 1-layer RBM | 0.97 | 21 |
| 2-layer DBN | 0.97 | 15 |

**VERDICT: NULL** — depth does not help on this task; the deeper model is no better (slightly worse on
novelty, likely from greedy layer-wise training loss).

## Finding — the no-LLM physical paradigm is BOUNDED; depth doesn't trivially extend it
The shallow RBM already captures the bars-and-stripes structure, and stacking adds nothing here. This
matches the historical record: deep belief networks were hard to train and were SUPERSEDED by transformers
for good reasons. So the honest headroom of the no-LLM physical path: it does the primitive AI capabilities
(optimize/recall/learn/generate, G138-142) on bounded/structured tasks, but does not obviously scale toward
open-domain/human-level capability by adding depth. The route that DID scale is the transformer/LLM, which
the charter excludes.

## The complete, honest picture (EQMOD + the buildable path)
- EQMOD physics: computationally empty; a no-LLM memory only (G131-G137).
- Buildable no-LLM physical-AI stack (Ising/Boltzmann family): optimize+recall+learn+generate, REAL but
  BOUNDED (toy-scale, doesn't extend by depth here) — G138-G143.
- Human-level no-LLM AI: not reachable by these pieces; that's the established LLM gap.
This is the evidence-based ceiling, delivered honestly with working references — the actionable truth.
