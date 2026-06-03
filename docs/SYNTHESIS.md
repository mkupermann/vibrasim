# EQMOD — Synthesis: what this substrate is, causally (BET-086 → G86)

Bottom-up physics: vibrations → electrons → atoms → molecules → bridges → membranes. This is the
honest, causally-grounded summary of ~100 pre-registered experiments. The charter's goal is a
deadlock-BREAKING PROCESS, not guaranteed success; this document is that process's result.

## What the substrate IS (robust positives)
1. **A self-organizing proto-cell.** Rich chemistry (G27) → a large closed membrane forms (G30) →
   selectively permeable in the engine (G32) → maintains an interior gradient = homeostasis (G43) →
   regulates back to set-point after perturbation (G44). Membrane formation is scale-invariant (G51).
2. **A tunable nonlinear ANALOG signal processor.** The proto-cell is a first-order linear controller
   (step response G58, DC gain G59, low-pass G60, cutoff tunable by membrane size G61) WITH a
   saturating nonlinearity (G74) — so it COMPUTES, not just filters: denoise (G62), frequency
   discriminate (G63), AM demodulate (G75), recover a signal buried in noise (G76).
3. **Partially self-renewing structure.** Bond turnover makes the membrane a FLUID, partially
   self-repairing, size-homeostatic structure (G53-G55) — the rigidity ceiling is a tunable frontier.

## What the substrate CANNOT do (robust, causal negatives)
1. **No selective persistent MEMORY** — exhausted across ~70 experiments (BET-089→102, G33-G73,
   G64-G86): every write mechanism, firing rule, plasticity rule, consolidation, sleep-sweep, charge
   gate, quiet substrate, local emission, AND physical disconnection fails identically. CAUSE: the
   substrate has NO STABLE BLANK STATE — any region with atoms develops latched bridge activity, so
   there is never a written-vs-unwritten contrast. write=leak is fundamental.
2. **No TEMPORAL / reservoir computation** — held-out temporal XOR ≈ chance via every reservoir state
   (proto-cell interior G78, firing lattice G79, bridge strengths G80). CAUSE: the substrate can't
   hold a high-dimensional fading memory; the same memory wall.
3. **No MULTI-channel computation, no metabolism, no division, no self-repair-from-rigidity** (G45-G52,
   G56, G81-G82).

## The single ROOT (causally confirmed)
**Homogeneous self-activity.** On the ACTIVE substrate a localized input is unreadable (≈chance); on
a QUIET substrate the SAME input is read PERFECTLY (G83, 1.00 both seeds). The substrate's own
ceaseless activity drowns signal and latches structure everywhere — this single fact unifies every
negative (memory, reservoir, multi-channel computation) AND explains every positive (the proto-cell
works because its channel PROTECTS a quiet interior where signal stands out).

## BREAKTHROUGH — selective persistent memory exists, in a NEW representation (G114–G116)
The programme's central negative ("no selective persistent memory") was true for ACTIVITY-based stores
(bridge strength, firing, charge) — they couple persistence and selectivity through one spreading dynamic
(write=leak, maintenance=contamination). The driven-matter discovery (G110–G113) opened a different
representation: MATTER POSITION. An atom driven to a location holds it after release (persists, G115,
12/12 atoms, drift<2 over 2000 ticks, identity stable), and a written cell A stays occupied while an
unwritten cell B stays empty and a no-write control leaves A empty (selective, G116 PASS both seeds). So
matter-position is the FIRST selective+persistent store on this substrate — the deadlock was
REPRESENTATIONAL, not absolute. Scope (honest): a 1-bit presence store in an engineered cleared band
(scaffold ~ §4.8 ports); content-addressable multi-pattern memory is the next frontier. The route out
came from chasing and correcting three wrong transport claims (G107/G110 retracted) — the honesty
discipline literally produced the breakthrough.

## The deep unification (G88–G107): no controllable middle regime [superseded in part by G116]
NOTE: the "no signal is localized+persistent+mobile" framing below holds for ACTIVITY signals; G116 shows
MATTER POSITION achieves localized+persistent (just not fast-mobile). Read the unification as about
activity-based representations.
Three deadlocks, one root — the substrate has NO regime where a signal is at once localized, mobile, AND
persistent. Signal behaviour is density-dependent and offers no usable middle:
- **Too sparse/active → it SPREADS uncontrollably.** Writing a memory broadcasts ("write = leak");
  sustaining an engram drives self-activity that contaminates elsewhere ("maintenance = contamination").
  You cannot keep a signal LOCAL.
- **FREE carriers do not TRAVEL; bound matter DOES, slowly.** A symbol-strength FREE excitation never
  reaches the far end — free vibrations (G105/G107/G108; velocity not conserved, diffusive, G109) and
  charge (G106; decays along bridges). But BOUND matter transports: a continuously-driven atom traverses
  >20 units ALIVE with its symbol coordinate preserved (G112 PASS, both seeds), moving coherently at ~3%
  of nominal speed (mass-scaled, NOT bond-restrained — cutting its bridges changes nothing, G111). THREE
  retractions found this: "condenses into an atom" (G107→G108), "overdamped, nothing travels"
  (G110→G111), and the general "transport closed" framing (→G112). A signal CAN move — as driven matter,
  slowly (~200 ticks per ~20 units) — though a free signal cannot.
Between the two, there is no easy operating point that is simultaneously localized, persistent, and
FAST-mobile: selective MEMORY (localized + persistent) fails because activity spreads; FREE-carrier
TRANSPORT fails because vibrations are diffusive and charge decays. The one mobility that DOES exist —
driven bound matter (G112) — works but is ~30× slow: a real second communication mode, bounded by speed
not possibility. What the substrate DOES do well needs only ONE property at a time: co-located readout
(localized; mobility not required, G104), analog filtering, proto-cell homeostasis (persistent structure,
no signal to move). The deadlock is a hard trade-off in the medium, not a tuning failure.

## Update — G88–G107 (2026-06-03): memory re-closed sharper, COMMUNICATION positive, TRANSPORT closed
- **Memory deadlock re-opened (G88) then re-closed at a sharper level (G88–G96).** G88 found a perfect
  zero-input blank state, refuting the "no stable blank state" wording. The deeper truth: persistence
  and selectivity are coupled on BOTH horns — ACTIVE substrate sustains the engram but contaminates
  control; QUIET substrate keeps control blank but ERODES the engram's anchoring atoms (G93). Bridge
  consolidation persists NON-selectively, by count (G94) and topology (G95); vibration seals are inert
  vs the charge/bridge channel (G96). New slogan beside "write=leak": **"maintenance=contamination."**
- **A COMMUNICATION positive (G97–G105) — corrects "single-channel", scoped by G105.** The quiet
  substrate is a clean MULTI-channel CO-LOCATED spatial codec: ~10 parallel spatial channels (pitch ~3,
  G97) × 4 bits/symbol (G99) × 1 tick/symbol (G100), noise-robust (G101). It needs an active reset
  between symbols (G98) — the SAME accumulation that defeats memory, seen as inter-symbol interference.
  CAPSTONE: a text string was written into the substrate as localized excitations and read back VERBATIM
  on both seeds (G104, K=4), no LLM/transformer/embedding. IMPORTANT SCOPE (G105): this is co-located
  encode/decode (same site, same tick), NOT transport over distance — free vibrations are absorbed
  locally and do not carry a symbol downstream. "Transmission/transported" wording was retracted.
  G102/G103 are the instructive failures (K=16 violates the G97 pitch). See COMMUNICATION_SUMMARY.md.

## The honest headline
**The substrate is a memoryless but MULTI-CHANNEL, nonlinear ANALOG signal processor and CO-LOCATED
spatial codec — and a self-regulating proto-cell.** It computes instantaneous continuous functions
(filter, integrate, demodulate, denoise) and encodes/reads-back information in real time at one site
(parallel spatial channels; verbatim text end-to-end with an active reset). Free carriers do not transport
a signal across distance (vibrations diffusive G109, charge decays G106), but DRIVEN MATTER does — slowly,
with the symbol preserved (G112) — a second, slow communication mode. It cannot store, learn, or compute
over time. The reset that makes it a usable codec is the very operation it cannot avoid, because
it retains-and-superimposes rather than storing selectively. A memory/learning system on this physics
requires a fundamentally different SUBSTRATE — sparse, quiescent-by-design, with a stable blank state and
cuttable connectivity — an architecture, not a parameter. That is the deadlock, mapped to its root; the
co-located codec is the constructive complement. Both are the charter's deliverable.

## Reusable mechanisms (docs/patterns/)
atom_proximity_reflector · engineered_port_wall · protocell_homeostasis · protocell_controller ·
parallel_spatial_channel · driven_matter_transport · 01-which-constraint-binds · 02-write-contaminate-tension.

## Sub-summaries
MEMORY_PROGRAMME_SUMMARY (+G88–G96 addendum) · PROTOCELL_SUMMARY · ANALOG_COMPUTER_SUMMARY ·
COMMUNICATION_SUMMARY (G97–G104) · FINDINGS_SUMMARY (+4 addenda).
