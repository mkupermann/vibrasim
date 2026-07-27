# BP-E191 — Incomplete cascade negative control (missing last hop fails fire-select)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E186 full two-hop cascade PASS; E187 mid-hop critical  
**Discipline:** **new question** = train path0 with L–M only (no M–R hop); fire L must **not** select R; full path1 still selects. Honest negative control for hop chain necessity (not mid-hop kill farm).

## Hypothesis
Path0: train only L0–M0 (freqs 400→1200); **omit** M0–R0.  
Path1: full L1–M1–R1.  

1. Fire L0: path0 select **fails** ≥0.80 (no R0 latch win)  
2. Fire L1: path1 select **succeeds** ≥0.80  
3. Control full path0 train (fresh world): fire L0 select ≥0.80  

## Bars
B1 incomplete p0 fail ≥0.80 · B2 full p1 select ≥0.80 · B3 full p0 control ≥0.80  

Seeds {5141,5151} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS. Missing terminal hop should block R select; complete paths work.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Missing terminal hop blocks R fire-select; complete paths work. Cascade hop chain is necessary end-to-end (complements mid-hop kill E187).
