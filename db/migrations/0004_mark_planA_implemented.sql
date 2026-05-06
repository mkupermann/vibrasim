-- Plan A — mark substrate growth amendments as implemented.
-- Run AFTER Plan A merges to main. The merge commit SHA gets recorded by the
-- Makefile target `make db-migrate-planA-mark-implemented MERGE_SHA=<sha>`.
UPDATE amendments
SET status = 'implemented',
    impl_commit = :'merge_sha',
    decided_at = NOW()
WHERE number IN ('R1', 'R2', 'PHASE3-R1');
