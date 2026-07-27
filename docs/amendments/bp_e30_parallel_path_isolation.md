# BP-E30 — Parallel path isolation (two chains)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E29 two-hop PASS

## Hypothesis
Two exclusive chains (no midplane; r₂ large enough):
- Chain1: L1(x=12)–M1(x=35)–R1(x=58) freqs 400–1500–5000  
- Chain2: L2(x=18)–M2(x=42)–R2(x=65) freqs 800–2500–7000  

PRIM5 pair-links L–M and M–R per chain. Force-fire **L1 only**.  
Peak latch on **R1 ≥ 1.0** and peak latch on **R2 ≤ 0.25** in ≥ **0.85** of trials.  
Control fire **all L**: both R1 and R2 peaks ≥1.0 in ≥0.80 trials.  
Both chains have ≥2 bridges each ≥0.90.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Fire L1: R1 peak latch ≥1.0 rate | ≥0.85 |
| B2 | Fire L1: R2 peak latch ≤0.25 rate | ≥0.85 |
| B3 | Fire all L: both R1&R2 ≥1.0 rate | ≥0.80 |
| B4 | Treat both chains ≥2 bridges | ≥0.90 |

Seeds {981,991} trials 10. Smoke 1×3.

## Prediction
🔮 PASS lean: exclusive links isolate paths. Miss: spatial proximity cross-links.

## RESULT
**NULL** (2026-07-20). B1=0 B2=1.0 B3=0 B4_bridges=**0**.  

### Diagnosis
`ilw_pair_replace_enabled=True` kills L–M when writing M–R (M endpoint replace). Multi-hop chains **incompatible** with replace-on. E29 used replace OFF.
