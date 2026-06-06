# Pattern 01 — Three-way triage before you believe a null result

**Discovered:** 2026-05-30, during BET-090 (anchored selective memory).
**Status:** empirical.
**Substrate evidence:** BET-090 ran an intervention (velocity-anchoring of
mature lattice sites) that did not move the outcome (selective memory still
absent, `frac_strong=0.00`). The naive read was "the mechanism is inert."
Instrumentation showed the opposite: anchoring *fired* (1027 atoms entered
maturity tracking) and *worked* (frozen atoms 0.0144 vs 0.0804 mean speed,
5.6× slower) — but a different quantity bound the result (atom lifetime ~13 s
< the 50 s maturity gate). The verdict flipped from "broken mechanism" to
"sound mechanism, wrong binding constraint" only because the intervention was
instrumented, not just the outcome. See docs/amendments/bet_090_anchored_memory.md
and the LOGBOOK entry of the same date.

## The mechanism

When an intervention fails to change an outcome, there are three distinct
causes, and they demand opposite next moves:

1. **It never fired.** The code path / treatment didn't actually engage
   (a gate never opened, a config knob defaulted to off, a guard returned
   early). Fix: make it fire.
2. **It fired but was mechanically ineffective.** It engaged but didn't do
   the thing it claims to do. Fix: fix the mechanism.
3. **It fired and worked, but a different constraint binds.** It did exactly
   what it claims, and that simply wasn't the limiting factor. Fix: find and
   attack the real binding constraint — leave this mechanism alone.

The error is collapsing all three into "it didn't work, tune it." Cases 1 and
2 look identical from the outcome alone, and case 3 is invisible from the
outcome — yet only case 3's correct move is "stop touching this knob." You
cannot distinguish them by staring at the result. You distinguish them by
instrumenting the *intervention itself*: did it engage, and did engaging
produce its local effect, independent of whether the global outcome moved.

## Why it works

Outcome metrics are downstream of a whole causal chain; a flat outcome is
consistent with a break anywhere along it. Measuring the intervention's local
effect (here: did frozen atoms actually slow down?) cuts the chain at the
treatment and isolates which link failed. The decisive number is almost never
the headline metric — it's the cheap local probe that says "the treatment did
its job," which then *forces* the conclusion that the bottleneck is elsewhere.

## Reusable form

Before concluding from a null:

1. **Probe firing.** Add a counter: how many times did the treatment actually
   engage? Zero → case 1, you have a wiring bug, not a finding.
2. **Probe local effect.** Measure the quantity the treatment directly acts on,
   in treated vs untreated units. No local effect → case 2, mechanism is broken.
3. **Local effect present, global outcome flat → case 3.** Now hunt the binding
   constraint: what other quantity, if held fixed, would have let the outcome
   move? Name it, measure it, and check it against the treatment's timescale /
   magnitude. (Here: site *lifetime* 13 s vs the 50 s the treatment needed to
   even begin — the treatment was outrun before it could matter.)
4. **Only then choose the next intervention** — and it targets the binding
   constraint, not the knob that already works.

Anti-pattern: tuning the treatment's parameter to force the outcome. In case 3
this both fakes a result and leaves the real constraint unfixed. (BET-090
explicitly refused to drop `anchor_age` from 50 s to 13 s for exactly this
reason — a shorter gate would catch more atoms but still can't host memory on
13 s-lived sites.)

## Real-world / business mapping

- **A/B test shows no lift from a new feature.** Before killing it: did users
  actually reach it (firing)? Of those who did, did the proximal metric it
  targets move (local effect)? If yes but revenue is flat, the bottleneck is
  downstream (pricing, checkout) — shipping more of this feature won't help.
- **A latency optimization doesn't speed up the request.** Profile confirms the
  optimized span got 5× faster (local effect ✓) but p99 is unchanged → a
  different span dominates. Optimizing the first one further is wasted.
- **An LLM pipeline change (better retrieval) doesn't improve answers.** Check:
  is the retrieved context actually reaching the model, and is it more
  relevant (local effect)? If yes but answers are flat, the generation step or
  the eval is the binding constraint, not retrieval.

In each, the failure mode is treating a flat top-line as a verdict on the
intervention, when the intervention may be working perfectly on a non-binding
link.

## Failure modes pre-registered

- This pattern does not tell you *what* the binding constraint is — only that
  you must go find it. Step 3 is still real work.
- The local-effect probe must measure the treatment's *direct* action, not a
  proxy one step removed, or it inherits the same ambiguity as the outcome.
- Cheap to over-apply: for a treatment that obviously fired and obviously
  works, skip straight to step 3. The triage earns its cost only when the null
  is surprising.

## Empirical evidence

BET-090 (2026-05-30). Outcome probe: `frac_strong=0.00` both arms (looked like
case 1/2). Firing probe: 1027 distinct level-4 atoms entered maturity tracking.
Local-effect probe: frozen mean |vel| 0.0144 vs unfrozen 0.0804 (5.6×, case 3
confirmed — mechanism sound). Binding constraint identified: mean level-4 atom
lifetime ~13 s vs 50 s maturity gate. Verdict recorded NULL with the constraint
named, next amendment redirected from "anchoring knob" to "node persistence."
