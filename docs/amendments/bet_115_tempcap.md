# BET-115 — Temporal Capacity (max sequences vs N)

Pre-registered: 2026-05-31 (BEFORE the run). BET-114 showed 3 sequences (12
patterns) interfere at N=120 — exactly the static-capacity edge. BET-115 measures
the temporal capacity directly: for each N, the largest number of length-4
sequences recallable with min per-step overlap ≥ 0.90.

## Method
N ∈ {120,160,200,240,280}. For each, sweep S=1,2,3,… length-4 sequences; capacity
= largest S with min per-step recall overlap ≥ 0.90. Energy substrate, train_sequence.

## Acceptance bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T115a | Stores multiple | max-sequences ≥ 2 at every N |
| T115b | Monotonic | max-sequences non-decreasing in N |
| T115c | Scales | max-sequences at largest N ≥ 2× at smallest N |

PASS = T115a–c. PASS confirms BET-114 was a capacity edge and that temporal
capacity scales with N (total stored patterns ≈ static 0.1·N). Plot included.

## RESULT (2026-05-31): NULL — low temporal capacity; concurrent sequences interfere

max-sequences per N = [1,2,1,2,2] for N=120..280 — only ~1-2 length-4 sequences,
NOT scaling with N (and noisy/non-monotonic). Yet BET-113 stored a SINGLE length-8
sequence (8 patterns) perfectly. So the bottleneck is not pattern count or
attractor capacity — it is INTERFERENCE between CONCURRENT sequences in the simple
Hebbian transition matrix T: a shared T superimposes multiple chains and clean-up
disambiguates wrongly.

T115a x, T115b x, T115c ok. Honest NULL: the transition WRITE (Hebbian outer
product) is the weak link, and multiple sequences need CONTEXT to disambiguate.
BET-116: context-gated transitions (a hidden context state tagging the active
sequence) — the move toward hierarchical predictive coding.
