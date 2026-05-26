# BET-081c — Pre-registered

Date: 2026-05-26 05:30

## Hypothesis
Feedback needs lower STDP depression to survive. dApost=-0.004 (vs -0.012) on L5->L6 and L6->L4.

## Parameter changes from BET-081 baseline
{
  "feedback_dApost": -0.004,
  "feedback_dApre": 0.008
}

## Acceptance bars (pre-registered BEFORE run)
| T81c_a | duration >= 4h wallclock |
| T81c_b | L5 active >= 50% |
| T81c_c | >= 3 distinct clusters |
| T81c_d | silhouette > 0.05 |
| T81c_e | feedback Gini syn_5_6 < 0.95 |

## Time budget
Realistic: 6.0h, Ceiling: 12.0h
