# GEO-32 — Capstone: integrated grounded QA agent on a realistic mini-KB (dogfoods GeometricReasoner)

## Motivation
Each capability was shown in isolation. GEO-32 runs them TOGETHER as one usable agent on a coherent mini
knowledge base, using the packaged tools/geometric_reasoner.py (so the module is proven usable, not just the
experiments). Measures: semantic (non-lexical) Q, multi-hop, abstention on out-of-KB Q, symbolic
aggregation, and runtime update — end to end.

## Pre-registration (locked BEFORE run)
- Mini-KB: a small company domain — ~10 employees (role + team + city facts), giving ~30 facts.
- Test set (locked): (a) 5 semantic questions using ROLE descriptions not names (non-lexical); (b) 3
  multi-hop (person->team->city); (c) 3 out-of-KB questions that must ABSTAIN; (d) 2 aggregation counts;
  (e) 1 runtime update then re-query.
- Metric: per-category accuracy + overall. Bars: semantic >=0.6, multi-hop >=0.6, abstain >=0.8, aggregate
  exact, update flips. PASS if all categories meet bars (the integrated agent works on a realistic task).
- Honest: this reuses small clean entities; it demonstrates the system integrates + is usable, not scale.

## Result — PARTIAL (integration works; abstention needs calibration)
| category | result | bar |
|----------|--------|-----|
| (a) semantic role questions | **1.00** | >=0.6 PASS |
| (b) multi-hop person->city | **1.00** | >=0.6 PASS |
| (c) abstain on out-of-KB | 0.67 (2/3) | >=0.8 MISS |
| (d) aggregation counts exact | yes (Boston 3/Denver 3/Austin 2/Seattle 2) | exact PASS |
| (e) runtime update flips | yes (Alice -> Chicago) | flip PASS |

**VERDICT: PARTIAL.** The integrated agent (running on the packaged GeometricReasoner) works end-to-end on
4/5 categories at the bar — semantic non-lexical role resolution, multi-hop chaining, symbolic aggregation,
and runtime update all perfect. The miss is abstention: at a FIXED, uncalibrated tau=0.40 it caught only 2
of 3 out-of-KB questions. This confirms the GEO-23 lesson — grounded abstention requires per-KB threshold
CALIBRATION (GEO-23 calibrated tau on a held-out split and got 1.00); a guessed constant is unreliable. NOT
retuned post-hoc. **Honest takeaway:** the system integrates and is usable; deploying it means calibrating
the abstention threshold on a small dev set (answerable vs out-of-KB), exactly as GEO-23 prescribes. Caveat
added to the module docs.

## GEO-32b — calibration did NOT fix abstention; an honest grounding refinement
Calibrating tau on a labelled dev set (GEO-23 method) gave tau=0.41 (~ the guessed 0.40) and abstention
stayed 0.67. Diagnosis: the failing question "Who is the CEO?" has maxsim 0.434 (nearest "Frank is a product
manager...") — it is DOMAIN-ADJACENT (CEO ~ manager/role) though no CEO is stored; the genuinely out-of-
domain questions abstain fine (capital of France 0.14, stock price 0.18).

**Honest refinement of the grounding claim (GEO-23):** similarity-threshold abstention reliably rejects
OUT-OF-DOMAIN questions (low similarity) but NOT IN-DOMAIN-but-unanswerable ones (a question that looks like
the stored facts but has no actual answer). GEO-23 scored 1.00 because its unanswerable questions (other
countries) were genuinely dissimilar; the harder in-domain-unanswerable case needs ANSWER VERIFICATION (does
the retrieved fact entail an answer to the question?), which a retrieval threshold alone cannot do. The
calibrate_abstention() helper (added to the module) is still the right tool for the out-of-domain case, but
its limit is now documented. This bounds grounding honestly: geometry filters relevance, not answerability.
