# JEP-22 — robustness of the world-model agent under STOCHASTIC transitions (action slip)

## Motivation
All EQMOD-4 navigation used deterministic transitions. Real environments are stochastic. The SR is DEFINED via
expected discounted occupancy under a policy, so it should naturally handle transition noise; and SR-value
planning is closed-loop (re-decides from the ACTUAL state each step), so it should self-correct from slips. This
rung tests that and finds where it breaks.

## Pre-registration (locked BEFORE run)
- Looped maze. Transitions are STOCHASTIC: the chosen action succeeds with prob (1-eps); with prob eps the agent
  slips to a uniformly random neighbour. SR learned by LOCAL TD on the SAME stochastic dynamics.
- Closed-loop SR-value policy: each step pick the neighbour maximizing M[neighbour, goal], execute (stochastic),
  repeat. Measure goal-reaching within budget.
- Sweep eps in {0.0, 0.1, 0.2, 0.3, 0.5}. Bars: reach >= 0.9 up to eps=0.2 (robust to moderate noise) AND
  graceful (monotone) degradation beyond; report the curve. PASS = the agent is robust to realistic transition
  noise. NULL if it breaks at low noise. SR / closed-loop control established - named as such.
