-- Plan D — VIDEO-IO-R1 video I/O amendment.
-- Adds the amendment row + marks it implemented.
-- Run AFTER Plan D merges to main:
--   make db-migrate-planD-mark-implemented MERGE_SHA=<sha>

INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES (
    'VIDEO-IO-R1',
    'Live video I/O — webcam input via retinotopic patch encoder',
    'docs/superpowers/specs/2026-05-06-baby-brain-foundation-plan-D-video-io-design.md',
    'VideoIO class with one background webcam capture thread (lazy cv2 import) and a deque frame buffer. Encoder helpers (downsample_frame, build_oriented_filter_bank, encode_frame, patch_to_port_position, feature_magnitude_to_frequency) produce retinotopic patch+orientation features from each frame. inject_into_substrate reads the most-recent buffered frame, encodes it, injects one vibration per feature at its frequency-mapped port position. Input only — no read_from_substrate, the substrate doesn''t dream pictures yet.',
    'Without live video I/O, the substrate is blind — it cannot see the world. Plan D provides the video half of the M4 glass-of-water demo (Plan E ties it together with audio and reward).',
    'proposed'
)
ON CONFLICT (number) DO NOTHING;

UPDATE amendments
SET status = 'implemented',
    impl_commit = :'merge_sha',
    decided_at = NOW()
WHERE number = 'VIDEO-IO-R1';
