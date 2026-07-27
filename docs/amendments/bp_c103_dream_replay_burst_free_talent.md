# BP-C103 — Free dual talent with dream_replay_burst_size (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C102; C13 dream free dual NULL; `dream_replay_burst_size` never BP free dual treatment  
**Discipline:** **new mechanism** = dream ON + elevated replay burst size free dual + wall vs default burst. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `dream_mode_enabled=True`.  
Treatment: `dream_replay_burst_size=16`.  
Control: `dream_replay_burst_size=8` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7901,7911} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Larger dream replay burst unlikely to unlock free dual decade specialisation.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.75 B3=0.25 B4=-0.75.
Larger dream replay burst (16 vs 8) did not unlock free dual decade specialisation — treatment scored *below* control on ordered fraction (negative delta), the opposite of an unlock. Extends the free-dual NULL farm C27–C102; `dream_replay_burst_size` is not a free-chemistry talent lever.
