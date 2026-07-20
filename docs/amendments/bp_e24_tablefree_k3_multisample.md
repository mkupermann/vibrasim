# BP-E24 — Table-free map K=3 with multi-sample per band

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E22/E23 CLOSED PARTIAL (K=2 size-1 groups)  
**Discipline:** reopen table-free only with **K≥3 multi-sample**; no E22/E23 bar retune

---

## Hypothesis

**H-E24.** With **3 exclusive pairs** and **2 spatial slots per pair** (distinct port y-offsets so multislot/radius yields ≥2 L atoms per L-band):

After multi-trial PRIM5 `apply_ilw_pair_write` train + latch partner readout (no pair table in score):

1. Cluster L by **tertiles** of `f_L` (3 groups).  
2. **Self-consistency:** fraction of L whose partner `f_R*` matches its group’s mean-R nearest among 3 group means ≥ **0.80**.  
3. **Discriminability:** minimum pairwise relative gap among the 3 group mean-R ≥ **0.20**.  
4. **Rewire control:** after random R-endpoint rewire, self-consistency ≤ **0.55**.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat self-consistency | ≥ **0.80** |
| B2 | Treat min pairwise modal-R gap | ≥ **0.20** |
| B3 | Rewire self-consistency | ≤ **0.55** |
| B4 | ≥2 L atoms in ≥2 distinct L-bands (multi-sample sanity) | ≥ **0.90** of trials |

## Protocol
Seeds `{781, 791}`, trials 10; T_train=9 episodes; N_write=6 per episode pair-slot;  
pairs `{(400,7000),(1500,2500),(5000,800)}`; slots `y∈{13,37}` (sep > 2×ilw_radius);  
latch ON; valence=0. Smoke: 1 seed × 3 trials. Budget 200s / hard 400s.

## Prediction
🔮 LEAN PASS: exclusive links + multi-sample should make rewire hurt consistency.  
Most-likely miss: B3 rewire still high if charge routes by freq not bridge; or B4 fails if multislot merges slots.

## NOT claimed
Free talent; unsupervised free chemistry map.

## RESULT
**NULL** (2026-07-20). B1_cons=**1.000**, B2_gap=**0.643**, B3_rewire=**0.633** (fail ≤0.55), B4_multi=**1.000**.

### Calibration
🔮 lean PASS — **MISS on B3**. Multi-sample works (B4). Treat routing self-cons+gap strong. Rewire drops cons from ~1.0→0.63 but not under 0.55 (random bipartite still partly tertile-consistent).

### Finding
K≥3 multi-sample **fixes** E22 size-1 vacuity (B4 PASS). Rewire remains a **weak negative control** for table-free claim (0.63>0.55). No bar retune.
