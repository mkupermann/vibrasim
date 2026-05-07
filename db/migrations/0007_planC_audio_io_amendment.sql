-- Plan C — AUDIO-IO-R1 audio I/O amendment.
-- Adds the amendment row + marks it implemented.
-- Run AFTER Plan C merges to main:
--   make db-migrate-planC-mark-implemented MERGE_SHA=<sha>

INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES (
    'AUDIO-IO-R1',
    'Live audio I/O — mic input + speaker output',
    'docs/superpowers/specs/2026-05-06-baby-brain-foundation-plan-C-audio-io-design.md',
    'AudioIO class with two background threads (sounddevice capture + playback) and two threading.Lock-protected circular numpy buffers. Encoder helpers (freq_to_port_position, encode_block, decode_to_audio) convert audio to and from substrate vibration emissions via log-mapped frequency-to-position pipeline. inject_into_substrate drains live mic audio, encodes blocks, injects vibrations at frequency-mapped positions in the input port. read_from_substrate samples firings inside the output port, inverse-log-maps to frequencies, decodes to audio, writes to playback buffer.',
    'Without live audio I/O, the substrate is silent — it cannot listen to or speak with the world. Plan C provides the audio half of the M4 glass-of-water demo (Plan E ties it together with video and reward).',
    'proposed'
)
ON CONFLICT (number) DO NOTHING;

UPDATE amendments
SET status = 'implemented',
    impl_commit = :'merge_sha',
    decided_at = NOW()
WHERE number = 'AUDIO-IO-R1';
