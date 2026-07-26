# BP-C81 — Free dual talent under graceful node capacity pressure (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C80; `graceful_capacity` never BP free dual  
**Discipline:** **new mechanism** = tight `n_nodes_max` + `graceful_capacity=True` free dual + wall vs ample capacity. Budget-fit T=500 N=250.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `graceful_capacity=True` and `n_nodes_max=96` (binding stops gracefully at cap — resource competition).  
Control: same inject with `graceful_capacity=False` and `n_nodes_max=8192` (ample; default crash-on-full path never hits).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction (L mean decade < R) | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {6821,6831} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Negative control

Ample-capacity control must not pass high order while treat does (B2≤0.80 and B4≥0.15).

## What is NOT claimed

Not that crashing-on-full is better. Not multi-trial port. Not C16. If treat crashes, verdict FAILED (bug) not NULL.

## Prediction

?? LEAN NULL. Tight capacity more often collapses pop (B3 fail) or randomises order; competition unlikely to create decade specialisation from free dual inject alone.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=0.0 B4=0.0.  
Tight graceful capacity (n_nodes_max=96) collapses treat dual-side L4+ pop; no free dual talent unlock. Ample control also unordered at this budget/seeds.

