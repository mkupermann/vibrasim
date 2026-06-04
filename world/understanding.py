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
        self.neg_isa: set[tuple[str, str]] = set()  # explicit negative facts: child is NOT parent
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
        self.prototypes[self._norm_phrase(concept)] = np.asarray(features, dtype=float)

    def learn_concept(self, name: str, examples: list) -> np.ndarray:
        """Human-like concept acquisition: form a prototype from a few perceptual EXAMPLES (their mean),
        rather than being told. The new concept then participates in perception + comprehension."""
        proto = np.mean(np.asarray(examples, dtype=float), axis=0)
        self.prototypes[self._norm_phrase(name)] = proto
        return proto

    def perceive(self, features: np.ndarray) -> str | None:
        """Ground noisy features to the nearest concept prototype."""
        if not self.prototypes:
            return None
        feats = np.asarray(features, dtype=float)
        return min(self.prototypes, key=lambda c: np.linalg.norm(feats - self.prototypes[c]))

    # --- parsing / telling --------------------------------------------------
    # articles require a trailing space and are longest-first, so a noun's leading "a"/"an" (e.g. "animals")
    # is never mistaken for an article (the JEP-92/94 surface-form lesson, applied to EVERY parser).
    # subject and object may both be multi-word noun phrases ("a big dog is a living thing").
    _ISA = re.compile(r"^\s*(?:(?:an|a|the)\s+)?(.+?)\s+(?:is|are)\s+(?:(?:an|a|the)\s+)?(.+?)\s*\.?\s*$", re.I)
    # SVO: leading "the" optional so plural statements parse ("Poodles chase cats.")
    _SVO = re.compile(r"^\s*(?:the\s+)?(\w+)\s+(\w+)\s+(?:the\s+|a\s+|an\s+|in\s+the\s+|on\s+the\s+)?(\w+)\s*\.?\s*$", re.I)

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

    @classmethod
    def _norm_phrase(cls, p: str) -> str:
        """Canonical key for a (possibly multi-word) concept phrase: lowercase, strip a trailing period,
        collapse spaces, and singularize the LAST word. 'A living thing.' -> 'living thing'; 'dogs' -> 'dog'.
        Accepts underscore_joined tokens too (kept as one word)."""
        p = p.strip().rstrip(".").lower().replace("_", " ")   # underscore and space are the same concept
        p = re.sub(r"\s+", " ", p)
        if not p:
            return p
        words = p.split(" ")
        words[-1] = cls._norm(words[-1])
        return " ".join(words)

    # words that are not concepts when they land in object position of a copula
    _COPULA_STOP = {"is", "are", "was", "were", "not", "the", "a", "an"}
    # pronouns can't be concepts without coreference resolution (a later tier) — reject, don't guess
    _PRONOUNS = {"it", "he", "she", "they", "this", "that", "these", "those",
                 "we", "you", "i", "him", "her", "them", "its"}

    @staticmethod
    def _preprocess_isa(sentence: str) -> str:
        """Normalize IS-A phrasings to the canonical 'X is/are Y' before regex parse:
        strip universal quantifiers (every/all/each), and collapse 'a kind/type/sort of'."""
        s = sentence
        s = re.sub(r"^\s*(?:every|all|each)\s+", "", s, flags=re.I)
        s = re.sub(r"\b(?:a\s+|an\s+)?(?:kind|type|sort)s?\s+of\s+", "", s, flags=re.I)
        return s

    _NEG_ISA = re.compile(r"^\s*(?:(?:an|a|the)\s+)?(.+?)\s+(?:is|are)\s+not\s+(?:(?:an|a|the)\s+)?(.+?)\s*\.?\s*$", re.I)

    def tell(self, sentence: str) -> tuple:
        """Parse one simple fact. Returns ('isa',c,p) / ('neg_isa',c,p) / ('rel',s,r,o) / ('none',).

        Supports learning-by-correction: 'X is not a Y' retracts the belief X->Y and records a negative
        fact; a later 'X is a Z' installs the corrected parent."""
        pre = self._preprocess_isa(sentence)
        mneg = self._NEG_ISA.match(pre)
        if mneg:
            child, parent = self._norm_phrase(mneg.group(1)), self._norm_phrase(mneg.group(2))
            self.neg_isa.add((child, parent))
            if self.parents.get(child) == parent:
                del self.parents[child]          # retract the corrected belief
            return ("neg_isa", child, parent)
        m = self._ISA.match(pre)
        if m:
            subj_phrase, parent = m.group(1), self._norm_phrase(m.group(2))
            if parent not in self._COPULA_STOP:
                # conjoined subjects: "Robins and sparrows are birds" -> robin->bird, sparrow->bird
                raw = [self._norm_phrase(s) for s in re.split(r"\s+and\s+", subj_phrase)]
                children = [c for c in raw if c and c != parent]
                if children and all(c in self._PRONOUNS for c in children):
                    return ("none",)                       # unresolved pronoun subject — reject, don't guess
                children = [c for c in children if c not in self._PRONOUNS]
                if children:
                    for c in children:
                        self.parents[c] = parent
                    return ("isa", children if len(children) > 1 else children[0], parent)
        m = self._SVO.match(sentence)
        if m:
            s, r, o = self._norm(m.group(1)), m.group(2).lower(), self._norm(m.group(3))
            self.facts.append((s, r, o))
            self._fact_vecs.append(self._bind(s, r, o))
            return ("rel", s, r, o)
        return ("none",)

    # --- inference / comprehension -----------------------------------------
    def ancestors(self, x: str) -> set[str]:
        x = self._norm_phrase(x)
        out, seen = set(), set()
        while x in self.parents and x not in seen:
            seen.add(x)
            x = self.parents[x]
            out.add(x)
        return out

    def _known_concepts(self) -> set:
        """Every concept the engine has heard of (as child, parent, negative fact, or prototype)."""
        ks = set(self.parents) | set(self.parents.values()) | set(self.prototypes)
        for a, b in self.neg_isa:
            ks.add(a); ks.add(b)
        return ks

    def assess(self, x: str, c: str) -> str:
        """Three-valued IS-A: 'yes' (path), 'no' (explicit negative, or category KNOWN but no path -
        closed-world over known concepts), or 'unknown' (category never heard of - epistemic humility)."""
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        if (x, c) in self.neg_isa:
            return "no"
        if c in self.ancestors(x):
            return "yes"
        return "no" if c in self._known_concepts() else "unknown"

    def frontier(self, x: str) -> str:
        """The topmost ancestor of x the engine currently knows (where x's IS-A chain ends)."""
        x = self._norm_phrase(x)
        cur, seen = x, set()
        while cur in self.parents and cur not in seen:
            seen.add(cur)
            cur = self.parents[cur]
        return cur

    def inquire(self, x: str, c: str):
        """Learning-through-dialogue: for an is-a question the engine can't answer YES, identify the
        precise knowledge GAP to be taught (the boundary of what it knows). None if it already knows."""
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        if self.assess(x, c) == "yes":
            return None
        top = self.frontier(x)
        if top == x:
            return f"I don't know anything about {self._art(x)} yet."
        return (f"I know {self._art(x)} is {self._art(top)}, "
                f"but I don't know whether {self._art(top)} is {self._art(c)}.")

    def is_a(self, x: str, c: str) -> bool:
        """Multi-hop IS-A by transitive closure; an explicit negative fact (correction) overrides."""
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        if (x, c) in self.neg_isa:
            return False
        return c in self.ancestors(x)

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

    # --- communication: explain the answer in English (template generation, no transformer) ----
    # a/an is phonetic, not orthographic: a letter rule fails on consonant-sound vowels ("a unicorn")
    # and vowel-sound consonants ("an hour"). Full correctness needs a pronunciation dictionary; this is
    # the standard pragmatic partial — a letter rule plus an exception set for common words.
    _ART_A = {"unicorn", "university", "unit", "united", "union", "unique", "european", "ewe",
              "one", "once", "u", "use", "user", "useful", "utah"}
    _ART_AN = {"hour", "honest", "honor", "honour", "heir", "honourable", "honorable"}

    @classmethod
    def _art(cls, noun: str) -> str:
        head = noun.split()[0] if noun else noun
        if head in cls._ART_A:
            art = "a "
        elif head in cls._ART_AN:
            art = "an "
        else:
            art = "an " if head[:1].lower() in "aeiou" else "a "
        return art + noun

    @staticmethod
    def _parse_isa_q(q: str):
        """Parse an is-a question into (subject, object), allowing multi-word subjects.
        Prefers an article-delimited object ('is a big dog an animal' -> 'big dog','animal');
        falls back to single-word subject + rest ('is poodle animal')."""
        m = re.match(r"(?:is|are)\s+(?:(?:an|a|the)\s+)?(.+?)\s+(?:an|a|the)\s+(.+)", q)
        if m:
            return m.group(1), m.group(2)
        m = re.match(r"(?:is|are)\s+(?:(?:an|a|the)\s+)?(\w+)\s+(.+)", q)
        if m:
            return m.group(1), m.group(2)
        return None

    def _isa_chain(self, x: str, c: str):
        """The path x -> ... -> c through the IS-A graph, or None if no path."""
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        path = [x]
        cur = x
        seen = set()
        while cur in self.parents and cur not in seen:
            seen.add(cur)
            cur = self.parents[cur]
            path.append(cur)
            if cur == c:
                return path
        return None

    def explain(self, question: str) -> str:
        """Answer a question in natural English, showing the reasoning (the inference chain)."""
        q = question.strip().rstrip("?").lower()
        sc = self._parse_isa_q(q)
        if sc:
            x, c = self._norm_phrase(sc[0]), self._norm_phrase(sc[1])
            verdict = self.assess(x, c)
            if verdict == "unknown":
                return f"I don't know whether {self._art(x)} is {self._art(c)}."
            if verdict == "yes":
                chain = self._isa_chain(x, c)
                disp = lambda w: w.replace("_", " ")
                steps = ", ".join(f"{self._art(disp(chain[i]))} is {self._art(disp(chain[i+1]))}"
                                  for i in range(len(chain) - 1))
                steps = steps[0].upper() + steps[1:] if steps else steps
                return f"Yes. {steps}."
            rest = f"{self._art(x)} is not {self._art(c)} as far as I know."
            return "No. " + rest[0].upper() + rest[1:]
        m = re.match(r"does\s+the\s+(\w+)\s+(\w+)\s+(?:(?:the|an|a)\s+|in\s+the\s+)?(\w+)", q)
        if m:
            s, r, o = m.group(1), m.group(2), m.group(3)
            if self.relation_true(s, r, o):
                return f"Yes, the {s} {self._norm_rel(r)}s the {o}."
            return f"No, I was not told that the {s} {self._norm_rel(r)}s the {o}."
        return "I cannot parse that question."

    def respond(self, question: str) -> str:
        """Conversational answer: handles WH-questions ('what is a poodle?', 'what does the dog chase?')
        and falls back to yes/no explanation for is-a / relation questions."""
        q = question.strip().rstrip("?").lower()
        m = re.match(r"what\s+(?:is|are)\s+(?:(?:an|a|the)\s+)?(.+)", q)
        if m:
            x = self._norm_phrase(m.group(1))
            p = self.parents.get(x)
            if p:
                ans = f"{self._art(x)} is {self._art(p)}."
                return ans[0].upper() + ans[1:]
            return f"I don't know what {self._art(x)} is."
        m = re.match(r"what\s+does\s+(?:the\s+)?(\w+)\s+(\w+)", q)
        if m:
            s, r = self._norm(m.group(1)), self._norm_rel(m.group(2))
            for fs, fr, fo in self.facts:
                if fs == s and self._norm_rel(fr) == r:
                    return f"The {s} {r}s the {fo}."
            return f"I don't know what the {s} {r}s."
        return self.explain(question)

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
        sc = self._parse_isa_q(q)
        if sc:
            return self.is_a(sc[0], sc[1])
        m = re.match(r"does\s+the\s+(\w+)\s+(\w+)\s+(?:(?:the|an|a)\s+|in\s+the\s+)?(\w+)", q)
        if m:
            return self.relation_true(m.group(1), m.group(2), m.group(3))
        return None
