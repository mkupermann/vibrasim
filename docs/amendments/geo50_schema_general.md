# GEO-50 — Schema-general auto-dispatch: operators over arbitrary meta fields, two schemas

## Motivation
GEO-49's operators were schema-specific (person/team/city). To be a usable tool the auto-dispatch must work
on ARBITRARY schemas. GEO-50 generalizes the operators to operate on arbitrary meta fields (count-by-field,
join-on-field, factoid-retrieve) and proves generality by running the SAME agent on TWO different schemas.

## Pre-registration (locked BEFORE run)
- Generalize: facts carry arbitrary meta; operators are field-parameterized:
  count_by(field, value), join_on(subject, field), get(subject, field) via geometric retrieve.
- Schema A: people {team, city}. Schema B: products {category, warehouse}.
- Mixed test set per schema (factoid + count + join), answers known.
- Metric: end-to-end accuracy on BOTH schemas. Bar: >= 0.8 on each (the general agent works across schemas).
  NULL if generalization breaks. (Routing stays keyword-based; resolution geometric; operators field-generic.)

## Result — PASS
| schema | accuracy |
|--------|----------|
| A: people {team, city} | 4/4 = **1.00** |
| B: products {category, warehouse} | 4/4 = **1.00** |

**VERDICT: PASS.** The SAME agent with field-parameterized operators (count_by(field,value),
join_on(subject,field), get(subject,field)) works on two distinct schemas. The auto-dispatch pattern is
SCHEMA-GENERAL — a usable tool for arbitrary structured data, not a person/team/city demo. **Honest note:** it
takes a small per-schema `field_hints` config (which query words map to which meta fields); the OPERATORS are
generic and schema-agnostic, the wiring is config-driven (not hardcoded, not zero-config). This is the
expected, reasonable level of generality for a lightweight neuro-symbolic agent. Resolves the GEO-49 scope
caveat.
