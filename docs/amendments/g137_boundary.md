# G137 — Mapping the no-LLM stack's competence boundary (linear vs nonlinear composition)

## What was tested + the two honest corrections it produced
Goal: find exactly where the EQMOD-2 stack's "systematic generalization" holds vs collapses to bigram.

**v1 (rule = f(verb)) — invalid task.** obj depended only on the previous word (verb), so a BIGRAM
captures it trivially (1.00 at noise=0). Held-out (subj,verb) "generalization" on such a task proves
NOTHING beyond bigram. (Lesson: BET-style "held-out combo" claims must use a target that depends on a
COMBINATION, or a bigram baseline already wins.)

**v2 (rule = (a[subj]+b[verb]) mod N) — compositional but NONLINEAR.** Now the target needs BOTH symbols
(bigram fails), but the modular sum is NOT linearly separable. Result (held-out novel combos, chance=0.17):
| noise | stack | bigram |
|-------|-------|--------|
| 0.00  | 0.12  | 0.10   |
| 0.25  | 0.15  | 0.10   |
| 0.50  | 0.10  | 0.17   |
The stack is at CHANCE even on the clean (noise=0) rule. **VERDICT: NULL.**

## Finding — the niche is LINEAR-composable relations only (refines BET-130, doesn't refute it)
This does NOT contradict BET-130's 90.6%: BET-130's task is v[i] > v[j], a target LINEAR in per-symbol
values (a threshold on v[i]−v[j]), which the analog-VSA code makes linearly readable — so a single linear
RLS readout generalizes. G137's modular-sum target is NONLINEAR (wraps), so the same linear readout cannot
generalize it (chance). The honest boundary of the no-LLM stack's "systematic generalization":
- **Works:** relations that are LINEAR in per-symbol features (comparison, sums-without-wrap, weighted
  votes) — BET-130/132.
- **Fails:** NONLINEAR compositions (modular, XOR-like, conjunctions) — G137 chance; and open natural
  language — bigram-level (G136). The reservoir's tanh features don't rescue it here (the readout is the
  bottleneck, and held-out NONLINEAR combinations need nonlinear features the random map doesn't align).

## Net effect on the strategic answer
The realizable no-LLM niche is narrower than "structured tasks": it is **linearly-composable structured
relations** + retrieval + rule-based synthesis. Nonlinear composition and open language are out of reach
(linear-readout ceiling). This sharpens, with evidence, exactly what the no-LLM toolkit can and cannot do.
