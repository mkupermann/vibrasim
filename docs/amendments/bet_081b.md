# BET-081b — Pre-registered

Date: 2026-05-25 20:52

## Hypothesis
Feedback collapse caused by STDP depression killing L5->L6->L4 weights. Fix: w_min=0.05 floor on feedback synapses prevents full collapse.

## Parameter changes from BET-081 baseline
{
  "feedback_w_min": 0.05,
  "feedback_dApost": -0.012
}

## Acceptance bars (pre-registered BEFORE run)
| T81b_a | duration >= 4h wallclock |
| T81b_b | L5 active >= 50% |
| T81b_c | >= 3 distinct clusters (intra > inter + 0.05) |
| T81b_d | silhouette > 0.05 |
| T81b_e | feedback Gini syn_5_6 < 0.95 (feedback NOT dead) |

## Time budget
Realistic: 6.0h, Ceiling: 12.0h
