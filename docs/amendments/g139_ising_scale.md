# G139 — Oscillator-Ising scaling (what the recommended hardware can do at size)

> ⚠️ **Tempered by G146–G149 (2026-06-05).** This doc concludes the oscillator is "a genuinely useful analog
> optimizer — build this." A later rigorous audit found the oscillator merely TIES a *correct* multi-restart
> greedy and LOSES to classical simulated annealing at every scale (n=200–360), even at 10× compute. So the
> genuine optimization edge belongs to the **classical SA algorithm**, not the oscillator/vibrations machine.
> "Matches/slightly beats greedy" here is consistent with that (oscillator ≈ correct greedy); the
> "build this hardware" conclusion does not survive — build SA. See `g146`–`g149` + FINDINGS_SUMMARY Addendum 5.

## Result (random graphs, best of 8 anneals; UB = total edge weight, loose)
| n | oscillator/UB | greedy/UB |
|---|---------------|-----------|
| 10 | 0.82 | 0.82 |
| 20 | 0.76 | 0.73 |
| 40 | 0.69 | 0.66 |
| 80 | 0.63 | 0.60 |

**Finding:** the oscillator-Ising machine matches or slightly beats a multi-pass greedy at every size; the
declining ratios reflect the LOOSE upper bound (greedy declines the same way), not the machine degrading.
So the recommended hardware paradigm SCALES and is competitive with a good heuristic — a genuinely useful
analog optimizer. Established method; numpy reference (real hardware runs the relaxation in parallel).
Surfaced as docs/patterns/oscillator_ising_computing.md. The honest hardware answer: build this, not EQMOD.
