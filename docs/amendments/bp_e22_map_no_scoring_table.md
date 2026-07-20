# BP-E22 — Multi-trial partner map with **no** hidden scoring table

**PRE-REGISTERED 2026-07-20 before data (night scheduler)**  
**Depends on:** E20/E21 (peak/latch partner routing works when scored against table)  
**Discipline:** scoring uses **only** self-consistency + discriminability of empirical L→R routes; PAIRS table is write-side only, never used to score correctness of a “true partner”

---

## Hypothesis

**H-E22.** After multi-trial PRIM5 dual writes of two exclusive pairs (write-side known only to training), for every bridged L atom run latch end-state prop and record `(f_L, f_R*)` where `f_R*` = freq of R atom with max `k_latch`.

**Decoder / score (no pair table):**
1. Split L atoms into two groups by median of `f_L` (data-driven).  
2. Within each group, take modal `f_R*` (nearest of the two empirical R modes from all f_R*).  
3. **Self-consistency:** fraction of L atoms whose `f_R*` matches their group’s modal R ≥ **0.80**.  
4. **Discriminability:** the two groups’ modal R freqs differ by relative gap ≥ **0.25** (not collapsed to one partner).  
5. **Control rewire:** after random rewire of bridge R ends, self-consistency ≤ **0.55**.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat self-consistency | ≥ **0.80** |
| B2 | Treat group modal R relative gap | ≥ **0.25** |
| B3 | Rewire self-consistency | ≤ **0.55** |

Seeds `{681, 691}`, trials 12; T_train=6; N_write=10; latch ON; valence=0. Budget 180s / hard 360s.

## Prediction
🔮 PASS lean: exclusive links already route correctly; median split should recover two clusters.  
Most-likely miss: single L atom per class → median split unstable; or rewire still consistent by chance.

## NOT claimed
Unsupervised discovery of map from free chemistry; free talent; generative partner.

## RESULT
**NULL** (2026-07-20 night scheduler). B1_self_cons=**1.000**, B2_gap=**0.643**, B3_rewire=**0.917** (fail ≤0.55).

### Calibration
🔮 PASS lean — **MISS on B3**. With one L atom per exclusive pair, median groups are size-1 → self-consistency is **vacuously 1.0** even after rewire. Control definition inadequate for K=2 exclusive slots. No bar retune.

### Finding
Treat structure (cons+gap) looks right; rewire self-consistency is not a valid negative control at this cardinality.
