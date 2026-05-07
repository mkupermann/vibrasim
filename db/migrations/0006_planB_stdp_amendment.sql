-- Plan B — STDP-R1 directional plasticity amendment.
-- Adds the amendment row + marks it implemented.
-- Run AFTER Plan B merges to main:
--   make db-migrate-planB-mark-implemented MERGE_SHA=<sha>

INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES (
    'STDP-R1',
    'STDP and directional bridge plasticity',
    'docs/superpowers/specs/2026-05-06-baby-brain-foundation-plan-B-stdp-design.md',
    'Per-tick STDP scan over firing_events (apply_stdp). Causal A→B firing pairs within τ_LTP strengthen bridge molecules in the A→B tube and update each bridge''s k_orientation 3-vector as a strength-weighted running average toward the unit A→B vector. Per-molecule alignment check: pairs that contradict an existing orientation (alignment < 0) trigger LTD (weaken only, orientation unchanged). Plus synaptic_transmission inside neuron_dynamics: strong oriented bridges deposit charge into post-synaptic level-4 atoms when aligned moving vibrations cross them.',
    'Without directionality, bridges record correlation but cannot represent causality. Plan B adds the asymmetry needed for prediction and sequential learning, validated end-to-end by P3 (single-bridge plasticity-driven prediction).',
    'proposed'
)
ON CONFLICT (number) DO NOTHING;

-- Marks it implemented; bound to the merge SHA via make target.
UPDATE amendments
SET status = 'implemented',
    impl_commit = :'merge_sha',
    decided_at = NOW()
WHERE number = 'STDP-R1';
