# JEP-50 — is the order>Poincare advantage driven by hierarchy IRREGULARITY? (the JEP-49-implied hypothesis)

## Motivation
JEP-49 refuted DEPTH as the driver (Poincare fine on balanced trees even deep) and implied IRREGULARITY (uneven
branching/depth) drives order's real-WordNet advantage. Direct test: compare both methods on a BALANCED tree vs
an IRREGULAR tree (random branching factor + variable depth) of similar size. If order pulls ahead on the
irregular one, irregularity is the driver. (This is my 4th mechanism hypothesis after 3 refutations - reported
honestly whatever it shows.)

## Pre-registration (locked BEFORE run)
- Balanced binary tree (depth 7, ~255 nodes) vs irregular tree (~250 nodes, random branching 1-4, variable
  depth). Held-out 30% IS-A, poincare vs order.
- CHARACTERIZATION: report the order-minus-poincare gap on balanced vs irregular. If gap is clearly larger on
  irregular -> irregularity confirmed as the driver. Established (Vendrov 2016, Nickel-Kiela 2017), named.

## Result — PARTIAL: irregularity NARROWS but does not FLIP the gap; mechanism investigation concluded
| tree | poincare | order | gap (order-poincare) |
|------|----------|-------|----------------------|
| balanced (255) | 0.910 | 0.859 | -0.051 |
| irregular (251) | 0.902 | 0.892 | -0.010 |

**VERDICT: PARTIAL - irregularity is PART of the driver, not the whole.** On the irregular tree order CAUGHT UP
(gap -0.051 -> -0.010) but Poincare still wins; the dramatic real-WordNet FLIP (order 0.91 >> Poincare 0.78) is
NOT reproduced by synthetic single-parent irregularity. The likely missing factor: real WordNet is a MULTI-PARENT
DAG (synsets have multiple hypernyms), which I did not synthesize. After FOUR mechanism hypotheses (depth JEP-49,
cross-branch precision JEP-46, cone precision JEP-47, irregularity JEP-50) - each refuted or only partial - the
honest conclusion is: the order>Poincare real-WordNet advantage ELUDES clean synthetic reproduction. That is
itself a finding (real lexical hierarchies have structure simple synthetic models miss). Per my own
docs/patterns/honest_evaluation.md (#1, #7: trust measurement over mechanistic stories), I CONCLUDE the mechanism
investigation here rather than chase a 5th hypothesis. The robust EMPIRICAL facts stand and are the deliverable's
guidance: order embeddings for is-a classification on real/irregular hierarchies; Poincare for grounding and
clean/balanced taxonomies. The WHY is incompletely understood and honestly labelled so. Untested factor (future):
multi-parent DAG structure. Established methods (Vendrov 2016, Nickel-Kiela 2017), named as such.
