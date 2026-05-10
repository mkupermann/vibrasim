# Flux Substrate — Phase Log

Append-only build log. Each entry: date, phase, status, key decisions.

## 2026-05-10 — F0 start

- Spec committed at `2bab7a7`.
- Plan: `docs/superpowers/plans/2026-05-10-flux-substrate-F0.md`.
- Target: skeleton + T1 conservation test passes.
- Estimated 1 week solo.

## 2026-05-11 — F0 complete

- 9 plan tasks landed across 12 commits (`09f9488..750337b`).
- 33/33 flux tests pass (`tests/flux/`). 382 legacy tests untouched.
- T1 acceptance test green: energy conservation holds within 1e-9 relative tolerance per-tick across 1000 ticks of constant injection.
- README §"Two substrates" names legacy + flux side by side.

Known carry-overs into F1:
- **Spec §6 tick order**: spec lists `inject → absorb → move`; F0 implements `inject → move → absorb` per the F0 plan. Both preserve conservation. F1 should reconcile when adding `interact` and `structure-flux` steps.
- **`Quanta.add` is a pure-Python O(N) linear scan.** Adequate for F0 at 10×10×10/5 quanta-per-tick; will become the bottleneck after binding + plasticity. Numba-ify in F1 if profiling confirms.
- **Cleanup landed pre-F1**: `Quanta.remove_batch` encapsulates the previously-private cursor reset; `world/flux/__init__.py` now re-exports the public API; type hints unified on PEP-604 style.

F1 plan to be written next.
