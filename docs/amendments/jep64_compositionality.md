# JEP-64 — does the grounded approach COMPOSE (understanding) or only CATEGORIZE? (honest test of the user's question)

## Motivation
Michael asked: is this innovative / understanding? A real test of understanding (vs mere categorization) is
COMPOSITIONAL generalization: can the agent recognize a NOVEL COMBINATION of affordances it never observed, from
having seen the parts? Clustering/nearest-prototype concept formation (JEP-62/63) assigns to ONE learned
category - it should FAIL on combinations. An explicitly COMPOSITIONAL (additive decomposition) model should
succeed. This honestly bounds what the approach achieves.

## Pre-registration (locked BEFORE run)
- K primitive affordances; each prototype a random vector. Items afford a SUBSET; outcome = sum of its primitives'
  prototypes + noise. TRAIN concept formation on SINGLE-primitive items. TEST on novel TWO-primitive items: does
  the model identify BOTH affordances?
- Compare: (a) nearest-prototype / clustering (categorize), (b) additive linear decomposition (compose).
- Bars: clustering recall on combinations < 0.6 (it does NOT compose - categorizes) AND additive decomposition
  recall >= 0.9 (composition needs explicit compositional structure). This is a CHARACTERIZATION, not a PASS-to-
  celebrate: it bounds the approach honestly. Established (clustering, linear decomposition), named as such.

## Result — the approach CATEGORIZES, does not COMPOSE (a key gap toward human-level)
| method | recall on NOVEL 2-affordance combinations |
|--------|-------------------------------------------|
| nearest-prototype (clustering, JEP-62/63) | 0.500 (gets only ONE of two affordances) |
| additive decomposition (explicit composition) | 1.000 |

**VERDICT: characterization confirmed - and it locates the gap to human-level.** Clustering-based concept
formation CATEGORIZES (assigns a novel item to ONE learned category -> 0.50 recall on a 2-affordance combination)
but does NOT COMPOSE. An EXPLICITLY COMPOSITIONAL model (additive decomposition onto primitive prototypes)
recovers both affordances (1.00). So compositionality is NOT emergent from clustering - it must be BUILT IN.
COMPOSITIONAL generalization (recognizing novel combinations from known parts) is a hallmark of HUMAN
understanding, and this is precisely where the toy approach falls short. The constructive implication: to move
toward human-level, BUILD IN compositional structure (JEP-65). Honest: this confirms 'categorization, not yet
compositional understanding' - but it also points at the concrete next step. Established (clustering, linear
decomposition), named as such.
