"""EQMOD-4 — the understanding engine (substrate-legal, NO transformer / LLM / pretrained model).

Consolidates the working machinery proven rung-by-rung (JEP-84 inference, JEP-88 role-binding,
JEP-90 end-to-end on simple language, JEP-91 grounding) into ONE tested engine:

    tell()  -> parse a simple English fact into structure (IS-A graph or a VSA-bound relational fact)
    perceive() -> ground noisy perceptual features to a concept (nearest prototype)
    is_a() / ask() -> answer comprehension, including MULTI-HOP never stated, and SAME-BAG truth
                      (who-plays-which-role), which bag-of-words cannot do.

Primitives only: VSA/HRR role-filler binding (circular convolution), transitive closure over a
learned IS-A graph, prototype perception. Honest scope: the target domain is SIMPLE, parseable,
controlled language with given prototypes — the engine is "100% working" on THAT domain. Scaling the
PARSE to dense real prose (JEP-89) and LEARNING concepts/relations from raw experience are the open
frontier, deliberately outside this engine's contract.
"""
from __future__ import annotations
import re
import numpy as np


class UnderstandingEngine:
    def __init__(self, dim: int = 2048, feat_dim: int = 32, seed: int = 0):
        self.dim = dim
        self.feat_dim = feat_dim
        self._rng = np.random.default_rng(seed)
        self._vocab: dict[str, np.ndarray] = {}
        # fixed role vectors for (subject, relation, object) binding
        self.SUBJ = self._rand()
        self.REL = self._rand()
        self.OBJ = self._rand()
        self.parents: dict[str, str] = {}          # IS-A graph (child -> parent)
        self.facts: list[tuple[str, str, str]] = []  # stored relational facts (s, r, o)
        self._fact_vecs: list[np.ndarray] = []
        self.prototypes: dict[str, np.ndarray] = {}  # concept -> perceptual feature prototype

    # --- vector primitives --------------------------------------------------
    def _rand(self) -> np.ndarray:
        return self._rng.normal(0.0, 1.0 / np.sqrt(self.dim), self.dim)

    def _vec(self, w: str) -> np.ndarray:
        w = w.lower()
        if w not in self._vocab:
            self._vocab[w] = self._rand()
        return self._vocab[w]

    @staticmethod
    def _cconv(a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    @staticmethod
    def _cos(a, b):
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

    @staticmethod
    def _norm_rel(r: str) -> str:
        """Normalize a verb to a common form so declarative ('chases') and interrogative ('chase')
        match. Strip 3rd-person-singular -s (chase s->chase, eats->eat, swims->swim); keep -ss."""
        r = r.lower()
        if r.endswith("s") and not r.endswith("ss") and len(r) > 2:
            return r[:-1]
        return r

    def _bind(self, s: str, r: str, o: str) -> np.ndarray:
        return (self._cconv(self.SUBJ, self._vec(self._norm(s)))
                + self._cconv(self.REL, self._vec(self._norm_rel(r)))
                + self._cconv(self.OBJ, self._vec(self._norm(o))))

    # --- grounding (perception) --------------------------------------------
    def add_prototype(self, concept: str, features: np.ndarray) -> None:
        self.prototypes[concept.lower()] = np.asarray(features, dtype=float)

    def perceive(self, features: np.ndarray) -> str | None:
        """Ground noisy features to the nearest concept prototype."""
        if not self.prototypes:
            return None
        feats = np.asarray(features, dtype=float)
        return min(self.prototypes, key=lambda c: np.linalg.norm(feats - self.prototypes[c]))

    # --- parsing / telling --------------------------------------------------
    _ISA = re.compile(r"^\s*(?:a|an|the)?\s*(\w+)\s+(?:is|are)\s+(?:a|an|the)?\s*(\w+)\s*\.?\s*$", re.I)
    _SVO = re.compile(r"^\s*the\s+(\w+)\s+(\w+)\s+(?:the\s+|a\s+|an\s+|in\s+the\s+|on\s+the\s+)?(\w+)\s*\.?\s*$", re.I)

    @staticmethod
    def _norm(w: str) -> str:
        w = w.lower()
        # light, deterministic singularization so "animals"/"animal" unify
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("ses") or w.endswith("shes") or w.endswith("ches"):
            return w[:-2]
        if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
            return w[:-1]
        return w

    # words that are not concepts when they land in object position of a copula
    _COPULA_STOP = {"is", "are", "was", "were", "not", "the", "a", "an"}

    def tell(self, sentence: str) -> tuple:
        """Parse one simple fact. Returns ('isa', child, parent) or ('rel', s, r, o) or ('none',)."""
        m = self._ISA.match(sentence)
        if m:
            child, parent = self._norm(m.group(1)), self._norm(m.group(2))
            if child != parent and parent not in self._COPULA_STOP:
                self.parents[child] = parent
                return ("isa", child, parent)
        m = self._SVO.match(sentence)
        if m:
            s, r, o = self._norm(m.group(1)), m.group(2).lower(), self._norm(m.group(3))
            self.facts.append((s, r, o))
            self._fact_vecs.append(self._bind(s, r, o))
            return ("rel", s, r, o)
        return ("none",)

    # --- inference / comprehension -----------------------------------------
    def ancestors(self, x: str) -> set[str]:
        x = self._norm(x)
        out, seen = set(), set()
        while x in self.parents and x not in seen:
            seen.add(x)
            x = self.parents[x]
            out.add(x)
        return out

    def is_a(self, x: str, c: str) -> bool:
        """Multi-hop IS-A by transitive closure (works for chains never stated)."""
        return self._norm(c) in self.ancestors(x)

    def relation_true(self, s: str, r: str, o: str, thresh: float = 0.9) -> bool:
        """Is (s, r, o) asserted? Role-binding makes this order-sensitive (same-bag discrimination).

        Threshold must be high: in the 3-role superposition a query sharing 2 of 3 roles (e.g. same
        subject+object, different relation) scores ~0.67, so 0.5 would false-positive. A correct fact
        scores ~1.0; any single differing role drops it to <=~0.67. 0.9 requires all three roles match.
        """
        if not self._fact_vecs:
            return False
        q = self._bind(self._norm(s), r.lower(), self._norm(o))
        return max(self._cos(q, fv) for fv in self._fact_vecs) >= thresh

    def _eval_clause(self, clause: str):
        """Evaluate one atomic clause (is-a or relation), honouring a leading/embedded 'not'."""
        c = clause.strip().rstrip("?").lower()
        negate = False
        # detect negation: "is not a", "does not", "not"
        if re.search(r"\bnot\b", c):
            negate = True
            c = re.sub(r"\bnot\b", " ", c)
            c = re.sub(r"\s+", " ", c).strip()
        val = self.ask(c)
        if val is None:
            return None
        return (not val) if negate else val

    def ask_bool(self, question: str):
        """Boolean-composed comprehension over atomic clauses: AND / OR / NOT (single connective + negation).

        e.g. 'is a poodle an animal and is a poodle not a fish' -> True.
        Mixed and/or precedence is deliberately out of contract (a later tier).
        """
        q = question.strip().rstrip("?").lower()
        if " or " in q and " and " not in q:
            clauses, op = re.split(r"\s+or\s+", q), "or"
        elif " and " in q and " or " not in q:
            clauses, op = re.split(r"\s+and\s+", q), "and"
        else:
            return self._eval_clause(q)  # single atomic clause (possibly negated)
        vals = [self._eval_clause(cl) for cl in clauses]
        if any(v is None for v in vals):
            return None
        return all(vals) if op == "and" else any(vals)

    def ask(self, question: str):
        """Route a simple question. 'is a poodle an animal' -> is_a; 'does the dog chase the cat' -> relation."""
        q = question.strip().rstrip("?").lower()
        # articles longest-first (an|a|the) + required trailing space, so "a" can't match inside "an"
        m = re.match(r"(?:is|are)\s+(?:(?:an|a|the)\s+)?(\w+)\s+(?:(?:an|a|the)\s+)?(\w+)", q)
        if m:
            return self.is_a(m.group(1), m.group(2))
        m = re.match(r"does\s+the\s+(\w+)\s+(\w+)\s+(?:(?:the|an|a)\s+|in\s+the\s+)?(\w+)", q)
        if m:
            return self.relation_true(m.group(1), m.group(2), m.group(3))
        return None
