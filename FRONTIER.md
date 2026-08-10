# FRONTIER — sharp discipline

**One-screen pointer so a new session knows where the frontier is WITHOUT re-deriving settled work.**
Authoritative detail lives in `docs/DISCIPLINE_SHARP.md` (operating rules), `docs/BELIEF_PATH.md` (spine),
`docs/amendments/FINDINGS_SUMMARY.md` (+ addenda), `LOGBOOK.md` (append-only diary; newest at the bottom),
and the per-experiment `docs/amendments/g*.md`. This file is a map, not a source of truth — if it disagrees
with those, they win. Last updated: 2026-08-10 (merge-conflict resolution; content states 2026-07-19 + 2026-06-12).

## Active programme: belief path (2026-07-19, after BP-C5)

### BP-C5 result: **NULL** (informative)

| Arm | Specialisation | Pop | χ |
|-----|----------------|-----|---|
| FREE + midplane | **0.667** (&lt;0.90) | 1.0 | **0.0** |
| ILW + midplane | **1.000** | 1.0 | n/a |

- Walls work.
- **Engineered ILW** specialises halves (scoped, named engineering).
- **Free dual-band chemistry** still fails the 0.90 structural bar even with χ=0.

### Board
A/B PASS · C closed partial + C5 NULL · PRIM1-D2 PASS · PRIM2-D0 PASS · D1 PASS

### Belief (honest)
Collection **difference** via **ILW ports** is achievable as **engineered write**.
Collection talent from **free shared physics alone** remains **unproven** at locked bars.

### PRIM14 (2026-08-10): per-bond rest length — D0 PARTIAL, D1 NULL (informative)
The G154 follow-on (R5). D0: displaced middle moves back toward stored geometry
where the global-r_eq control does not (controls clean). D1 (tension×damping
matrix): R ceilings at ~0.5 in every regime — STRUCTURAL, not dynamical. Mechanism
census: a second bond forms DURING the probe at the displaced geometry
(**measurement-write coupling** — formation-frozen rest lengths store every held
geometry, including the measurement's), so all regimes settle at the two-attractor
compromise. D0's "true attractor at stored geometry" inference is corrected: the
substrate stores a superposition of stored + probe-held geometry. Next (NEW ID
only): D2 with the write channel closed during probing (saturated valence /
bond-formation freeze). LOGBOOK 2026-08-10.

### Next (discipline)
- ~~Document ILW as §4.8 port doctrine~~ **done 2026-08-10** (CONCEPT §4.8 + ilw_port_doctrine.md + Brain-blocked statement)
- New pre-reg only if a *non-engineered* free-chemistry talent mechanism is proposed
  (temporal/rhythm at same band is ALREADY NULL: BP-C4, BP-C8, C21–C79 — DISCIPLINE_SHARP §4.1 corrected)
- No lowering B1 from 0.90

## Engineering side-track status (2026-08-10, two honest NULLs, closed)
Flux G15/G16 port: tagging path + energy-conserving dreaming delivered and tested
(E1–E3 green, auditor 1e-9 with dream active). **G15F-1 = NULL-T** (tagged engrams
don't survive training; consolidation never testable). **G15F-2 = NULL** (6-condition
persistence map): tagged nodes are a ~2–5 s recency echo of the ongoing stimulus, not
a store — decay threshold lifts the echo (C2/C5: ~25–32 nodes) but only for the
last-trained pattern; continuous stimulus thermally destroys its own traces (C4: 0
nodes); rest-phase survival S = 0.0 everywhere. Full case: LOGBOOK 2026-08-10.
A G15F-3 would need stimulus-energy/decay-pressure decoupling — new ID, only if
re-admitted. G16F untestable without persistent engrams. No bar was retuned.

## Archive threads (all honestly closed; do NOT reopen without re-admission)

### Highest experiment numbers (check before starting anything)
- **Substrate physics thread `gNNN`:** completed through **G159** (G154–G159 added 2026-06-12, in
  `docs/amendments/G15*.md` + LOGBOOK). `ls docs/amendments/g*.md | sort` and read the highest few before
  proposing a "new" gNNN — much of G30–G159 is already done.
- **Cognition/affect thread `JEP-NNN`:** completed through ~**JEP-476** (clean-room integration audit PASS).
- Do NOT trust a stale start-of-session git snapshot for the frontier (it caused G47–G49 to be re-derived on
  2026-06-05). Trust `git log` + the highest `g*.md`/`jep*` docs.

### Verdict by thread (see FINDINGS_SUMMARY for the full case)
| Thread | Status | Bottom line |
|--------|--------|-------------|
| Memory (activity representation) | **CLOSED NEGATIVE** | No stable blank state; any region latches activity → no written-vs-unwritten contrast (G83–G96, ~70 NULLs). |
| Memory (MATTER position) | **POSITIVE, scoped** | Driven-matter position is a selective+persistent multi-bit store with wide spacing (G114–G119); MAINTAINED not static (G120). The one real memory positive. **Recall-by-content NULL (G154):** matter is a REGISTER, not a content-addressable memory — bridge tension has one global r_eq, no per-bond rest length, so a stored pattern is not a retrievable attractor; Hopfield does it at ~1/546th the compute. |
| Modular isolation (topological) | **POSITIVE, scoped (2026-06-12)** | A persistent-homology (H₀ / connected-component) bond-formation rule SELF-ORGANISES a stable modular partition (G158) — emergent, chosen by graph topology, NOT a hand-placed plane like G86 — and that partition COMPLETELY blocks bond-mediated charge percolation (G159: M=2 → B_fire=0; connected control percolates, B_fire=54). Scope: bond channel ONLY; the field channel (`r_integrate`/emitted vibrations) and atom erosion (G93) remain → necessary, not sufficient, for modular memory. G158's mechanical functional marker was under-sensitive (NULL); G159 confirmed the functional effect on the right channel. |
| Communication | **POSITIVE, scoped** | Co-located real-time spatial codec; needs active reset between symbols; NOT transport over distance (G97–G105). |
| Transport | **scoped** | Free carriers don't cross distance; continuously-driven matter does, slowly (G109–G112). |
| Computation / optimization | **EQMOD substrate NEGATIVE; adjacent CIM hardware competitive (2026-06-05)** | G145's "8/8" rested on a sign-bugged greedy; the NAIVE oscillator ties correct greedy & loses to SA (G146–G149). But the textbook AHC-CIM (Leleu 2019) BEATS correct greedy & is in SA's league (G150), robust across both Gaussian & ±1/SK families (G151) and to n=600 (G152) — a real but *established, adjacent* physical-annealer result, NOT EQMOD. At **matched budget classical SA is marginally BEST** (~1.7% ahead, 8/8; G153), and far simpler. EQMOD's OWN dynamics still can't optimize (G135). Ordering: SA > CIM-AHC > correct-greedy. |
