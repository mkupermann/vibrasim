# Pattern — Durable, growing, directed VSA relational memory

**What it is.** A substrate-native memory that stores typed relational facts, persists to disk, grows without a
fixed ceiling, and supports transitive multi-hop inference — built entirely from VSA primitives (`world/vsa`), no
transformer/pretrained model. Implemented in `world/substrate_memory.py :: SubstrateMemory`. Established methods
(HRR/VSA binding, modular capacity, permutation binding, instance-based cleanup), named as such — the value is the
substrate-native assembly + the measured limits, not new mathematics.

## The five mechanisms (each earned in an amendment)

1. **Role-filler binding for instances (JEP-294).** A fact `(entity, role, value)` is stored as
   `bind(bind(entity, role), value)` superposed (bundled) into a module vector. Distinct instances that share a
   concept stay distinct: `bind(germany, politics)` ≈⊥ `bind(hungary, politics)` (sim ~0), so a property attaches
   to the bound instance, not the shared concept. **Capacity law:** one module holds ≈ **D/32** facts before the
   bundle blacks out; linear in D (64/128/256 at D=2048/4096/8192). Untaught keys are separable (rejectable).

2. **Durable persistence (JEP-295).** `save(dir)` → a folder (`vectors.npz` + `meta.json`); `load(dir)` rebuilds
   exact state. **Critical detail:** atom vectors are derived deterministically from the symbol name via
   **hashlib** seeding (NOT Python's builtin `hash()`, which is per-process salted) — so a *separate process*
   reconstructs identical vectors. Survives close+reopen and grows across sessions without forgetting.

3. **Unbounded growth / neurogenesis (JEP-296).** When the current module reaches ~0.8·K* facts, a new empty
   module is auto-added; `query` searches all modules and takes the best cleanup match. Total capacity is linear
   in #modules. 384 facts where a single bundle → 0.38 recover 0.98 across 4 modules.

4. **Directed edges via permutation (JEP-298).** Plain Hadamard binding is **direction-ambiguous** (commutative +
   self-inverse → a node retrieves children as well as parents; this sank the first multi-hop attempt, JEP-297
   NULL). Fix: store the value **permuted**, `bind(entity*role, ρ(value))` with `ρ = np.roll`; forward query
   applies `ρ⁻¹` and recovers a clean value, a backward probe yields `ρ(x)·x` noise the cleanup rejects. Enables
   transitive climbing. Gated behind `directed=` so the symmetric key→value path is unchanged.

5. **Gated multi-hop inference + membership probe (JEP-298/300).** Transitive relations (is-a, part-of) are
   answered by climbing: iterate `query(node, role)`, accept a parent only if cleanup sim ≥ a gate, stop when none
   clears it. The gate is set ONCE from held-out calibration facts as the midpoint of taught vs untaught edge
   similarity (derived from data, never tuned on the test). Multi-valued relations (causal, property) use
   `contains(entity, role, value, gate)` = max-over-modules edge similarity ≥ gate.

## Bridging a symbolic engine (JEP-299/300)

The Understanding Engine's learned graphs (`parents`, `part_of_g`, `causes`, `properties`) bridge in directly via
`add_fact(a, role, b)` with one role vector per relation. After save→reload (engine discarded) the substrate alone
answers multi-hop and membership questions matching the engine **1.000** across is-a/part-of/causal/property. So a
symbolic reader's full knowledge can live in the durable substrate and be reasoned over after a restart.

## When to use / when not

- **Use** for: durable content-addressable knowledge that must survive restarts, accumulate over sessions, keep
  instances distinct, and support transitive queries — without any learned/pretrained component.
- **Limits (honest):** per-module capacity ≈ D/32 (widen D or add modules); the taught/untaught margin narrows at
  very high load (reliable "I don't know" then needs per-relation gates or a routing key); **cross-relation
  inheritance** (part-of across is-a, property inheritance down is-a) is NOT done by a single-relation climb — that
  is multi-relation reasoning left to the engine or a future amendment.

## Reusable API
`SubstrateMemory(D, directed=)`, `add_fact(e,r,v)`, `query(e,r)→(value,sim)`, `contains(e,r,v,gate)`,
`save(dir)`/`load(dir)`; `atom_vector(name, D)` for cross-process-stable symbol vectors.

Amendments: docs/amendments/jep29{4,5,6,7,8,9}_*.md, jep300_multirelational_bridge.md.
