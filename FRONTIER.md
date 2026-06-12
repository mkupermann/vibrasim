# FRONTIER — current state of the EQMOD/vibrasim substrate programme

**One-screen pointer so a new session knows where the frontier is WITHOUT re-deriving settled work.**
Authoritative detail lives in `docs/amendments/FINDINGS_SUMMARY.md` (+ its addenda), `LOGBOOK.md` (append-only
diary; newest at the bottom), and the per-experiment `docs/amendments/g*.md`. This file is a map, not a source
of truth — if it disagrees with those, they win. Last updated: 2026-06-12.

## Highest experiment numbers (check before starting anything)
- **Substrate physics thread `gNNN`:** completed through **G159** (G154–G159 added 2026-06-12, in
  `docs/amendments/G15*.md` + LOGBOOK). `ls docs/amendments/g*.md | sort` and read the highest few before
  proposing a "new" gNNN — much of G30–G159 is already done.
- **Cognition/affect thread `JEP-NNN`:** completed through ~**JEP-476** (clean-room integration audit PASS).
- Do NOT trust a stale start-of-session git snapshot for the frontier (it caused G47–G49 to be re-derived on
  2026-06-05). Trust `git log` + the highest `g*.md`/`jep*` docs.

## Verdict by thread (all honestly closed; see FINDINGS_SUMMARY for the full case)
| Thread | Status | Bottom line |
|--------|--------|-------------|
| Memory (activity representation) | **CLOSED NEGATIVE** | No stable blank state; any region latches activity → no written-vs-unwritten contrast (G83–G96, ~70 NULLs). |
| Memory (MATTER position) | **POSITIVE, scoped** | Driven-matter position is a selective+persistent multi-bit store with wide spacing (G114–G119); MAINTAINED not static (G120). The one real memory positive. **Recall-by-content NULL (G154):** matter is a REGISTER, not a content-addressable memory — bridge tension has one global r_eq, no per-bond rest length, so a stored pattern is not a retrievable attractor; Hopfield does it at ~1/546th the compute. |
| Modular isolation (topological) | **POSITIVE, scoped (2026-06-12)** | A persistent-homology (H₀ / connected-component) bond-formation rule SELF-ORGANISES a stable modular partition (G158) — emergent, chosen by graph topology, NOT a hand-placed plane like G86 — and that partition COMPLETELY blocks bond-mediated charge percolation (G159: M=2 → B_fire=0; connected control percolates, B_fire=54). Scope: bond channel ONLY; the field channel (`r_integrate`/emitted vibrations) and atom erosion (G93) remain → necessary, not sufficient, for modular memory. G158's mechanical functional marker was under-sensitive (NULL); G159 confirmed the functional effect on the right channel. |
| Communication | **POSITIVE, scoped** | Co-located real-time spatial codec; needs active reset between symbols; NOT transport over distance (G97–G105). |
| Transport | **scoped** | Free carriers don't cross distance; continuously-driven matter does, slowly (G109–G112). |
| Computation / optimization | **EQMOD substrate NEGATIVE; adjacent CIM hardware competitive (2026-06-05)** | G145's "8/8" rested on a sign-bugged greedy; the NAIVE oscillator ties correct greedy & loses to SA (G146–G149). But the textbook AHC-CIM (Leleu 2019) BEATS correct greedy & is in SA's league (G150), robust across both Gaussian & ±1/SK families (G151) and to n=600 (G152) — a real but *established, adjacent* physical-annealer result, NOT EQMOD. At **matched budget classical SA is marginally BEST** (~1.7% ahead, 8/8; G153), and far simpler. EQMOD's OWN dynamics still can't optimize (G135). Ordering: SA > CIM-AHC > correct-greedy. |

## Programme-wide honest conclusion
The physics is **decorative everywhere tested**; standard classical methods carry every win. The deliverable was
never the simulation succeeding — it is the rigorous, self-correcting **process** (pre-registration, matched
negative controls, retracting over-claims like the G145 sign-bug). See `README.md` lines ~37–67 for Michael's
own framing of this as the honest result.

## If you are an autonomous session deciding the next step
1. The substrate's positive threads (matter-memory, co-located codec) are SCOPED and characterized; the negative
   threads (activity-memory, computation) are closed after exhaustive testing. There is no obvious open positive.
2. Before launching a "new" experiment, confirm it is not already in `docs/amendments/` (G30–G149). Re-derivation
   wastes compute (it happened this session).
3. Genuinely valuable moves now are consolidation, reproducibility/process infrastructure, or a *clearly* novel
   question — not churn. NULL is a valid finding; manufactured busywork is not. Honor pre-registration
   discipline (bars in `docs/amendments/<name>.md` BEFORE the run; no post-hoc threshold tuning).
</content>
