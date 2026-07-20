# BP-E101 — Soft 2×2 wide-sep dual-cut full restore + soft re-cut identity arm

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E81 full 2×2 restore; E94/E97 wide-sep re-cut doctrine  
**Discipline:** 2×2 crossbar with **wide y for L0/L1 and R0/R1** (sep≥18); soft re-cut 00 only after full restore

## Hypothesis
L0 y=12, L1 y=36, R0 y=12, R1 y=36; mids spaced accordingly. Soft dual-cut all four; restore all; soft re-cut arm 00 only.
1. After full restore: concurrent both R ON ≥0.80  
2. Soft-cut 00 → L0 only lights R1 (via 01 if present) or L0 fails R0; specifically R0 OFF when probing L0 if only 00 cut and 01 still up  
   Actually after full restore all arms: L0→R0 and L0→R1. Soft-cut 00: L0 should still light R1 via 01; R0 off from L0-only if we check R0 after L0 fire with 00 cut — wait L0 still has 01 to R1. R0 might still light via L1→10→R0.  
Better bars:
1. Full restore concurrent both ON ≥0.80  
2. Soft-cut 00 only → concurrent still both ON (redundancy) OR L0 isolation: L0→R0 OFF but L0→R1 ON ≥0.80  
3. L1 only still R1 ON and R0 ON (via 10,11) ≥0.75  

Simpler:
1. Full restore: L0 isolation identity fails (fan-out) — concurrent both ON ≥0.80  
2. Soft-cut 00 and 11 (identity diagonal) → identity broken: L0 lights R1 only if 01 up...  

Simplest honest bars matching E94 style:
1. After full restore concurrent both R ON ≥0.80  
2. Soft-cut all identity arms (00,11) → concurrent may still work via swap arms; instead soft-cut **only 00**: after L0 fire, R0 latch ≤0.25 if 00 was sole path to R0 from L0 — but 01 goes L0→R1 not R0. R0 still lit by L1→10.  
So for concurrent L0+L1: R0 gets charge from L1-10 and possibly residual.

Bars like E94 for arm 00 only on L0→R0 path:
1. After full restore, fire L0 alone: R0 ON and R1 ON (fan-out) ≥0.80  
2. Soft-cut 00: fire L0 → R0 OFF, R1 ON ≥0.80  
3. Fire L1 → R0 ON (via 10) and R1 ON ≥0.80  

## Bars
B1 L0 fan-out both R ≥0.80 · B2 after cut00 L0→R0 OFF R1 ON ≥0.80 · B3 L1 still both ≥0.80  

Seeds {2881,2891} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if mids for 00 and 01 are > soft radius apart. Miss if L0 port clustering confuses.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0.  
Full restore fan-out works; soft re-cut 00 fails to silence L0→R0 (B2=0). Residual 00 bridges or spatial I miss under this wide 2×2 layout.
