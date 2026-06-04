# GEO-4 — Distance-preserving embedding recovers CLEAN geometric understanding

## Result (grid; classical MDS on graph shortest-path distances)
| metric | hits@1 | (TransE, GEO-3) |
|--------|--------|------------------|
| analogy (b−a)+c → d | **0.76** | 0.25 |
| composition right+up → diagonal | **1.00** | 0.52 |

**VERDICT: PASS** — a metric embedding makes BOTH analogy and composition strong.

## Finding — the EMBEDDING METHOD is decisive for geometric understanding
A distance-preserving embedding (MDS / spectral; could also be force-directed or UMAP) recovers the clean
underlying geometry, so analogy (0.76) and composition (1.00) both work — vs margin-trained TransE which
left the space noisy (0.25 / 0.52). So EQMOD-3's core thesis holds GIVEN the right method: a metric
geometric concept space supports compositional + analogical reasoning — the structural core of
understanding. Methodological rule for the programme: build the space to preserve relational DISTANCES
(metric), not just satisfy margins. Next: test on REAL relational/semantic structure (and the LLM bridge).
