# Pattern — Auditing a headline POSITIVE before you trust it

A reusable research procedure, distilled from the G146→G149 arc (2026-06-05) that reversed the substrate
programme's lone positive claim. Pre-registration and matched negative controls protect you from a false
*negative being retried into a positive*; this pattern protects you from the opposite failure — a **false
positive you want to believe**. Use it on any result you are about to put in the README / summary / abstract.

## When to apply
A single experiment reports "X beats baseline B → genuine advantage." Before that becomes the headline:
the more a result flatters the hypothesis (especially "our thing finally wins"), the harder you audit it.

## The four moves (each killed a layer of the G145 claim)

1. **Re-implement and sanity-check the BASELINE, not just your method.** A baseline that scores worse than
   chance is a bug, not a weak competitor. (G146: the "greedy" baseline returned *negative* MAX-CUT cuts —
   it was sign-bugged, descending to MIN-cut. A correct greedy tied the hero method outright.) Concretely:
   compute the baseline's score on a trivial input where the optimum is known; if it loses to random, stop.

2. **Compare against the PROPER peer, not a strawman.** "Beats greedy" is not "beats the right algorithm."
   Name the textbook method your approach is really a member of (here: annealing → simulated annealing) and
   run it. (G146/G148: classical SA matched or beat the physical machine everywhere.)

3. **Separate YOUR thing from the established method it rides on.** If you report `max(yours, classical)`,
   you may be crediting your method for the classical method's win. Break them out. (G148: `max(OSC,SA)` beat
   greedy 15/15 — but separated, *SA* won and the oscillator merely tied greedy and lost to SA 15/15. The
   advantage was the algorithm's, not the substrate's — the whole question.)

4. **Kill the obvious objection with a matched-resource control, not a tuned one.** The first defense of a
   dying claim is "you under-resourced my method." Pre-empt it: scale the budget (same dynamics, only more of
   it) — a fairness control, NOT parameter tuning. If the gap persists, the weakness is fundamental. (G149:
   10× compute did not close the oscillator↔SA gap → not a budget artifact.)

## Discipline guards (so the audit stays honest)
- **Symmetric, pre-registered bars.** Write the COMPETITIVE / SUBOPTIMAL / INCONCLUSIVE thresholds before the
  run; design it so the *interesting* outcome (e.g. "sweet spot exists") is the one that fails your bar, not
  passes it — then a PASS can't be an artifact of a rigged test.
- **Doc is the pre-registration of record, not the code.** When a harness's printed verdict disagrees with the
  pre-registered doc definition (a classification-ordering bug bit G147), report the *doc's* outcome and flag
  the code defect — don't silently accept the misprint or silently flip to the flattering reading.
- **Scale-dependence is real.** A gap invisible at n=30 (trivially solvable) emerged by n=150 and crossed
  threshold by n=200. Test where the problem is actually hard, or you'll "refute" and "confirm" the same claim
  by choosing n.

## Outcome shape
The honest result is often a *refinement*, not a clean yes/no: "the advantage is real but belongs to the
classical algorithm; our physical realization confers none." That is more valuable than the over-claim it
replaces — and it is what survives scrutiny. Reversing your own headline is a feature of the process, not a
failure of it. See `g146`–`g149`, FINDINGS_SUMMARY Addendum 5.
</content>
