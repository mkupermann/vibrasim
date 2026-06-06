# Pattern — Engineered port wall (specular reflection) for robust activity containment

**What it is.** A config-gated tick step (`apply_engineered_compartment`, no-op when
`compartment_k=0`) that confines free vibrations to an engineered sphere by reflecting any
that reach the boundary moving outward. The charter sanctions this as ENGINEERED topology
(CONCEPT §4.8 ports are engineered; internals emerge). It is the only memory-programme
mechanism that proved robust across seeds.

**The mode matters — use specular, not clamp or soft.** Three reflection rules were tested
on the same task (G33, G35, G36, G37):
- `clamp` (snap reflected vibrations to r = R·0.999): contains firing 259× but collapses all
  vibrations onto one degenerate shell, erasing the interior field → it SUPPRESSES whatever
  the interior dynamics were doing (e.g. killed a co-firing write entirely, |E|=0).
- `soft` (revert the overshoot only, pos − v·dt): preserves the interior but LEAKS — fast or
  tangential vibrations escape over successive ticks → containment incomplete.
- `mirror` (specular: r → 2R−r, keep inward speed): contains FULLY (no r>R persists) WITHOUT
  pinning — reflected vibrations stay distributed through the interior. **This is the one to
  use.** Robust firing containment 175–330× across seeds {42,7,99} (G37/G38/G39).

**Recipe.**
1. Reflect alive free vibrations with r ≥ R and outward radial velocity (v·n̂ > 0).
2. Flip the radial velocity component inward: v ← v − 2(v·n̂)n̂.
3. Mirror the radial position: r → 2R − r along n̂ (clip to [0, R·0.999]).
4. Touch only free vibrations, never bound atoms — the contained region's structure is
   undisturbed (verify with a "structure survives" bar).

**What it does and does NOT buy you.**
- DOES (robust): isolate a firing/activity compartment — emissions inside stay inside,
  outside stimuli stay outside. A reliable engineered module boundary.
- Does NOT (shown by G33–G39): by itself yield selective persistent MEMORY. Containment is
  necessary but not sufficient; the co-firing/bistable write produces only a tiny (1–6),
  stochastic, sometimes-non-persistent strong-bridge engram regardless of containment or
  input drive. Use the wall for what it robustly provides (activity modularity), not as a
  memory fix.

**Where it applies.** Building engineered modular compartments / ports: isolating activity
to a region, preventing cross-talk between regions, bounding a stimulus's reach. See
docs/amendments/g33–g39 and MEMORY_PROGRAMME_SUMMARY (2026-06-02 update).
