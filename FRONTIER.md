# FRONTIER — current state of the EQMOD / vibrasim programme

**One-screen pointer so a new session knows where the frontier is WITHOUT re-deriving settled work.**  
Authoritative detail: `docs/BELIEF_PATH.md` (active question), `docs/FINDINGS_SUMMARY.md` / `docs/SYNTHESIS.md` (closed maps), `LOGBOOK.md` (diary, newest at bottom).  
If this file disagrees with those, **BELIEF_PATH + the latest pre-registered amendment win for direction; FINDINGS/SYNTHESIS win for settled negatives.**  
Last updated: **2026-07-19** (autonomous belief-path session).

---

## Active programme (read first)

**Belief path — restart the question, keep the lab.**

- Charter: **`docs/BELIEF_PATH.md`**
- Spine: vibrations → energy field → bind → electrons → atoms → molecules (information) → matter → collections with talent → brain
- **Live 3D default ON** for belief-path runners (`world/bet_live.py`); use `--headless` for batch/CI

### Latest belief-path results
| ID | Verdict | One-liner |
|----|---------|-----------|
| **BP-A1** | **PASS** | Local free-vibration **density** enables binding |
| **BP-B1** | **PASS** | Molecule composition fingerprint = content (engineered write) |
| **BP-B2** | **PASS** | Emergent species decades decode drive identity |
| **BP-C1** | **NULL** | Dual-drive talent: **population too sparse** (B4 fail) |
| **BP-C1b** | **NULL** | Population fixed (B4=1.0); specialisation **0.778 &lt; 0.90** — real but noisy |

Rungs **A** and **B** climbed. **Rung C** open with a **mapped near-miss** (majority specialisation, not acceptance). Pattern: `docs/patterns/dual_drive_collection_specialisation.md`.

### Next step (when resuming)
- **BP-C2** (only if pursuing talent further): probe-response selectivity after dual drive — new bars, not retune C1b’s 0.90.
- Or freeze Rung C as “partial/noisy structural specialisation” and document brain rung as blocked until talent is clean.
- Optional: BP-B3 multi-bit molecule alphabet; BP-A2 if proposing a new energy primitive beyond density.

---

## Settled threads (do NOT re-derive)

| Thread | Status | Bottom line |
|--------|--------|-------------|
| Binding hierarchy under current rules | **Mapped** | Electrons→atoms→molecules work; rules hand-specified |
| Proto-cell | **POSITIVE, scoped** | Forms, homeostasis; repair partial |
| Memory (activity) | **CLOSED NEGATIVE** | write≈leak |
| Memory (matter position) | **POSITIVE, scoped** | Selective multi-bit store |
| Communication | **POSITIVE, scoped** | Co-located codec only |
| EQMOD as optimizer / SA-CIM / VSA wins | **Archive** | Not belief path |

---

## Live 3D commands

```text
python tools/run_bp_a1_field_bind.py --smoke          # live default
python tools/run_bp_b2_emergent_species.py --smoke
python tools/run_bp_c1b_collection_talent_dense.py --smoke
python -m world gui                                   # free playground
# batch: add --headless
```
