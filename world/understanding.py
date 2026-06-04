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
        self.parents: dict[str, set] = {}           # IS-A DAG (child -> set of parents)
        self.neg_isa: set[tuple[str, str]] = set()  # explicit negative facts: child is NOT parent
        self.facts: list[tuple[str, str, str]] = []  # stored relational facts (s, r, o)
        self._fact_vecs: list[np.ndarray] = []
        self.prototypes: dict[str, np.ndarray] = {}  # concept -> perceptual feature prototype
        self.properties: dict[str, set] = {}         # concept -> properties it HAS ("a robin can fly")
        self.not_properties: dict[str, set] = {}     # concept -> properties it explicitly LACKS
        self._induced: dict[str, set] = {}           # category -> inductively generalized properties
        self._last_subject: str | None = None        # for simple pronoun coreference ("it"/"they")
        self._last_query: tuple | None = None         # last (x, c) is-a question, for "why?" follow-ups
        self._orders: dict[str, dict[str, set]] = {}   # comparative -> {x -> set(y)} for transitive comparison

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
    # MANDATORY article form for EVERY parser in this file: r"(?:(?:an|a|the)\s+)?"
    # longest-first (an|a|the) + REQUIRED trailing space, so a noun's leading "a"/"an" (e.g. "animals", "an" in
    # "animal") is never mistaken for an article. The bare form r"(?:a|an|the)?" is BUGGED (matches "a" inside
    # "an") and recurred 6 times (JEP-92/94/95/100/119) — NEVER hand-write it; copy the form on this line.
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
        p = re.sub(r"^\s*(?:a|an|the)\s+", "", p)              # strip a leading article so callers can pass "a poodle"
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            return p
        words = p.split(" ")
        words[-1] = cls._norm(words[-1])
        return " ".join(words)

    # words that are not concepts when they land in object position of a copula
    _COPULA_STOP = {"is", "are", "was", "were", "not", "the", "a", "an"}

    @staticmethod
    def _valid_concept(p: str) -> bool:
        """A concept must be a short noun phrase (<=4 words, no internal punctuation) — so the engine
        REJECTS complex/clausal sentences cleanly instead of grabbing whole clauses as 'concepts'."""
        if not p:
            return False
        if len(p.split()) > 4:
            return False
        return not re.search(r"[,;:()‘’“”]", p)
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
        sentence = self._resolve_pronoun(sentence)
        pre = self._preprocess_isa(sentence)
        # properties: "X cannot/can't/can not VERB" (negative) before "X can VERB" (positive)
        mpn = re.match(r"^\s*(?:(?:an|a|the)\s+)?(\w+)\s+(?:cannot|can't|can\s+not)\s+(\w+)\s*\.?\s*$", pre, re.I)
        if mpn:
            x, p = self._norm_phrase(mpn.group(1)), mpn.group(2).lower()
            self.not_properties.setdefault(x, set()).add(p)
            self._last_subject = x
            return ("neg_prop", x, p)
        mpp = re.match(r"^\s*(?:(?:an|a|the)\s+)?(\w+)\s+can\s+(\w+)\s*\.?\s*$", pre, re.I)
        if mpp:
            x, p = self._norm_phrase(mpp.group(1)), mpp.group(2).lower()
            self.properties.setdefault(x, set()).add(p)
            self._last_subject = x
            return ("prop", x, p)
        # comparative/order relation: "X is bigger than Y" (BEFORE _ISA, which would read it as 'X is-a bigger')
        mcmp = re.match(r"^\s*(?:(?:an|a|the)\s+)?(\w+)\s+(?:is|are)\s+(\w+)\s+than\s+(?:(?:an|a|the)\s+)?(\w+)\s*\.?\s*$", pre, re.I)
        if mcmp:
            x, comp, y = self._norm(mcmp.group(1)), mcmp.group(2).lower(), self._norm(mcmp.group(3))
            self._orders.setdefault(comp, {}).setdefault(x, set()).add(y)
            self._last_subject = x
            return ("order", x, comp, y)
        mneg = self._NEG_ISA.match(pre)
        if mneg and self._valid_concept(self._norm_phrase(mneg.group(1))) and self._valid_concept(self._norm_phrase(mneg.group(2))):
            child, parent = self._norm_phrase(mneg.group(1)), self._norm_phrase(mneg.group(2))
            self.neg_isa.add((child, parent))
            self.parents.get(child, set()).discard(parent)   # retract the corrected belief (one edge)
            self._last_subject = child
            return ("neg_isa", child, parent)
        m = self._ISA.match(pre)
        if m:
            subj_phrase, parent = m.group(1), self._norm_phrase(m.group(2))
            if parent not in self._COPULA_STOP and self._valid_concept(parent):
                # conjoined subjects: "Robins and sparrows are birds" -> robin->bird, sparrow->bird
                raw = [self._norm_phrase(s) for s in re.split(r"\s+and\s+", subj_phrase)]
                children = [c for c in raw if c and c != parent]
                if children and all(c in self._PRONOUNS for c in children):
                    return ("none",)                       # unresolved pronoun subject — reject, don't guess
                children = [c for c in children if c not in self._PRONOUNS and self._valid_concept(c)]
                if children:
                    for c in children:
                        self.parents.setdefault(c, set()).add(parent)   # DAG: a concept may have many parents
                        self.neg_isa.discard((c, parent))               # asserting overrides a prior negative
                    self._last_subject = children[0]
                    return ("isa", children if len(children) > 1 else children[0], parent)
        m = self._SVO.match(sentence)
        if m:
            s, r, o = self._norm(m.group(1)), m.group(2).lower(), self._norm(m.group(3))
            self.facts.append((s, r, o))
            self._fact_vecs.append(self._bind(s, r, o))
            self._last_subject = s
            return ("rel", s, r, o)
        return ("none",)

    def _resolve_pronoun(self, sentence: str) -> str:
        """Simple discourse coreference: if the sentence's subject is a pronoun, substitute the most
        recently mentioned subject. Honest limit: assumes topic continuity (subject antecedent)."""
        m = re.match(r"^(\s*)(\w+)\b(.*)$", sentence, re.S)
        if m and m.group(2).lower() in self._PRONOUNS and self._last_subject:
            # plain string splice — NEVER use a data-derived value as a regex replacement template
            return m.group(1) + self._last_subject + m.group(3)
        return sentence

    # --- inference / comprehension -----------------------------------------
    def ancestors(self, x: str) -> set[str]:
        """All ancestors of x over the IS-A DAG (transitive closure across multiple parents)."""
        x = self._norm_phrase(x)
        out, stack, seen = set(), [x], {x}
        while stack:
            cur = stack.pop()
            for p in self.parents.get(cur, ()):
                if p not in seen:
                    seen.add(p); out.add(p); stack.append(p)
        return out

    def _known_concepts(self) -> set:
        """Every concept the engine has heard of (as child, parent, negative fact, or prototype)."""
        ks = set(self.parents) | set(self.prototypes)
        for ps in self.parents.values():
            ks |= ps
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
        """A topmost ancestor of x the engine currently knows (follow one parent chain to a root)."""
        x = self._norm_phrase(x)
        cur, seen = x, set()
        while self.parents.get(cur) and cur not in seen:
            seen.add(cur)
            cur = next(iter(self.parents[cur]))   # follow one parent up to a root
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

    def induce(self):
        """Inductive generalization: a property shared by >=2 instances is generalized to the MOST-SPECIFIC
        category common to those instances (their lowest common ancestor), NOT every ancestor — so 'robins and
        sparrows fly' yields 'birds fly', not 'animals fly' (a poodle must not inherit flight). Defeasible: an
        explicit counterexample overrides per-instance."""
        from collections import defaultdict
        self._induced = {}
        prop_pos = defaultdict(set)
        for x, ps in self.properties.items():
            for p in ps:
                prop_pos[p].add(x)
        for p, pos in prop_pos.items():
            if len(pos) < 2:
                continue
            # categories common to ALL positive instances
            common = None
            for i in pos:
                anc_i = self.ancestors(i) | {i}
                common = anc_i if common is None else (common & anc_i)
            common = (common or set()) - pos
            if not common:
                continue
            # most-specific common ancestor(s): no other common category sits below them
            most_specific = {c for c in common
                             if not any(c in self.ancestors(c2) for c2 in common if c2 != c)}
            for c in most_specific:
                insts = [x for x in self.parents if c in self.ancestors(x)]
                posc = sum(1 for i in insts if p in self.properties.get(i, set()))
                neg = sum(1 for i in insts if p in self.not_properties.get(i, set()))
                if posc >= 2 and posc > neg:
                    self._induced.setdefault(c, set()).add(p)
        return self._induced

    def has_property(self, x: str, p: str) -> bool:
        """Does x have property p? Explicit fact wins; else INDUCED from a category x belongs to (defeasible)."""
        x, p = self._norm_phrase(x), p.lower()
        if p in self.not_properties.get(x, set()):
            return False
        if p in self.properties.get(x, set()):
            return True
        for c in self.ancestors(x):
            if p in self._induced.get(c, set()):
                return True
        return False

    def would_contradict(self, sentence: str):
        """Consistency check (non-blocking): does asserting `sentence` conflict with current beliefs?
        Returns a message or None. ('X is not C' conflicts if C is currently derivable for X; 'X is C'
        conflicts if X was explicitly told NOT to be C.) A correction via tell() still overrides."""
        pre = self._preprocess_isa(self._resolve_pronoun(sentence))
        mneg = self._NEG_ISA.match(pre)
        if mneg:
            x, c = self._norm_phrase(mneg.group(1)), self._norm_phrase(mneg.group(2))
            if self._valid_concept(x) and self._valid_concept(c) and c in self.ancestors(x):
                return f"Contradiction: I currently believe {self._art(x)} is {self._art(c)}."
            return None
        m = self._ISA.match(pre)
        if m:
            x, c = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
            if self._valid_concept(x) and self._valid_concept(c) and (x, c) in self.neg_isa:
                return f"Contradiction: I was told {self._art(x)} is NOT {self._art(c)}."
        return None

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
        """A shortest path x -> ... -> c through the IS-A DAG (BFS), or None if no path."""
        from collections import deque
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        q, seen = deque([[x]]), {x}
        while q:
            path = q.popleft()
            node = path[-1]
            if node == c:
                return path
            for p in self.parents.get(node, ()):
                if p not in seen:
                    seen.add(p)
                    q.append(path + [p])
        return None

    def explain(self, question: str) -> str:
        """Answer a question in natural English, showing the reasoning (the inference chain)."""
        q = question.strip().rstrip("?").lower()
        sc = self._parse_isa_q(q)
        if sc:
            x, c = self._norm_phrase(sc[0]), self._norm_phrase(sc[1])
            self._last_query = (x, c)
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

    def _order_holds(self, comp: str, x: str, z: str) -> bool:
        """Transitive closure over a comparison relation: is x `comp`-than z (directly or transitively)?"""
        g = self._orders.get(comp, {})
        x, z = self._norm(x), self._norm(z)
        stack, seen = [x], {x}
        while stack:
            cur = stack.pop()
            for y in g.get(cur, ()):
                if y == z:
                    return True
                if y not in seen:
                    seen.add(y); stack.append(y)
        return False

    def describe(self, concept: str) -> str:
        """Generate a multi-sentence English description of a concept from everything known (categories,
        inherited properties, relations). Generative communication from structure — no transformer."""
        x = self._norm_phrase(concept)
        sents = []
        parents = sorted(self.parents.get(x, set()))
        if parents:
            joined = parents[0] if len(parents) == 1 else ", ".join(self._art(p) for p in parents[:-1]) + " and " + self._art(parents[-1])
            sents.append(f"{self._art(x)} is {self._art(parents[0]) if len(parents)==1 else joined}.")
        # inherited categories beyond direct parents
        higher = sorted(self.ancestors(x) - set(parents))
        if higher:
            sents.append(f"That makes it also " + ", ".join(self._art(h) for h in higher) + ".")
        # properties: own + inherited (induced), minus explicit exceptions
        props = set(self.properties.get(x, set()))
        for c in self.ancestors(x):
            props |= self._induced.get(c, set())
        props -= self.not_properties.get(x, set())
        if props:
            sents.append("It can " + ", ".join(sorted(props)) + ".")
        # relations where x is the subject
        rels = [f"{self._norm_rel(r)}s the {o}" for s, r, o in self.facts if s == self._norm(x)]
        if rels:
            sents.append("It " + ", and ".join(sorted(set(rels))) + ".")
        if not sents:
            return f"I don't know anything about {self._art(x)} yet."
        sents[0] = sents[0][0].upper() + sents[0][1:]
        return " ".join(sents)

    def _all_have_property(self, cat: str, prop: str):
        """Universal over instances: do ALL known instances of `cat` have property `prop`?
        Returns (verdict, counterexample-or-None)."""
        cat, prop = self._norm_phrase(cat), prop.lower()
        instances = [x for x in self.parents if cat in self.ancestors(x)] + [cat]
        lacking = [i for i in instances if prop in self.not_properties.get(i, set())]
        if lacking:
            return False, lacking[0]
        has = [i for i in instances if self.has_property(i, prop)]
        return (len(has) > 0), None

    def respond(self, question: str) -> str:
        """Conversational answer: quantified ('is every dog an animal?', 'can all birds fly?'), WH-questions
        ('what is a poodle?'), and yes/no explanation for is-a / relation questions."""
        q = question.strip().rstrip("?").lower()
        # hypothetical: "if a whale is/were a fish, is a whale an animal" -> assume, answer, RETRACT
        if q.startswith("if "):
            parts = q[3:].split(",", 1)
            if len(parts) == 2:
                ma = re.match(r"(?:(?:an|a|the)\s+)?(\w+)\s+(?:is|are|were|was)\s+(?:(?:an|a|the)\s+)?(.+)", parts[0].strip())
                if ma:
                    x, y = self._norm_phrase(ma.group(1)), self._norm_phrase(ma.group(2))
                    x_existed = x in self.parents
                    had = y in self.parents.get(x, set())
                    self.parents.setdefault(x, set()).add(y)          # temporarily assume
                    sub = parts[1].strip()
                    sub = re.sub(r"\b(?:would|could)\s+(\w+)\s+be\b", r"is \1", sub)   # 'would it be' -> 'is it'
                    sub = re.sub(r"\b(?:would|could)\b", "is", sub)
                    sub = re.sub(r"\bit\b", x, sub)                    # resolve 'it' to the hypothetical subject
                    ans = self.respond(sub)
                    if not had:                                       # RETRACT (leave KB unchanged)
                        self.parents[x].discard(y)
                        if not self.parents[x] and not x_existed:
                            del self.parents[x]
                    return ans
        # analogy: "dog is to puppy as cat is to ?" -> find the relation A->B, apply it to C
        ma = re.match(r"(?:what is |)(\w+) is to (\w+) as (\w+) is to", q)
        if ma:
            a, b, c = self._norm(ma.group(1)), self._norm(ma.group(2)), self._norm(ma.group(3))
            rels = {fr for fs, fr, fo in self.facts if fs == a and fo == b}        # relations linking A->B
            for gs, gr, go in self.facts:
                if gs == c and self._norm_rel(gr) in {self._norm_rel(r) for r in rels}:
                    return go.capitalize() + "."
            return "I can't complete that analogy."
        # compositional query: "is what the dog chases an animal" -> resolve relation, then taxonomy
        mcomp = re.match(r"is what (?:the\s+)?(\w+)\s+(\w+)\s+(?:(?:an|a|the)\s+)?(.+)", q)
        if mcomp:
            s, r, c = self._norm(mcomp.group(1)), self._norm_rel(mcomp.group(2)), self._norm_phrase(mcomp.group(3))
            for fs, fr, fo in self.facts:
                if fs == s and self._norm_rel(fr) == r:
                    return "Yes." if self.is_a(fo, c) else "No."
            return f"I don't know what the {s} {self._norm_rel(r)}s."
        # comparative query: "is X bigger than Z" -> transitive closure over the order relation
        mc = re.match(r"(?:is|are)\s+(?:(?:an|a|the)\s+)?(\w+)\s+(\w+)\s+than\s+(?:(?:an|a|the)\s+)?(\w+)", q)
        if mc:
            x, comp, z = self._norm(mc.group(1)), mc.group(2).lower(), self._norm(mc.group(3))
            return "Yes." if self._order_holds(comp, x, z) else "Not that I can tell."
        # "why?" follow-up: justify the last is-a answer using the reasoning chain
        if re.fullmatch(r"why\b.*", q):
            if not self._last_query:
                return "You haven't asked me a question I can justify yet."
            x, c = self._last_query
            chain = self._isa_chain(x, c)
            if chain:
                disp = lambda w: w.replace("_", " ")
                steps = ", and ".join(f"{self._art(disp(chain[i]))} is {self._art(disp(chain[i+1]))}"
                                      for i in range(len(chain) - 1))
                return f"Because {steps}."
            if self.assess(x, c) == "unknown":
                return f"Because I was never told whether {self._art(x)} is {self._art(c)}."
            return f"Because nothing I was told makes {self._art(x)} {self._art(c)}."
        # universal IS-A: "is every X (a) Y" / "are all X Y" -> taxonomy is_a (a category subsumes another)
        mq = re.match(r"(?:is every|are all|is each)\s+(\w+)\s+(?:an?\s+|the\s+)?(.+)", q)
        if mq:
            x, c = self._norm_phrase(mq.group(1)), self._norm_phrase(mq.group(2))
            return "Yes." if self.is_a(x, c) else f"Not necessarily — I can't derive that every {x} is {self._art(c)}."
        # universal property: "can/do all X VERB"
        mqp = re.match(r"(?:can|do|does)\s+(?:all|every|each)\s+(\w+)\s+(\w+)", q)
        if mqp:
            cat, prop = mqp.group(1), self._norm_rel(mqp.group(2))
            ok, ex = self._all_have_property(cat, prop)
            if ok:
                return f"Yes, all {self._norm_phrase(cat)}s can {prop}."
            if ex:
                return f"No — not all. For example, {self._art(ex)} cannot {prop}."
            return f"I don't know whether all {self._norm_phrase(cat)}s can {prop}."
        m = re.match(r"what\s+(?:is|are)\s+(?:(?:an|a|the)\s+)?(.+)", q)
        if m:
            x = self._norm_phrase(m.group(1))
            ps = self.parents.get(x)
            if ps:
                parts = [self._art(p) for p in sorted(ps)]
                joined = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
                ans = f"{self._art(x)} is {joined}."
                return ans[0].upper() + ans[1:]
            return f"I don't know what {self._art(x)} is."
        m = re.match(r"what\s+does\s+(?:the\s+)?(\w+)\s+(\w+)", q)
        if m:
            s, r = self._norm(m.group(1)), self._norm_rel(m.group(2))
            for fs, fr, fo in self.facts:
                if fs == s and self._norm_rel(fr) == r:
                    return f"The {s} {r}s the {fo}."
            return f"I don't know what the {s} {r}s."
        # Boolean-composed questions route through ask_bool (otherwise explain can't see the connective)
        if (" and " in q or " or " in q) and re.match(r"(is|are|does)\b", q):
            r = self.ask_bool(question)
            if r is not None:
                return "Yes." if r else "No."
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
