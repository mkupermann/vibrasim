# G51 — Multiple proto-cells: does a larger substrate form a POPULATION of membranes?

Pre-registered: 2026-06-02 (BEFORE the run). The proto-cell single-membrane thread is
consolidated (G30→G50). Fresh structural question, building on the PROVEN membrane formation
(G30) rather than channel extensions (all NULL): in a larger box at the same density, does the
substrate spontaneously form MULTIPLE distinct closed membranes — a population of proto-cells —
or does it coalesce into a single shell regardless of scale?

## Method
G30 rich-substrate config, scaled to a larger box (33³ vs 22³, ~3.4× volume) with proportionally
scaled vibration generation and node/vibration capacity. Run formation (300 ticks). Enumerate ALL
bridged atom components; for each with ≥ 30 atoms, fit a sphere and count those that are
shell-like (σ_r/R < 0.4). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G51a | Membranes form | ≥ 1 large shell-like component (≥30 atoms, σ_r/R<0.4), both seeds |
| G51b | MULTIPLE (a population) | ≥ 2 large shell-like components, both seeds |

PASS = G51a–b → the substrate forms a POPULATION of distinct proto-cells at scale (a meaningful
new structural result: not just one membrane but several independent ones). NULL: if only one
large shell forms (G51b fails), the substrate coalesces to a single membrane regardless of box
size — an honest finding about its self-organization (single minimal surface, not a population).
No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL/partial — coalesces to ONE scale-invariant membrane, not a population

| seed | shell-like components |
|------|------------------------|
| 42 | 1 — (372 atoms, R 16.5, σ/R 0.272) |
| 7 | 1 — (385 atoms, R 16.9, σ/R 0.261) |

G51a ✓, G51b ✗ → **NULL on the population hypothesis.** In a 3.4× box the substrate formed ONE
large shell (372/385 atoms), not several. 

**Notable positive inside the NULL — scale-invariant membrane formation.** The single shell
scales cleanly: 372 atoms at box 33³ with σ/R 0.27, the same shell quality as 110 atoms at box
22³ (G30, σ/R 0.25). A bigger substrate makes a BIGGER membrane, not multiple — the curvature +
bridge-tension + edge-closure machinery drives toward a single closed minimal surface.

**Honest finding:** the substrate self-organizes to ONE membrane regardless of scale (coalescence,
not a population). Combined with G45–G50, the structural extensions are exhausted: the substrate's
ceiling is a single persistent, self-regulating, scale-invariant membrane. See FINDINGS_SUMMARY.md.
