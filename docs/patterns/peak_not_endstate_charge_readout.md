# Pattern: Peak charge readout, not end-state

## Source
E13 NULL · E14 PASS · E18 NULL · E19 NULL · E20 PASS

## Claim
`tau_membrane` decays `k_charge` between fires. Partner routing via `bridge_charge_prop` is **real on fire ticks** but **invisible at window end**.

## Do
- Track **peak** charge per target during the prop window (E14, E20).
- Re-drive source periodically if testing sustained opportunity.

## Don't
- Score end-of-window mean charge as evidence of failed routing (false NULL).
- Retune an end-state bar after seeing decay — open a peak metric under a **new** ID.
