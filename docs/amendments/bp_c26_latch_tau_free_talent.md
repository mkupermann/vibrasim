# BP-C26 — Free dual talent with **charge_latch_tau>0** (new free-talent mechanism)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16 family CLOSED PARTIAL; C24–C25 NULL  
**Discipline:** **new mechanism** = non-zero `charge_latch_tau` during free dual inject + wall — not dual-inject+decay alone, not port-seed, not local pair scaffold

## Hypothesis
Wall ON. Treatment: free dual inject L-low / R-high with `charge_latch_tau=2.0`.  
Control: same free dual inject with `charge_latch_tau=0` (default).  
Success: treatment ordered specialisation ≥0.90; control ≤0.80; delta ≥0.15.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment ordered mean_decade L < R | ≥0.90 |
| B2 | Control ordered | ≤0.80 |
| B3 | Treatment both sides populated | ≥0.80 |
| B4 | Treatment − control delta | ≥0.15 |

Seeds {4081,4091,4101} trials 3. T=1200. Box 80×50×50 mid=40. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN NULL. Latch half-life may not improve free dual decade specialisation; maps latch-tau free class.

## RESULT
**FAILED (time overrun)** (2026-07-20). Hard cap 30 min exceeded without completion. First attempt: RuntimeError node capacity exhausted at n_nodes_max=4096. Retry with n_nodes_max=16384 still no verdict within hard cap (wallclock >30 min, only start line). No bar retune. Infrastructure fix + re-run requires new pre-reg ID or written re-attempt under budget.
