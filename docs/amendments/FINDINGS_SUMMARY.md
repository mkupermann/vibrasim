# EQMOD Findings Summary — what the substrate CAN and CANNOT do

Top-level synthesis of the substrate exploration (BET-086→G51), written 2026-06-02. Ties the two
major threads — cognition/memory and proto-cell structure — into the project's overall result.
The charter's goal is "developing a deadlock-breaking process, not necessarily succeeding"; this
document is that deliverable: the substrate's capabilities and ceilings, mapped and bounded.

## The bottom-up chain that WORKS (robust positives)

vibrations → electrons → atoms → molecules → bridges → **a persistent, self-regulating membrane
(a proto-cell)**. Every step is emergent from substrate primitives; the only engineered piece is
the §4.8 channel/port boundary (charter-sanctioned). No LLM, no transformer.

| Result | What | Status |
|--------|------|--------|
| G27 | Widening the frequency rule → rich chemistry (200 atoms, 600+ molecules) | PASS |
| G28 | Element-count ceiling lifted (100–313-atom bridged structures) | finding |
| G30 | Large closed membrane composes (~110 atoms, shell-like, persists) | PASS |
| G32 | Selective permeability in the engine (atom-proximity reflector, clean seal) | PASS |
| G43 | Proto-cell homeostasis (maintained interior–exterior gradient) | PASS |
| G44 | Active regulation to set-point after perturbation | PASS |
| G51 | Membrane formation is scale-invariant (372 atoms at 3.4× box, same σ/R) | partial+ |

**The substrate builds a proto-cell with FUNCTION**: forms → seals selectively → maintains an
interior environment → regulates back to set-point after a disturbance. A genuine bottom-up
cell precursor.

## The ceilings (robust, exhaustively-mapped NEGATIVES)

### 1. No selective persistent memory — the deadlock, mapped across ALL channels
Across ~30 experiments (BET-089→102, G33→G39): selective persistent CONTENT memory does not
emerge. The signal that WRITES a memory is the signal that LEAKS it, on EVERY coupling channel —
vibration broadcast (BET-099–102, G33–G39), neuron charge field (BET-103–104), and bridge graph
(BET-105–106). Containment strong enough to stop the leak also starves the write (monotonic
trade-off, no win cell). Set-based readout proved the engram is PERMANENT (so it is not a
persistence/turnover problem) — it is a write=leak connectivity problem. See
MEMORY_PROGRAMME_SUMMARY.

### 2. No metabolism, no self-repair, no population — the proto-cell's structural ceiling
Across G45→G51 (seven experiments): the membrane is persistent, self-regulating, but STATIC.
- No channel-coupled synthesis / metabolism (G45, G49, G50): interior assembly (~16 atoms) is
  fixed by local geometry, independent of the channel or active uptake.
- No self-repair (G46–G48): a wounded shell does not heal; cause is positional rigidity + no
  wound-targeting (NOT valence commitment — G48 falsified that hypothesis).
- No population (G51): the substrate coalesces to ONE scale-invariant membrane, not several.
See PROTOCELL_SUMMARY.

## The unifying principle
Both ceilings are the same structural fact seen twice: **the substrate is a strongly-coupled,
positionally-rigid connected medium.** That connectivity is why memory leaks (write=broadcast=leak
across channels) AND why the membrane is one rigid coalesced surface that regulates but does not
metabolize, heal, or divide. The substrate excels at CONTAINMENT and REGULATION (its connectivity
working FOR you) and fails at SELECTIVE LOCALIZATION and FLUID REORGANIZATION (its connectivity
and rigidity working against you). Build functions on the former; the latter need a different
medium or new primitives.

## Reusable mechanisms surfaced (docs/patterns/)
- atom_proximity_reflector — gate off the real structure, not a fitted proxy.
- engineered_port_wall — specular reflection for robust activity containment (mode matters).
- protocell_homeostasis — emergent membrane + selective channel = regulated interior.
- (plus the earlier 01-which-constraint-binds, 02-write-contaminate-tension.)

## Honest process notes
Pre-registration held throughout (bars locked before every run; NULL a valid verdict; no post-hoc
tuning). Two of my own mechanistic hypotheses were FALSIFIED by confirmatory tests and corrected
in writing (G33 "turnover" → readout artifact; G47 "persistence⊥repair" → rigidity, via G48). A
single-seed apparent success (G37) was caught by a pre-registered multi-seed replication (G38) and
retracted. Honesty over consistency, throughout.

## What would move the needle next (requires new primitives / a decision, not a regime knob)
- Selective memory: a write channel DECOUPLED from broadcast (directional, non-leaking) — not
  achievable with current primitives (BET-105 tried bridge-graph write; it self-ignites).
- Metabolism/repair/division: a FLUID membrane (atoms that can migrate and re-bond). G52 pinned
  the rigidity precisely to PERMANENT BONDS (not stationarity). G53 BUILT the needle-mover
  (`bond_turnover_rate`: spontaneous bond break + reform) and showed the rigidity ceiling is
  BREAKABLE: with turnover the membrane partially self-repairs (37% of a wound healed at rate 0.1,
  seed 42) WHILE staying fully intact (persist 1.00 — no fluidity/stability trade-off at ≤0.3).
  The healing is not yet robust (seed-dependent, sub-threshold), but the mechanism is right. G54
  strengthened it (window 500, edge-closure 2.0): at turnover 0.15 healing rose to 0.49 (seed 42) /
  0.26 (seed 7), monotonically improving, membrane fully stable — robust ≥0.3-both-seeds repair is
  at the threshold (seed 7 0.04 short). Stopped tuning there (chasing one seed's gap is bar-
  optimization, not science). **Established: the rigidity ceiling is a breakable, tunable frontier,
  not a hard wall** — bond turnover gives fluid partial self-repair (up to 49%) with no fluidity/
  stability trade-off. G55 then showed the fluid membrane is SIZE-HOMEOSTATIC (holds a set-point
  size — neither grows ≥1.2× nor dissolves), a stable dynamic structure; it does NOT grow or
  divide (those need a different driver). Net: bond turnover yields a fluid, partially self-
  repairing, size-homeostatic membrane — a richer dynamic cell precursor, still short of growth/
  division.

## ADDENDUM (2026-06-02) — the substrate's positive COMPUTATIONAL capability is ANALOG SIGNAL PROCESSING

Beyond structure/homeostasis, the proto-cell is a fully characterized, TUNABLE first-order linear
analog element (G44 regulation, G58 step response, G59 DC gain, G60 low-pass frequency response,
G61 cutoff ∝ membrane radius, G62 ~9× denoising — all PASS, both seeds). docs/patterns/
protocell_controller.md. The honest framing of the substrate's computational value: it CANNOT do
digital/selective MEMORY (write=leak deadlock, all channels) but it CAN do ANALOG SIGNAL PROCESSING
(tunable low-pass filtering, disturbance rejection, denoising) — because these use the channel's
selective EFFLUX/containment (the substrate's strength), not a selective write (its deadlock).
The substrate is an analog signal processor, not a digital memory.

## ADDENDUM 2 (2026-06-03) — directional/self-limiting write evolution: EXHAUSTED (refractory 0.44 high-water mark)

Pursued the user-requested "directional self-limiting write" to break the memory deadlock, with NEW
mechanisms: local emission (G64), k-WTA lateral inhibition (G65), refractory (G66), high threshold
(G67), combos (G68), leaky write (G69), consolidation + weak leak (G70), fast-lock (G71), sleep-sweep
(G72). ALL NULL on selective persistent recall. Findings:
- **Refractory firing is the one real advance** — t_refractory=0.5 gives a SELECTIVE WRITE (stim-frac
  0.83) and recall 0.44, the best ever (vs ~0.3 prior). Directional firing (no immediate re-fire) is
  genuinely useful.
- **But the deadlock holds at the root:** G72 shows CONTROL bridges consolidate too (9 locked in the
  uniform arm). The control region is never blank — it co-fires and consolidates indistinguishably
  from stim, because the substrate is HOMOGENEOUSLY ACTIVE. No leak/threshold/consolidation/sweep
  separates them; the leak that drains control also kills stim (too-similar co-firing rates).
- **Conclusion:** write=leak is fundamental — not a tuning gap but a structural property of a
  homogeneously self-active medium. Breaking it needs a genuinely QUIESCENT substrate (no baseline
  activity outside driven regions), which is an architectural change, not a knob. The substrate's
  real computational value remains ANALOG signal processing (Addendum 1), not digital memory.

## ADDENDUM 3 (2026-06-03) — THE ROOT, causally confirmed: homogeneous self-activity

After ~50 experiments mapping limits (memory deadlock, reservoir NULL, computation NULL), G81-G83
isolated the SINGLE ROOT: the substrate's HOMOGENEOUS SELF-ACTIVITY drowns localized signal. On the
active substrate a localized input is unreadable (≈chance); on a QUIET substrate (background culled)
the SAME input is read PERFECTLY (sanity 1.00, both seeds, G83). This one fact unifies every failure:
- Memory fails because control is never blank (self-activity) — but measured on the ACTIVE substrate.
- Reservoir fails because no clean state encodes input (self-activity drowns it).
- Computation fails because the input doesn't register (self-activity).
And it explains the proto-cell successes: the channel PROTECTS a quiet interior where signal stands out.

**The architectural lever: a QUIET/SPARSE substrate** (atoms silent unless driven). This is the one
untested architecture that could unlock memory AND computation — the deadlock-breaking direction the
whole programme points to. The memory "fundamental" verdict (Addendum 2) was conditional on the ACTIVE
substrate; it must be re-tested on a quiet one. That is the live frontier.

## ADDENDUM 4 (2026-06-03) — memory thread CLOSED after exhausting even physical disconnection

The root-removal campaign (G83-G86) confirmed the homogeneous-activity root (quiet substrate reads
input perfectly, G83) but did NOT break the memory deadlock: on a quiet substrate control latches via
emission transit (G84), then bridge percolation (G85), then -- even with stim/control FULLY
DISCONNECTED (cut bridges + gated charge, G86) -- INTRINSICALLY. The invariant across ~70 experiments:
the substrate has no stable BLANK state; any structured region latches activity, so there is never a
written-vs-unwritten contrast. Selective memory is impossible in this medium, conclusively. DECISION:
the memory thread is closed; chasing further layers past 70 NULLs would be refusing a robust negative.
The substrate is a memoryless nonlinear analog processor (instantaneous single-channel computation
only). A learning/memory system requires a fundamentally different (sparse, quiescent-by-design,
disconnect-capable) substrate -- an architecture, not a knob.

## ADDENDUM 5 (2026-06-05) — the COMPUTATION/optimization thread's lone positive claim REFUTED (G145→G149)

After the memory thread closed (Addendum 4), a later arc (G138–G145) pivoted to energy-based / Ising /
annealing computation and produced the programme's ONLY positive-advantage claim: G145 reported an
oscillator-Ising machine beating greedy 8/8 on hard frustrated MAX-CUT — "the one place vibrations-computing
has a real edge." A 2026-06-05 audit (G146–G149) dismantled it, honestly and in stages:

- **G146** — G145's greedy baseline was SIGN-BUGGY: it flipped on `gain<0`, descending toward MIN-cut
  (returning NEGATIVE cuts, −25 to −67). A *correct* multi-restart greedy reaches the optimum on all 8 of
  G145's n=30 instances — they aren't hard, and the oscillator merely ties correct greedy. The "8/8 win" was
  a win over a backwards baseline. Oscillator vs proper SA at n=30: a tie (both near-optimal).
- **G147–G148** — scaling to n=200–360 (genuinely hard regime), **classical simulated annealing** does
  genuinely beat a strong correct greedy (~+2%, 14/15) — the textbook "annealing > local search on glassy
  landscapes." BUT separating the *physical oscillator* from classical SA: the oscillator TIES correct greedy
  (6/15, gap ≈ 0) and LOSES to SA 15/15 at every scale. The advantage belongs to the ALGORITHM (SA), which
  needs no substrate.
- **G149** — fairness control: gave the oscillator ~10× compute (same dynamics, only more of it). ROBUST-
  NEGATIVE — it still ties correct greedy and loses to SA 10/10. The weakness is in the dynamics, not the
  budget.

**Corrected bottom line:** the substrate's last candidate advantage is an advantage of the **classical SA
algorithm alone**; the physical/vibrations oscillator confers **no computational edge** over correct local
search at any scale or budget tested. Combined with the closed memory thread (Addendum 4) and the
scoped/decorative communication and proto-cell results, the honest, programme-wide conclusion stands without
exception: **the physics is decorative everywhere tested; standard classical methods carry every win.** The
deliverable was never the simulation succeeding — it was the rigorous, self-correcting process, here applied
to retract an over-claim (a sign-bugged baseline) rather than make one. Docs: g145–g149 amendments.
