# Reusable patterns register

**Status: open. New entries land here as substrate work surfaces them.**

This directory is the operationalisation of the EQMOD README's claim:

> *"The Skills, the dev and AI pipelines, the prompting and orchestration
> patterns it takes to push open-weight and cloud models against problems
> they cannot pattern-match — those translate directly to business and
> technical work in the moments when the usual playbook has run out.
> EQMOD does not need to succeed for that half to be useful. The patterns
> I am building to attack it are already shippable, and that is the half
> I want other people to be able to use."*

A pattern lives here when **all four** of these are true:

1. It came out of doing the substrate work, not out of a textbook.
2. It generalises beyond the substrate — at least one non-substrate use is
   credible.
3. It can be stated without depending on `world/`, `agent/`, or any
   EQMOD-specific code.
4. It has at least one piece of empirical evidence behind it (a run that
   worked, a failure mode it predicted, a deadlock it broke).

If a "pattern" is just a coding idiom or a refactor, it does not belong
here. Skills go in `~/.hermes/skills/`. Code goes in `world/`. This
directory is for **mechanisms** — reusable ways for a system to learn,
remember, recover, or decide — and for **process patterns** that broke a
deadlock and would break the next one.

---

## Entry template

Every entry is a single markdown file: `docs/patterns/<NN>-<slug>.md`.
Frontmatter is plain prose, not YAML.

```
# Pattern <NN> — <one-line name>

**Discovered:** YYYY-MM-DD, during <amendment / session>.
**Status:** draft | empirical | validated | retired.
**Substrate evidence:** one paragraph linking the run, the test, or the
                       LOGBOOK entry that surfaced the pattern.

## The mechanism

What the pattern is, in 100–300 words, framed in domain-neutral language.
A reader who has never heard of EQMOD should be able to follow.

## Why it works

The reasoning. Not the substrate's parameters — the underlying principle.

## Reusable form

The minimum useful statement of the pattern, with no substrate
dependencies. Pseudo-code or a numbered procedure. Should be 1–2 pages.

## Real-world / business mapping

At least one concrete example outside the substrate. Where would this
mechanism show up in business work, in an AI pipeline, in a research
process, in a deadlock-breaking workflow?

## Failure modes pre-registered

What this pattern does not solve. What it looks like when applied
incorrectly. The same honesty discipline as `docs/marker_protocol.md`.

## Empirical evidence

Run IDs, test IDs, LOGBOOK dates. The trail that takes a future reader
from this entry back to the substrate event that produced it.
```

---

## Index

Entries land below as they are written. The numbering is monotonically
increasing; numbers are never reused, and a retired entry stays in the
index with status RETIRED so the trail is preserved.

| # | Name | Status | Discovered | Last touched |
|---|------|--------|------------|--------------|
| — | (none yet) | — | — | — |

---

## What this directory is **not**

- Not a knowledge base of substrate internals — those live in
  `docs/CONCEPT.md`, `docs/TUTORIAL.md`, and `docs/RESEARCH_GUIDE.md`.
- Not a list of skills — those live in `~/.hermes/skills/` or in the
  Hermes plugin system.
- Not a paper. Each entry is a working note, not a publication. Patterns
  that mature into publishable claims migrate out to a real venue and
  remain here as the canonical reference.
- Not a brand book. No marketing voice. The honesty discipline of the
  EQMOD README is the voice.

---

## Curation rules

- A new entry is added by writing a new file. No PR ceremony.
- An entry's status field is the only place its maturity is recorded —
  not in the README, not in the LOGBOOK. One source of truth per entry.
- An entry can be retired but not deleted. Retired entries keep their
  number and gain a "Retired because:" paragraph.
- Cross-references from substrate code into this directory use the
  pattern number, not the slug. The slug can change; the number cannot.
- When a pattern is applied to a non-substrate project, the entry gains
  an "Applied at:" section with date, project, and outcome.

---

## First candidates (not yet written)

These are the patterns the substrate work has already surfaced. They will
become entries 01–NN as time permits, in no particular order:

- **Pre-registered acceptance bars with FAILED-first-class reporting.** The
  discipline that produced this entire amendment chain. Generalises to any
  empirical decision under pressure to overclaim.
- **Matched-wallclock negative controls.** The G19 / G23 pattern: every
  trained run is mirrored by N controls that consume the same wall-clock
  and the same pipeline, differing only in the instructive content.
- **Engineered topology, emergent dynamics.** CONCEPT §4.8's split between
  "ports are engineered" and "atoms / bridges / patterns are emergent."
  Generalises to any system where you want falsifiable claims about
  emergence without sneaking the answer into the initial conditions.
- **Mixture-of-experts memory vs. single-substrate memory as a labelled
  scientific distinction.** The `SubstrateLibrary` vs. `k_pattern_id` vs.
  dream-consolidation choice forces the project to name what kind of
  memory it is claiming. Generalises to any system where "the model
  learned X" needs a sharper claim.
- **Replay-driven consolidation as a forgetting-resistance mechanism.**
  G15/G18 dream code. Generalises to continual-learning settings outside
  the substrate.
- **The retry rule: unlimited attempts via new amendment numbers, never
  by editing a FAILED bar.** The discipline that lets a researcher be
  patient and honest at the same time. Generalises to any long-horizon
  research with iterative architecture changes.
- **Tri-modal training with engineered port topology.** G20–G23 itself,
  if it works. Generalises to any system that needs to bind heterogeneous
  input streams without a learned multimodal embedder.

When one of these gets written up, it becomes Pattern 01, 02, etc. and
this candidates list shrinks by one entry.
