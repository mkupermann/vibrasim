# BP-B4 — Emergent multi-band molecule/atom content (Rung B)

**PRE-REGISTERED** 2026-07-19 · headless lab · no live 3D  

## Hypothesis
Three free-vibration frequency **drives** produce emergent level≥4 matter whose mean atom-decade decodes the drive label (0/1/2) above chance — multi-class extension of BP-B2 without hand-planted molecules.

## Drives (locked)
| Label | freq_min | freq_max |
|-------|----------|----------|
| 0 | 100 | 800 |
| 1 | 800 | 3000 |
| 2 | 3000 | 12000 |

## Decode (locked)
mean floor(log10(k_freq)) over alive level≥4 nodes:
- < 2.7 → 0  
- < 3.5 → 1  
- else → 2  

If no level≥4 nodes → incorrect.

## Arms
- T: three drives, decode as above  
- C1: all labels use band [100,12000] (same)  
- C2: shuffle labels vs T fingerprints  
- C3: decode by n_nodes tercile only  

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | T acc | ≥ 0.75 |
| B2 | C1 acc | ≤ 0.45 |
| B3 | C2 acc | ≤ 0.45 |
| B4 | C3 acc | ≤ 0.50 |
| B5 | T fraction with ≥1 level≥4 | ≥ 0.80 |

Chance ≈ 0.33.

## Protocol
N=15 trials/seed (5 per label), seeds {81,83}, T=1000 ticks, box 60³, n_initial=600, r_2=28, ftol=0.03, session3b-like.

## RESULT
**NULL** (2026-07-19 headless). B1=0.133, B5 pop=0.467; controls OK. Three narrow bands don't form enough level≥4 matter / separable decades at this scale.
