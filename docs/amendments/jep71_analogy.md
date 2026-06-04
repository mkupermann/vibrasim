# JEP-71 — analogical reasoning via VSA (A:B::C:?) - a hallmark of human understanding

## Motivation
Analogy (infer a relation from one instance, transfer it to another) is central to human understanding. VSA
supports it structurally: if B = T (x) A (a transformation), then T = B (x) A^-1, and the analogous D = T (x) C.
Test relational analogy: from one (A,B) example, infer T and apply to a NEW C to recover D - including
TRANSFORMATIONS never seen with C.

## Pre-registration (locked BEFORE run)
- Entities + transformation roles (e.g. 'add-stripes', 'make-bigger') as VSA operators. B = T(x)A. Given (A,B,C),
  infer T = B (x) A^inv (circular correlation), apply D_pred = T (x) C, cleanup to nearest entity.
- Test on held-out (A,B,C,D) analogies (transformation inferred from ONE example, applied to NEW C).
- Bars: analogy completion hits@1 >= 0.8. PASS = structural analogical transfer works via VSA. NULL otherwise.
  Established (VSA/HRR analogy, Plate; Gayler), named as such.

## Result — NULL (random vectors -> noisy unbinding; fixable with unitary vectors)
analogy hits@1 = 0.262. Cause: random Gaussian vectors make A (x) A^-1 only APPROXIMATELY identity (noisy), so
T_inf = B (x) A^-1 = T (x) (A (x) A^-1) carries noise, compounded by D_pred = T_inf (x) C. Standard VSA fix:
UNITARY vectors (unit-magnitude FFT) -> circular correlation is EXACT inverse -> clean unbinding. JEP-71b.

## JEP-71b — unitary vectors — PASS
analogy completion (A:B::C:?) hits@1 = 1.000. With unitary vectors (exact unbinding), the transformation inferred
from a SINGLE (A,B) example transfers to a NEW C perfectly - one-shot analogical transfer, a hallmark of human
understanding, demonstrated structurally. JEP-71 NULL was the non-unitary-vector pitfall (noisy unbinding).
Established (VSA/HRR analogy, unitary HRR - Plate), named as such.

## Structural-cognition suite (JEP-64/65/66/67/68b/71b) - status toward human-level
Demonstrated hallmarks of human-like STRUCTURED thought, all via ESTABLISHED methods (decomposition, VSA/HRR), no
novelty: SET composition (65), RELATIONAL composition (66), RECURSIVE composition (67, depth-limited), RELATIONAL
ACTION (68b), one-shot ANALOGY (71b). Open frontier (JEP-69/70 NULL): UNSUPERVISED learning of arbitrary structure
(the roles/operators here are hand-built or supervised). So: the structural CAPABILITIES of understanding are
demonstrated; LEARNING them unsupervised + integrating into a generative scaled system is the honest open gap.
Genuine, measured progress; not arrival; named as established throughout.
