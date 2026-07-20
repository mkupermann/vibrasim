# BP-E127 — Dual 3-hop soft wipe-restore then **multi-site** hard re-cut path0 hops

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E123–E125 CLOSED NULL (single I0 mid re-cut fails); E124 hard single-site fails  
**Discipline:** **new mechanism** = multi-site hard kill along path0 (L0-A0 mid, A0-B0 mid, B0-R0 mid), not single I0 port only

## Hypothesis
Same geometry as E123. Soft dual-cut I0+I1; full restore both; hard-cut at three path0 hop mids M_LA0, M_AB0, M_BR0 (not only I0).
1. Both initial ON ≥0.80  
2. Both after wipe-restore ON ≥0.80  
3. Multi-site hard re-cut path0: path0 OFF ∧ path1 ON ≥0.80  

## Bars
B1 both initial ≥0.80 · B2 both after wipe-restore ≥0.80 · B3 multi-site re-cut ≥0.80  

Seeds {3461,3471} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS if single mid-port miss left residual hop bridges; multi-site severs full path0. NULL if restore rebuilds faster than multi-kill covers.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Multi-site hard re-cut along path0 hops after soft wipe-restore still fails. Single-I0 and multi-site re-cut classes both fail post wipe-restore on dual 3-hop (E123–E127).
