# Register programme summary — per-bond rest lengths as a matter memory
**Period: 2026-08-10 → 2026-08-13 · all experiments pre-registered, bars before data · LINE CLOSED 2026-08-13**

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
ticks of real agitation (G164 PASS clean). The association question closed by
CHARACTERIZATION (G171–G173): content association through an engineered
cross-structure exists exactly at FULL anchoring (every carrier cross-bonded:
1.000, four independent replications); below full anchoring the channel
carries span information only — a STEP FUNCTION, not a graded channel. Scope
of that statement (programme decision 2026-08-13): it holds for centered
chains with span-preserving contacts under the spacing encoding; an encoding
or geometry that couples a second contact variable to content (e.g. anchor
offset as a function of the bits) reopens the class — logged below as a
design candidate, not run. The capability is LEGACY-substrate-specific (Flux
lacks node kinematics and mechanical bonds — architectural note, 2026-08-12).

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
| G170 | LI-channel mechanism | **H-INDEX** | interior loss is an allocation-order artifact of the pair-scan, not physics |
| G171 | association bandwidth v1 | **K12 VALID 1.000 / K2,K6 census-INVALID** | standalone finding: cross-writability is pattern-dependent under end-anchoring |
| G172 | bandwidth, clean geometry | **FAIL (gate correct)** | span-matched decoy spec impossible at 1-bit chains; Stage-1 writability PASS stands |
| G173 | bandwidth, defined specificity | **INCONCLUSIVE → arc resolved** | decoy physically inert (ends fixed); sub-full channel span-only; K12 1.000 ×4 — step function |

## What is established (honest scope)

- **Stored geometry is a true attractor** under per-bond rest lengths
  (D2: quantitative point predictions).
- **A written rest-length register re-expresses its content from physics**
  after full scrambling (G163) and **retains it under sustained perturbation**
  (G164: carriers displaced ~2 bit-distances; information lives in rest
  lengths, not positions).
- **Association is a step function of anchoring** (G171–G173, scoped as
  above): full anchoring → perfect content reconstruction (1.000, ×4);
  partial anchoring → span-only. The observed anchor-distance order
  (d0 0.635 > d1 0.542, G173) is explicitly a GEOMETRY signal, not a content
  signal — its decoy reproduced it identically.
- Engineered write, single-anchor retrieval, 6 bits, legacy substrate.
  NOT established: graded association below full anchoring (characterized
  ABSENT under the spacing encoding), retention of full-anchoring
  associations (untested; note: a PASS would sit near the already-certified
  G164/G167 retention — degeneracy risk recorded), capacity beyond 24 bits,
  efficiency (Hopfield remains 546× cheaper — closed, G154), substrate
  independence (explicitly absent).

## The traps this arc found (load-bearing for any successor)

1. **Measurement-write coupling (D1):** formation-frozen rest lengths store
   ANY geometry held long enough for bond formation — including the probe's.
   Every read-out must close the write channel (valence saturation or
   formation freeze) and verify it by bond census.
2. **Encoding must respect the measured formation window (G162):** bonds form
   below distance 12 (sharp cutoff at r_2). All non-consecutive pairwise
   distances must exceed it, or the write inscribes a different graph than
   registered. The census gate caught this; the number 0.986 measured on the
   broken topology has NO evidential status.
3. **Allocation-order trap (G170):** the fixed triu pair-scan order of bond
   formation decides valence races — which of two competing structures loses
   a bond is an ARTIFACT of allocation order, not physics. Any multi-register
   result must rule this channel out before claiming interference physics.
4. **Pattern-dependent writability (G171):** under end-anchoring, stored
   content and connectivity are COUPLED — chain-end offsets grow with chain
   length and decide whether a cross-bond can form at all. Contact geometry
   must be validated pattern-independently (Stage-1 gate) before measuring.
5. **Control-spec non-degeneracy and measurement coupling (G172/G173):** a
   control spec must be proven satisfiable over its domain (span-matching is
   impossible at 1-bit chains), and a decoy must differ in a variable the
   MEASUREMENT is physically coupled to (span-preserving permutations of
   centered chains leave every cross rest identical — structurally inert).
   Walk the measurement coupling, not just combinatorial existence, BEFORE
   the run. Three consecutive spec degenerations forced this rule; it is now
   a standing pre-reg requirement for this programme.

## Design candidate (logged, not run)

**Content-coupled anchoring** (from the G173 review, 2026-08-13): an encoding
where anchor geometry is a FUNCTION of the stored bits (e.g. chain offset
derived from content) would couple content to the cross-structure below full
anchoring and could reopen graded association. This is a new register design,
not a decoy for the closed claim. Unscheduled.

## Where the detail lives

Amendments: `docs/amendments/bp_prim14_*.md`, `g161_*.md` – `g173_*.md`,
`g15f_*.md` · raw data: `archive/run-logs/{prim14,g161…g173,g15f,g15f2}` ·
diary: LOGBOOK.md 2026-08-10 … 2026-08-13 · pattern docs:
`docs/patterns/rest_length_register.md`,
`docs/patterns/control_spec_nondegeneracy.md`.
