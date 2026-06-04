# GEO-13 — Composition depth (INCONCLUSIVE: degenerate setup)

## Result
Linear ancestry chains + normalized TransE: even 1-step parent inference = 0.08 (vs GEO-12's tree 0.82).

## Honest note — setup flaw, not a method finding
On a LINEAR chain, child+r≈parent forces ~12 collinear points; with unit-sphere normalization they cannot
embed (collapse), so training fails at the base relation. This is a degenerate fit between normalized
translational embeddings and chain topology — NOT evidence about composition depth. The composition-depth
question was already answered cleanly by GEO-2 on the GRID (clean translations): multi-hop holds with
graceful decay (1-hop 0.60 → 5-hop 0.38, vs chance 0.028). GEO-12 (tree) showed grandparent composition at
0.63. So: shallow composition is strong; depth decays gracefully on well-embedded structures; chains are a
poor fit for normalized TransE. No new claim from GEO-13. (Recorded to keep the honest trail; the broken
numbers are not used.)
