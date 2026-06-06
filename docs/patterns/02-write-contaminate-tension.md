# Pattern 02 — The same coupling both writes and corrupts; you cannot null one without nulling the other

**Discovered:** 2026-05-31, during BET-099/100 (correlation memory).
**Status:** empirical.
**Substrate evidence:** firing emission with `n_emit=8` wrote selective memory
(co-firing of bridged neighbours potentiated their bridge) but also propagated
firing into the control region and corrupted selectivity over time. Setting
`n_emit=0` removed the propagation — and removed the write entirely (no co-firing
pairs formed; all bridges stayed at baseline). The single coupling (emission)
was simultaneously the write mechanism and the corruption mechanism. See
docs/amendments/bet_099_correlation_memory.md, bet_100_robust_selective_recall.md.

## The mechanism

In a coupled dynamical system, the channel that lets a signal WRITE (propagate
to where it must act) is frequently the SAME channel that lets it LEAK (spread to
where it must not). Turning the channel up gets you write + contamination;
turning it off gets you neither. There is no global gain that yields write
without leak — the fix has to change the channel's SHAPE (its locality, its
selectivity, its timing), not its magnitude.

Symptom to recognise: you fix confound A by reducing a coupling, and a different
confound B appears (the effect you wanted disappears). You reduce B by raising
the coupling, and A returns. If two successive "fixes" trade the same knob in
opposite directions and neither passes, you are not tuning — you are oscillating
on a single over-loaded coupling.

## Why it works

A scalar gain on a shared channel moves write and leak together; they are
co-monotonic in that parameter. Decoupling them requires a NEW degree of freedom
that the scalar didn't expose — e.g. make the coupling local (short range) so it
reaches intended targets but not distant ones, or gate it by a key so only
matching destinations receive it. The resolution lives in a dimension orthogonal
to the gain.

## Reusable form

1. Name the coupling you are tuning and write down BOTH things it does — the
   effect you want and the side effect you are fighting.
2. If they move together under your knob (co-monotonic), STOP tuning that knob.
3. Find an orthogonal degree of freedom that separates them: **locality**
   (range/decay), **selectivity** (a key/address/type filter), or **timing**
   (a window that includes targets, excludes others).
4. Change the channel's shape along that dimension; keep its gain where write works.

## Real-world / business mapping

- **Notifications**: the channel that reaches the right user (broadcast) also
  spams everyone. Fix is not "fewer/more notifications" (gain) — it is targeting
  (selectivity), not volume.
- **Caching/replication**: the propagation that keeps replicas fresh (write) also
  spreads a poisoned value (leak). The fix is scoping/validation (shape), not TTL
  (gain).
- **Microservice retries**: retries that deliver through transient failures
  (write) also amplify load storms (leak). Fix is jittered/circuit-broken
  locality, not retry count.
- **Teaching/comms**: the candor that builds trust (write) can also wound (leak).
  The lever is framing/timing (shape), not "more/less honesty" (gain).

## Failure modes pre-registered

- Mistaking an over-loaded coupling for a missing mechanism — wasting effort
  adding machinery when the fix is reshaping an existing channel.
- "Splitting" the channel in a way that secretly re-introduces a global gain
  (e.g. a "local" range still larger than the separation you need).
- Declaring the orthogonal fix without measuring that write survives it (BET-100
  killed write while removing leak — the fix must preserve the wanted effect).

## Empirical evidence

BET-099 (n_emit=8): selective write + persistent recall ~3000 s, but control
contaminated after ~6500 s (propagation). BET-100 (n_emit=0): firing contained
(ratio 125) but zero potentiation — write gone. Two fixes, same knob, opposite
directions, neither passes → over-loaded coupling. Proposed orthogonal fix
(BET-101): LOCAL emission (short range) — write to neighbours without long-range
leak.
