# Pattern 03 — Match the formalism to the binding constraint, not the symptom

**Discovered:** 2026-06-12, during the new-math unblock programme (adversarial
survey of 7 directions → G154 → the G158 pre-draft check).
**Status:** empirical.
**Builds on:** [01 — which constraint binds](01-which-constraint-binds.md).

## The trap

When a substrate is deadlocked, the seductive move is to import a more
sophisticated mathematical lens — persistent homology, spectral graph theory,
category theory, information geometry, chemical reaction network theory — and
build a mechanism around it. The formalism feels powerful, the mechanism is
elegant, and an LLM asked to design it will produce a confident, plausible
mapping for *any* lens you name. Almost always, it then reproduces a result the
project already has, by a prettier route — because the formalism acts on a
**different layer** than the one that binds.

## Substrate evidence (all from one session)

Three independent attempts, three collisions with the same wall:

1. **The 7-candidate survey.** Self-organized criticality, physical reservoir
   computing, continuous attractors, predictive coding, equilibrium propagation,
   thermodynamic sampling, modular scaffold — *all seven* dropped under
   adversarial review. Each addressed graph topology, learning rules, or
   representation; none touched the binding constraint (the field coupling that
   conflates write and leak, or the categorical binding rules that are not a
   programmable Hamiltonian).
2. **G154 (matter associative recall) — NULL.** The substrate's only associative
   coupling, bridge tension, has a *single global* equilibrium distance
   `r_eq = r_2*0.5` and no per-bond rest length. Bonds encode "be `r_eq` from
   your neighbour," not "be at cell k," so a stored pattern is not a retrievable
   attractor. The lens (attractor dynamics) was sound; the substrate had no
   variable for it to act on.
3. **G158 (topological bond rule) — caught before running.** A persistent-homology
   / spectral constraint on bond formation attacks *percolation*. But percolation
   was already shown containable (G86 hand-placed plane; G88–G95 quiet substrate).
   The binding constraint of the memory deadlock is orthogonal: **active → write
   starves; quiet → atoms erode** (G93). A bond-graph topology rule cannot touch a
   coupling that lives in the charge-integration field and in atom decay dynamics.
   Running it would have re-derived G86.

## The mechanism

Before investing in a new-formalism amendment, run a one-question gate:

> **Does this formalism change the variable that the binding constraint is
> *about*?**

- Name the binding constraint as a statement about a specific variable
  (pattern 01 gives you this): *"the write field is the leak field"* (a coupling
  in the charge/vibration field), *"atoms erode without flux"* (a decay rate),
  *"binding is categorical, not parameterised"* (the bond-eligibility rule).
- Name what the formalism acts on: persistent homology / spectral theory act on
  the **connectivity graph**; attractor theory acts on a **stored-target
  variable**; CRN acts on **reaction stoichiometry / flux balance**.
- If those two are different objects, the formalism will, at best, reproduce a
  prior result on the symptom layer. Stop, or re-scope the claim to exactly what
  it *can* show (e.g. "emergent partition reproduces an engineered one") and
  pre-register that the binding constraint remains untouched.

## Why it works

A deadlock is a property of the binding constraint, not of the whole system. The
symptom (percolation, no recall, can't optimise) is downstream of it. Formalisms
are tools for manipulating particular mathematical objects; a tool is only useful
here if its object *is* the constraint's variable. Elegance on the wrong object is
indistinguishable, from the outcome alone, from progress — which is precisely why
the adversarial-verify step (try to refute, default to drop) and this gate have to
run *before* the build, not after the NULL.

## Corollary — the LLM is a hypothesis generator, never the judge

An LLM will translate any deadlock into any formalism on request, fluently and
sycophantically. That fluency is the hazard, not the value. Keep the LLM in the
tutor / translator role (cheat-sheet, code diff, candidate mechanism) and keep it
out of the verdict: the substrate run and the frozen, pre-registered bar decide.
The adversarial-verify pass sits between every LLM suggestion and the amendment.

## Transfer beyond EQMOD

Any system where a fashionable method is proposed for a stubborn problem: ask
which variable the method manipulates and which variable the failure is about. If
they differ, the method is decoration on this problem — however well it works on
problems whose binding constraint *is* its variable.
