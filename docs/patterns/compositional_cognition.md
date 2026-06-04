# Pattern: compositional / structured cognition — the building blocks toward human-level (JEP-64..68)

Compositional generalization is a defining feature of human understanding. The EQMOD-4 grounded approach
CATEGORIZES but does not COMPOSE on its own (JEP-64) - composition must be BUILT IN. These are the structural
building blocks, each via established methods (named), with their honest limits.

## The progression (each closes a concrete gap)
| capability | method | result | honest bound |
|------------|--------|--------|--------------|
| **SET** composition (X AND Y) | additive decomposition | 2^K goals from K primitives, zero-shot, F1 1.00 (JEP-65) | LINEAR/additive only - a "striped horse" != zebra + stripes |
| **RELATIONAL** composition (X-on-Y != Y-on-X) | VSA role-filler binding (Plate 1995 HRR) | role queries 1.00; additive is commutative -> 0.00 (JEP-66) | hand-specified roles |
| **RECURSIVE** composition (structures of structures) | VSA nested binding | perfect to depth 4, degrades 5-6 (JEP-67) | DEPTH LIMIT (crosstalk) - parallels human working-memory limits |
| **relational ACTION** (act on structured goals) | VSA relations + SR planning | resolve 'on top of Y' + navigate, 1.00 (JEP-68b) | toy scene |

## Key lessons
1. **Composition is not emergent from clustering/similarity - it must be built in** (JEP-64). Categorization and
   composition are different capabilities; a similarity-based concept former does the first, not the second.
2. **The right ALGEBRA matters:** additive codes are commutative (no roles/order); VSA binding (circular
   convolution) gives role-filler structure and recursion. Choose the representation algebra to match the
   structure you need (same shape as honest_evaluation #1: pick the right thing).
3. **Encoding bugs masquerade as capability failures** (JEP-68 NULL: separate role-binding lost the pairing;
   fixed by binding the pair, a(x)(ABOVE(x)b)). Check the representation before concluding the method failed.
4. **Honest depth/capacity limits are real and cognitively plausible** - VSA recursion fails past depth ~4-5,
   like humans on deep center-embedding.

## The honest gap to human-level (mapped, not crossed)
These are CAPABILITIES demonstrated in TOY isolation with HAND-BUILT structure (roles given, not learned), via
ESTABLISHED methods (decomposition, VSA/HRR, SR) - NO novelty. A human-level system would (1) LEARN the
relational structure from grounded experience (not hand-coded roles), (2) INTEGRATE set+relational+recursive
composition with grounded perception and action in one system, (3) use it GENERATIVELY and at SCALE, (4) with
language as the compositional interface. Large language models achieve much of (2)-(4) - and are forbidden here
(CLAUDE.md). So: genuine, measured progress on the structural building blocks of understanding; the unifying,
learned, generative, scaled system remains the open frontier. Not arrival - honest steps, named as established.
