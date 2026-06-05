# FRONTIER — current state of the EQMOD/vibrasim substrate programme

**One-screen pointer so a new session knows where the frontier is WITHOUT re-deriving settled work.**
Authoritative detail lives in `docs/amendments/FINDINGS_SUMMARY.md` (+ its addenda), `LOGBOOK.md` (append-only
diary; newest at the bottom), and the per-experiment `docs/amendments/g*.md`. This file is a map, not a source
of truth — if it disagrees with those, they win. Last updated: 2026-06-05.

## Highest experiment numbers (check before starting anything)
- **Substrate physics thread `gNNN`:** completed through **G149**. `ls docs/amendments/g*.md | sort` and read the
  highest few before proposing a "new" gNNN — much of G30–G149 is already done.
- **Cognition/affect thread `JEP-NNN`:** completed through ~**JEP-476** (clean-room integration audit PASS).
- Do NOT trust a stale start-of-session git snapshot for the frontier (it caused G47–G49 to be re-derived on
  2026-06-05). Trust `git log` + the highest `g*.md`/`jep*` docs.

## Verdict by thread (all honestly closed; see FINDINGS_SUMMARY for the full case)
| Thread | Status | Bottom line |
|--------|--------|-------------|
| Memory (activity representation) | **CLOSED NEGATIVE** | No stable blank state; any region latches activity → no written-vs-unwritten contrast (G83–G96, ~70 NULLs). |
| Memory (MATTER position) | **POSITIVE, scoped** | Driven-matter position is a selective+persistent multi-bit store with wide spacing (G114–G119); MAINTAINED not static (G120). The one real memory positive. |
| Communication | **POSITIVE, scoped** | Co-located real-time spatial codec; needs active reset between symbols; NOT transport over distance (G97–G105). |
| Transport | **scoped** | Free carriers don't cross distance; continuously-driven matter does, slowly (G109–G112). |
| Computation / optimization | **CLOSED NEGATIVE (2026-06-05)** | G145's lone "genuine physical advantage" REFUTED: greedy baseline was sign-buggy; at scale classical **SA** beats correct greedy, but the **oscillator/vibrations machine ties greedy and loses to SA** (G146–G149). Advantage is the classical algorithm's, not the substrate's. |

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
