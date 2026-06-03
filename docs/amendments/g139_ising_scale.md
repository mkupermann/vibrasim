# G139 — Oscillator-Ising scaling (what the recommended hardware can do at size)

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
