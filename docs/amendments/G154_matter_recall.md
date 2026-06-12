# G154–G157 — Matter-register associative memory (pre-registered amendment)

**Authored:** 2026-06-12 · **Status:** pre-registered, no run yet · **Thread:** substrate physics (`gNNN`)
**Grounding:** `FRONTIER.md`, `docs/MATTER_MEMORY_SUMMARY.md` (G110–G125), `docs/MEMORY_PROGRAMME_SUMMARY.md`,
`LOGBOOK.md` (through G153 / JEP-476), `docs/patterns/`. Engine `world/` @ `bf1c08f` (main).

This amendment comes out of a grounded, adversarially-reviewed unblock survey (2026-06-12). Seven mechanism-level
"new science" directions were surveyed and **all seven were dropped** under adversarial review; the completeness
critic independently judged the map exhausted. No mechanism-change unblocks the named deadlocks within the hard
constraints. This amendment therefore does **not** re-litigate the deadlocks — it pushes the one representation
that ever broke a deadlock (matter position) from a *register* toward an *associative memory*, and tests each step
against a strong classical baseline at matched compute. NULL is an expected and valid outcome.

---

## Integrity note (read first — this is on the record on purpose)

Reservoir computing was one of the seven dropped directions. Two corrections to the drop's stated justification,
recorded here so a later audit finds them already disclosed rather than uses them to discredit the synthesis:

1. **The "disallowed 2026-05-22" citation is superseded.** The same-day correction (`LOGBOOK.md`, 2026-05-22)
   relaxed the constraint to "no LLM; combining existing research is allowed." Citing the pre-correction ban is
   stale.
2. **BET-030/031 is NOT valid empirical ground for excluding a substrate-reservoir for this niche.** Those runs
   tested an ESN against a persistence baseline on *raw-audio next-step prediction* and returned NULL by
   **task-granularity mismatch** — the LOGBOOK states verbatim "Not an ESN failure per se" and "ESN excels at
   NARMA/chaotic synthetic signals, not raw audio next-step prediction." That is a different question from
   "can a physical substrate act as a useful feature-map for matter-coded memory."

**Honest standing reason to deprioritize reservoir (not to declare it closed):** *decorative-risk.* A
substrate-as-reservoir would have to beat a matched random ESN, and the standing record (random reservoirs already
solve the repo's tasks; the substrate's own dynamics have never added value over classical baselines at matched
compute) gives no evidence it can. It was **never fairly tested** as a feature-map for the matter-memory niche.
If ever revisited, the fair test is *substrate-reservoir vs. matched random ESN at matched compute* — not a
re-cite of the audio-prediction null. The "frontier exhausted" conclusion is therefore taken as **provisional for
the reservoir direction specifically**, and settled for the other six.

---

## The reframe

Stop competing on activity-memory and combinatorial optimization. Occupy the niche the substrate provably owns:
a spatially-addressed analog store whose state lives in **matter position**, the substrate's one non-percolating
element. This sidesteps both binding constraints at once — matter does not percolate (kills write=leak), and we
do not ask it to optimize (kills the non-Hamiltonian lock). The G154 recall dynamic (cue → matter relaxes to a
stored configuration) is an attractor in *physical* space, fully emergent — the legal door for the attractor idea
that died at the illegal one (frozen weight modules).

## What stays closed (no softening)

- **Activity-based selective persistent memory** — CLOSED NEGATIVE (G83–G96, ~70 NULLs). No quiescent baseline;
  any structured region latches via ambient flux. Topological, not a tuning gap.
- **Write=Leak duality** — one physical medium carries write and leak; gating starves write, bridge-graph write
  self-ignites. A learning rule cannot decouple a percolation channel.
- **EQMOD cannot optimize** — categorical-label binding rules are not a programmable Hamiltonian (G135 NULL;
  G145–G149 lose to SA).
- **Classical SA beats all physical substrates at matched budget** — a verdict, not a deadlock (G150–G153).

Dropped candidates and fatal objections (SOC, attractor, predictive-coding, EqProp, thermo, modular) are recorded
in the 2026-06-12 unblock-survey synthesis; reservoir is qualified above.

---

## Pre-registration discipline for this amendment (FROZEN 2026-06-12)

- **Bars below are frozen as of 2026-06-12, before any run. No post-hoc threshold tuning. NULL stands as a
  finding and is logged in `LOGBOOK.md`, never quietly retried with a relaxed bar.**
- **Seeds:** `{42, 7, 13}` (three; the prior programme used two — the third hardens against single-seed flukes
  like the retracted G37). Report mean ± SD.
- **Matched compute:** every "beats baseline B" claim is judged at matched **wall-clock**, not matched iterations
  (the G153 fairness rule that flipped the CIM-AHC result). Baselines are numba-JIT.
- **Negative control is mandatory and MUST FAIL** for any PASS to count.
- **HARD GATING (non-negotiable):** the chain is **G154 → G155 → {G156 independent} → G157**. **G157 runs only on
  a PASS in G154 or G155.** A NULL or FAIL in a gating experiment **closes** the gated downstream experiment — it
  is not reopened by relaxing the gate, and the gate is not renegotiable post-hoc. If G154 NULLs, G155–G157 are
  **not** softened to manufacture a win elsewhere; each carries its own frozen bar and its own must-fail negative
  control, independently. A programme-wide NULL is a publishable finding about when physical substrates help.

---

## G154 — Content-addressable recall on the matter register (RANK 1, run first)

The open frontier `MATTER_MEMORY_SUMMARY` names (lines ~49–53): the matter store is selective + persistent +
multi-bit by write-cell, but recall-by-content (partial cue → matter relaxes to the stored pattern) is unshown.

- **Hypothesis (M beats B):** a driven-matter register M (≥5-unit-spaced carrier cells, anchored per G125)
  recalls a stored k-bit pattern from a partial cue (½ the bits stimulated) at bit-accuracy **≥ 0.90/bit**
  (mean over seeds {42,7,13}), *without re-writing the unstimulated cells from scratch* (true content-addressing).
- **Strong baseline B:** classical Hopfield / linear associative store sized to the *same carrier count*, run at
  **matched wall-clock**. If B reaches ≥0.90/bit for less compute, M's physics is decorative → NULL.
- **Negative control (MUST fail):** cue an *unwritten* register with the same partial stimulus → bit-accuracy
  must be ≤ chance (0.5/bit). If the empty register "recalls," the readout is an artifact (the G34 lesson).
- **Metric:** bit-accuracy/bit, mean ± SD over 3 seeds; carrier drift < 2 (G115 gate); retention ≥ 2000 ticks.
- **Bars:** **PASS** ≥0.90/bit AND beats-or-ties B at matched compute AND neg-control fails. **PARTIAL** 0.75–0.90
  or single-seed only. **NULL** <0.75 or B wins at matched compute. **FAIL** neg-control also recalls (artifact).
- **Engine:** matter-drive + anchor hooks in `world/physics.py`; readout via `world/substrate_memory.py`
  (`SubstrateMemory`, RLS); config `renders/calibration_session3.toml`.

## G155 — Codec ⇄ register integration (RANK 2)

Wire the co-located MIMO codec (G99 K=16, G104) to *address* the matter register: write a symbol through the codec
→ lands as a carrier position → read back through the codec.

- **Hypothesis:** codec-addressed round-trip symbol fidelity **≥ 0.94** (the codec's own G99/G104 floor) over
  ≥ 4 parallel channels, carriers persisting ≥ 1500 ticks.
- **Strong baseline:** classical parallel DAC/ADC + RAM at matched compute. Physics earns its place only if the
  co-located parallelism costs less per channel.
- **Negative control (MUST fail):** restore active background (λ_gen > 0) → per G83 the localized input must
  become unreadable. If it reads anyway, the channel-isolation claim is false.
- **Bars:** **PASS** ≥0.94 AND ≥4 ch AND ≥1500-tick hold. **PARTIAL** ≥0.94 but ≤3 ch or <1500-tick hold.
  **NULL** <0.90 or classical cheaper. **FAIL** neg-control reads on active substrate.
- **Engine:** quiet-substrate MIMO (`world/spatial.py` + ridge decoder); register = matter cells.

## G156 — Proto-cell analog front-end vs digital IIR, at scale (RANK 3, independent of G154/G155)

The proto-cell is the cleanest PASS in the programme (G44–G62, both seeds, `docs/patterns/protocell_controller.md`).
Open question: does *parallelism* of analog cells beat a digital first-order filter on energy/compute?

- **Hypothesis:** N parallel proto-cells denoise N streams at the documented ~9× SNR gain (G62) at **lower
  matched-compute cost** than N digital first-order IIR filters, for N ≥ Nₜ (Nₜ fixed from a pilot **before** the
  scaled run; recorded here once measured).
- **Strong baseline:** numba-JIT digital IIR low-pass, same cutoff (G61), same N.
- **Negative control (MUST fail):** "membrane" with the selective channel disabled must NOT regulate (no set-point
  recovery) — confirms the channel, not ambient dynamics, carries the filtering (G44).
- **Bars:** **PASS** ≥9× gain AND cheaper than digital at matched compute for the pre-set N. **PARTIAL** gain
  holds but not cheaper. **NULL** (expected per FRONTIER) digital cheaper at all N. **FAIL** channel-off regulates.
- **Engine:** `world/physics.py` membrane-channel; proto-cell construction harness.

## G157 — Driven-matter transport bus (RANK 4, GATED on G154/G155 PASS)

**Runs only if G154 or G155 PASS.** Transport is real but slow (~3% nominal, drive-dependent, G112); it matters
only as a distance bus for a working register/codec.

- **Hypothesis:** driven-matter line carries K-ary symbols ≥ 20 units at fidelity ≥ 1.00 (G113) *and* joins to
  G155's codec endpoints with no fidelity loss — plus a **named axis** on which it beats a classical buffered link
  (e.g. no-active-clock co-located refresh). Name the axis before running or accept NULL.
- **Negative control (MUST fail):** remove sustained drive → carriers diffuse, fidelity → chance (G109).
- **Bars:** **PASS** fidelity 1.00 + clean join + a named axis where it beats the wire. **NULL** (expected) wire
  dominates every axis. **FAIL** drive-off still transports.

---

## First experiment

**G154.** Highest information per unit compute: it extends the only deadlock-breaking positive (matter position),
needs no new primitive (anchored multi-cell harness prototyped at G119c/G125), is decisive either way (PASS = a
position register becomes an associative memory; NULL with Hopfield winning closes the last memory frontier
honestly), and its negative control directly guards the readout-artifact class that produced the retracted G34/G145
overclaims.

## Payoff

- **Brain science.** A PASS says a substrate can hold a selective, content-addressable memory in the slow
  positional/structural state of matter (synaptic-tag / spine-geometry analogue) precisely because that variable
  does not percolate, while the fast activity variable cannot — a concrete data point in the activity-vs-structural
  engram debate. A NULL teaches that even matter position needs an active maintenance scaffold to be associative.
- **AI learning.** A PASS demonstrates associative recall with no backprop and no learned weight layer — pure RLS
  readout over a physically-maintained register. A NULL adds a fourth independent confirmation that, at matched
  compute, a directly-engineered classical method (Hopfield/SA/ridge) beats the physical substrate — physics pays
  only where it buys parallelism or energy the algorithm cannot, and that axis must be named before the run.

---

## Reproducibility

Engine `world/` @ commit `bf1c08f` (main); macOS-arm64, Python 3.13, `.venv` at repo root; config
`renders/calibration_session3.toml` (atom-producing, λ_gen = 0); seeds `{42, 7, 13}`.
Each G15x runs as a `tools/g15x_*.py` script logging to `LOGBOOK.md` (append-only). Bars in this document are
frozen pre-run; no post-hoc tuning; NULL stands.
Baselines (Hopfield / IIR / SA) are numba-JIT, matched on wall-clock not iteration count; negative controls are
mandatory and must FAIL for any PASS to count.

*Verification flags:* deadlock/positive verdicts and G-numbers attributed to `FRONTIER.md` and
`docs/MATTER_MEMORY_SUMMARY.md`. **[INFERRED]** that new experiments are authored as `tools/` scripts (per-G
amendment docs were slimmed; LOGBOOK is the live record) and that the G119c/G125 anchored-multi-cell harness is
reusable as-is. **[UNVERIFIED]** the Hopfield/IIR baseline wall-clock parity and the proto-cell scaling threshold
Nₜ — both measured in a pilot and fixed before the scaled run.
