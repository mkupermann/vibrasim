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
