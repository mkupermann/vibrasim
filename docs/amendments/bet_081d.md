# BET-081d — Pre-registered

Date: 2026-05-26 10:10

## Hypothesis
Homeostatic plasticity on feedback synapses: if mean weight drops below threshold, potentiation is boosted. Biological: synaptic scaling.

## Parameter changes from BET-081 baseline
{
  "feedback_homeostasis": true,
  "feedback_target_mean_w": 0.1
}

## Acceptance bars (pre-registered BEFORE run)
| T81d_a | duration >= 4h wallclock |
| T81d_b | L5 active >= 50% |
| T81d_c | >= 3 distinct clusters |
| T81d_d | silhouette > 0.05 |
| T81d_e | feedback Gini syn_5_6 < 0.95 |

## Time budget
Realistic: 6.0h, Ceiling: 12.0h
