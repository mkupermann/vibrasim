# Register programme summary — per-bond rest lengths as a matter memory
**Period: 2026-08-10 → 2026-08-12 · all experiments pre-registered, bars before data**

## The one-paragraph story

G154 (2026-06) closed recall-by-content as NEGATIVE and isolated the physical
cause: bridge tension had a single global equilibrium distance, so stored
patterns were not attractors. PRIM14 added the direct follow-on — each bond
freezes its formation-time distance as its own rest length (a strictly local
rule). Three diagnostics established the primitive honestly (D0 PARTIAL with a
contaminated probe, D1 NULL that FOUND the contamination — measurement-write
coupling — and D2 PASS with exact point predictions once the write channel was
closed). On top of it, the rest-length register: bits encoded as bond rest
lengths (6.5/10.5), retrieved from full scrambling by substrate physics alone
(G163 PASS, 144/144 bits, controls at chance) and retained through 50 000
ticks of real agitation (G164 PASS clean). Cue-based ASSOCIATION remains
NEGATIVE (G154, G161), and the capability is LEGACY-substrate-specific
(Flux lacks node kinematics and mechanical bonds — architectural note,
2026-08-12).

## Verdicts (chronological)

| ID | Question | Verdict | Key number |
|----|----------|---------|------------|
| G15F-1 | Flux dream consolidation | **NULL-T** | tagged engrams die in training |
| G15F-2 | Flux engram persistence map | **NULL** | nodes = 2–5 s recency echo |
| PRIM14-D0 | per-bond rest → attractor? | **PARTIAL** | R=0.357, probe contaminated |
| PRIM14-D1 | dynamics matrix | **NULL** | R-ceiling 0.5 = 2nd bond wrote probe geometry |
| PRIM14-D2 | pure attractor, channel closed | **PASS** | P→17.0 / C→19.0 exact, 3/3 seeds |
| G161 | recall on occupancy register | **NULL** | PRIM14 orthogonal there; basin failure |
| G162 | rest-length register v1 | **FAIL** | census gate: skip bonds (4+4=8 < 12) |
| G163 | rest-length register, corrected | **PASS** | 144/144 bits, controls at chance |
| G164 | retention under agitation | **PASS (clean)** | 1.000 @ 2k/10k/50k ticks, rebonding 0 |
| G165 | capacity 6/12/24 bits | **PASS** | ≥0.986 at all K; real strain at K=24 (min-NN 11.68 < 12) |
| G166 | retention at scale v1 | **INCONCLUSIVE** | control-arm artifact (undamped NEG drifted out); P-arms flawless |
| G167 | retention at scale, certified | **PASS (clean)** | 1.000 everywhere incl. K6 contrast; NEG 0.493 validly measured (sensitivity gate) |
| G168 | interference v1 | **UNCLASSIFIABLE** | bars gap: structural interference real, decode survived — one-axis scale |
| G169 | interference, two axes | **COUPLED-BUT-SEPARABLE** + MECHANISM-OPEN | R1 1.000 / R2 ≥ 0.917; LI-channel discovered (write-order interior vulnerability); point prediction falsified (0.375) |
| PRIM14F | portability to Flux | **not portable** (engineering note) | no node kinematics / spring bonds in Flux |

## What is established (honest scope)

- **Stored geometry is a true attractor** under per-bond rest lengths
  (D2: quantitative point predictions).
- **A written rest-length register re-expresses its content from physics**
  after full scrambling (G163) and **retains it under sustained perturbation**
  (G164: carriers displaced ~2 bit-distances; information lives in rest
  lengths, not positions).
- Engineered write, single-anchor retrieval, 6 bits, legacy substrate.
  NOT established: association from partial cues (twice NEGATIVE), capacity
  beyond 24 bits, interference, efficiency (Hopfield remains 546× cheaper —
  closed, G154), substrate independence (explicitly absent).

## The two traps this arc found (load-bearing for any successor)

1. **Measurement-write coupling (D1):** formation-frozen rest lengths store
   ANY geometry held long enough for bond formation — including the probe's.
   Every read-out must close the write channel (valence saturation or
   formation freeze) and verify it by bond census.
2. **Encoding must respect the measured formation window (G162):** bonds form
   below distance 12 (sharp cutoff at r_2). All non-consecutive pairwise
   distances must exceed it, or the write inscribes a different graph than
   registered. The census gate caught this; the number 0.986 measured on the
   broken topology has NO evidential status.

## Where the detail lives

Amendments: `docs/amendments/bp_prim14_*.md`, `g161_*.md` – `g164_*.md`,
`g15f_*.md` · raw data: `archive/run-logs/{prim14,g161,g162,g163,g164,g15f,g15f2}` ·
diary: LOGBOOK.md 2026-08-10 … 2026-08-12 · pattern doc:
`docs/patterns/rest_length_register.md`.
