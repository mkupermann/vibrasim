# JEP-14 — what the SR abstraction transfers: reward-revaluation YES, transition-revaluation NO

## Motivation
JEP-13: compact bases abstract value for TRANSFER, not greedy control. The cleanest established transfer claim
is the SR's: value = M @ r, so changing the REWARD r gives an INSTANT new value function (no relearning) -
reward revaluation. But the SR is tied to the transition policy/structure, so changing TRANSITIONS (block a
passage) makes the cached SR STALE - it cannot revalue without relearning (Momennejad et al. 2017). This rung
quantifies exactly what the SR abstraction buys and where it breaks - an honest map of this abstraction.

## Pre-registration (locked BEFORE run)
- Maze (DFS tree), SR learned by LOCAL TD. 
- (A) REWARD revaluation: for N novel reward vectors r (random goal/reward placements), compute V=M@r with ZERO
  relearning; plan (greedy or MPC) to the reward. Bar: reach >= 0.9 instantly.
- (B) TRANSITION revaluation: BLOCK one passage (remove an edge), creating a detour. For goals whose optimal
  path used that edge: (i) STALE SR (old M) planning in the changed maze - expect FAILURE/degradation (quantify);
  (ii) after TD-RELEARNING M in the changed maze - expect RECOVERY >= 0.9.
- PASS-as-characterization: (A) reach >= 0.9 (reward transfer works) AND (B-i) stale reach << (B-ii) relearned
  reach (transition change needs relearning). This is the honest SR abstraction boundary. SR (Dayan 1993;
  Momennejad 2017) established - named as such.
