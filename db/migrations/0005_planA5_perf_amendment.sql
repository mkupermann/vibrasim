-- Plan A.5 — PERF-A5 substrate-performance amendment.
-- Adds the row + marks it implemented in one go.
-- Run AFTER Plan A.5 merges to main:
--   make db-migrate-planA5-mark-implemented MERGE_SHA=<sha>

INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES (
    'PERF-A5',
    'Substrate performance — slot recycling + Numba JIT',
    'docs/superpowers/specs/2026-05-06-baby-brain-foundation-plan-A5-substrate-performance-design.md',
    'Reference-counted slot recycling in World.allocate_node + @njit cores for the five hot per-tick loops (decay_unstable_nodes, decay_high_level_nodes, move_nodes, apply_scale_repulsion, bind_nodes_upward). RNG rolls pre-generated in Python and passed to JIT cores so the RNG stream is preserved.',
    'Discovered during Plan A Task 9 when 60-sim-minute F1 projected at multi-hour wall-clock. Per-tick cost grew linearly with k_count (monotonic allocator + O(k_count) Python loops); total wall-time quadratic in sim-time. Required to make Plan A integration tests + Plan B-G integration tests feasible.',
    'proposed'
)
ON CONFLICT (number) DO NOTHING;

-- Marks it implemented; bound to the merge SHA via make target.
UPDATE amendments
SET status = 'implemented',
    impl_commit = :'merge_sha',
    decided_at = NOW()
WHERE number = 'PERF-A5';
