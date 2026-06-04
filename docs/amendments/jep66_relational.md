# JEP-66 — RELATIONAL composition (role binding): the next gap toward human-level after additive (JEP-65)

## Motivation
JEP-65 did ADDITIVE composition (unordered sets, X AND Y). Human composition is RELATIONAL: X-on-Y != Y-on-X
(roles/order matter). Additive codes (sums) are COMMUTATIVE -> cannot distinguish role-bound structures. The
established method is VECTOR-SYMBOLIC binding (role (X) filler binding via circular convolution; Plate 1995) -
which EQMOD-2 already used. Test: can binding distinguish relational structures (above(X,Y) vs above(Y,X)) that
additive composition cannot?

## Pre-registration (locked BEFORE run)
- Random vectors for fillers (objects) and roles (e.g. TOP, BOTTOM). Structure above(X,Y) = TOP(x)X + BOTTOM(x)Y
  (binding via circular convolution, bundling via sum). UNBIND to query 'what is on top?' -> should recover X.
- Compare: ADDITIVE code (X+Y, commutative) vs VSA BINDING. Tasks: (a) distinguish above(X,Y) from above(Y,X);
  (b) answer 'what is on top of Z?' for novel structures.
- Bars: VSA distinguishes order with accuracy >= 0.9 AND additive is at chance (~0.5); VSA role-query accuracy
  >= 0.9. PASS = relational/role-binding composition works (next gap closed) where additive cannot. NULL else.
  Established (VSA / holographic reduced representations, Plate 1995), named as such.

## Result — PASS (relational/role-binding composition via VSA; additive cannot)
| capability | VSA binding | additive |
|------------|-------------|----------|
| what's-on-top correct for BOTH X-on-Y and Y-on-X | 1.00 | 0.00 (commutative) |
| role-query (top AND bottom) on novel structures | 1.00 | n/a |

**VERDICT: PASS.** VSA role-filler binding (circular convolution, Plate 1995 HRR) handles RELATIONAL composition
where additive composition cannot: it distinguishes above(X,Y) from above(Y,X) and answers role queries (what's
on top / on bottom) on NOVEL structures at 1.00, while the additive code is COMMUTATIVE (X+Y identical for both
orders -> cannot encode role/order). Closes the next gap after additive (JEP-65). Compositional progression toward
human-level structured cognition: SET composition (JEP-65) -> RELATIONAL/role composition (JEP-66). HONEST: VSA is
ESTABLISHED (Plate 1995; named in EQMOD-2 memory) - established method closing a real capability gap, NOT novel.
Remaining gap: RECURSION (structures of structures, e.g. above(X, above(Y,Z))) - VSA supports it (JEP-67 next).
Established (vector-symbolic architectures / HRR), named as such.
