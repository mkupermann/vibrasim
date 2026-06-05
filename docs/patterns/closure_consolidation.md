# Pattern — Closure consolidation (remove the hops that compound)

## Problem
Multi-hop reasoning over a VSA relational store (e.g. deep `is_a` across a depth-8 taxonomy) walks the graph hop by
hop. Each hop is a routed cleanup with small similarity noise; over a deep chain the per-hop error **compounds
multiplicatively** (per-hop 0.98 → 0.98^8 ≈ 0.85), and adversarial conjunctions compound it further. Raising the
vector dimension D does **not** fix this — it only shrinks per-hop error as ~√(load/D), which cannot beat
multiplicative compounding (measured: JEP-369 NULL — even D=16384 with a single module leaves deep is-a at ~0.85).

## Mechanism
**Materialize the transitive closure as a consolidation step**: for a transitive relation `rel`, store every
node→ancestor edge directly, so a deep query becomes a **single-hop lookup that does not compound**. This is the
relational analogue of the substrate's dream consolidation (G15/G18): an offline pass that turns derived, multi-step
knowledge into directly-stored facts.

`SubstrateMemory.consolidate_closure(relations=("isa",))`:
- builds the direct-parent map for each `rel` from live facts,
- walks ancestors, **skipping any edge denied by a `not_<rel>` exception** (so consolidation never bridges through a
  negation — it adds only true edges),
- adds the missing transitive edges into a fresh store,
- is **idempotent** (re-running yields the same fact set) and preserves all original answers.

The existing single-gate `BrainQuery.is_a` then resolves deep chains in one hop automatically — no query-side change.

## Evidence
- **JEP-370 PASS:** at ~360 base facts / depth 8, closure restores deep is-a 0.975–1.0 and adversarial composition
  0.875–1.0 (BASE multi-hop collapsed to 0.625), with no distractor false-positive inflation.
- **JEP-371 (PARTIAL/capability PASS):** the deployed `BrainQuery.is_a` reaches 1.0 on deep chains after consolidation,
  exceptions respected (no bridge through `not_isa`), idempotent, full suite green (23 passed).

## Trade-off & when to use
- **Cost:** storage grows ~depth× (a depth-8 taxonomy: 363 → ~2300 facts). This is a **tunable storage-for-accuracy**
  lever — unlike D, it actually removes the compounding.
- **Use when:** within-domain deep reasoning must be reliable at scale (the "no mistakes in a taught domain" goal).
- **Re-run** after large ingests (it is idempotent and exception-safe). Pairs with `compact()` (reclaim resolved
  corrections) — compact first, then consolidate.

## Query side: consolidation-aware is-a (JEP-375)
Once a relation's closure is materialized, mark it on the store (`SubstrateMemory.closed_relations`, persisted through
save/load) and answer is-a by **direct single-hop membership** (`y ∈ query_all(x,"isa")`), SKIPPING the recursive BFS
walk. The walk over a consolidated store expands spurious borderline edges and inflates false-positives (negatives
0.85 → 1.0 once skipped). The BFS path is kept for un-consolidated stores (multi-hop still needed there).
`Conversation.consolidate()` wires this end-to-end; `read_text` calls it automatically after a bulk read.

## Analog readout closes the deep floor (JEP-377/378)
- **Dimension** (auto_scale to keep load ≤ D/4, ~D=8192) restores deep reasoning, but pushing D further does NOT
  reliably help negatives (non-monotonic) — those were a query-side issue, fixed by the BFS-skip above, not by D.
- **Edge reinforcement does NOT work** under the default readout: modules are read through `sign()` (binarized), which
  discards magnitude (JEP-376 NULL).
- **The faint-edge deep floor was a SIGN-QUANTIZATION artifact, not dilution** (JEP-377): the deepest nodes (~10
  materialized ancestors) have faint true edges whose magnitude `sign()` throws away. A **magnitude-preserving (analog)
  readout** — unbind against the L2-normalized raw module sum (`SubstrateMemory.edge_sim_analog`) with its OWN
  calibrated gate — separates true from near-miss cleanly.
- **Deployed (JEP-378):** `is_a` over a materialized closure uses the analog readout for closed relations only;
  everything else stays on sign. Result: deep is-a **1.0** AND negatives **1.0** end-to-end via `Conversation.say()`,
  persistent across save/load, exceptions respected, suite green.

Net effect of the arc (JEP-370→378): adversarial composition 0.4 → ~1.0, deep is-a 0.85 → **1.0**, negatives → **1.0**,
end-to-end and persistent in the live talk loop. Within-domain deep reasoning is error-free at scale (hundreds of
facts, depth 8).

## Boundary
This makes *within-domain* deep reasoning reliable at scale; it does nothing for *open-domain* coverage (the untaught
knowledge tail, JEP-362) — that wall is separate and stands.
