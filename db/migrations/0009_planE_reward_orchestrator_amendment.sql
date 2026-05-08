-- Plan E — REWARD-R1 reward channel + closed-loop orchestrator amendment.
-- Adds the amendment row + marks it implemented.
-- Run AFTER Plan E merges to main:
--   make db-migrate-planE-mark-implemented MERGE_SHA=<sha>

INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES (
    'REWARD-R1',
    'Reward channel + closed-loop orchestrator (AgentLoop)',
    'docs/superpowers/specs/2026-05-07-baby-brain-foundation-plan-E-reward-orchestrator-design.md',
    'Closed-loop orchestrator (AgentLoop with stepped + real-time modes) and reward channel (RewardChannel with fire_positive / fire_negative). Asymmetric STDP physics: tristate k_reward_polarity (-1, 0, +1) on nodes; apply_stdp swaps LTP/LTD when atom_j has k_reward_polarity = -1. M4 (glass-of-water demo) and M5 (reward shaping) acceptance tests; pre-registered thresholds in tests/acceptance.toml.',
    'Without a reward channel and closed-loop orchestrator, the substrate cannot learn associations under supervision and cannot run continuously in real time. Plan E ties Plans A-D together: audio I/O (C) + video I/O (D) + substrate physics (A/B) are now orchestrated by AgentLoop, and RewardChannel provides the programmatic signal that drives asymmetric STDP learning.',
    'proposed'
)
ON CONFLICT (number) DO NOTHING;

UPDATE amendments
SET status = 'implemented',
    impl_commit = :'merge_sha',
    decided_at = NOW()
WHERE number = 'REWARD-R1';
