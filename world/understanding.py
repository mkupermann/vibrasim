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

    # singular nouns ending in -s that must NOT be de-pluralized (over-stripping bug: virus -> "viru")
    _NOT_PLURAL = {"species", "series", "news", "lens", "bus", "gas", "atlas", "bias", "iris", "axis",
                   "basis", "crisis", "analysis", "thesis", "virus", "census", "campus", "status", "focus"}

    @staticmethod
    def _norm(w: str) -> str:
        w = w.lower()
        # light, deterministic singularization so "animals"/"animal" unify
        if w in UnderstandingEngine._NOT_PLURAL:
            return w
        irregular = {"wolves": "wolf", "leaves": "leaf", "lives": "life", "knives": "knife", "wives": "wife",
                     "halves": "half", "shelves": "shelf", "calves": "calf", "thieves": "thief", "loaves": "loaf",
                     "feet": "foot", "teeth": "tooth", "geese": "goose", "mice": "mouse", "men": "man",
                     "women": "woman", "children": "child", "people": "person"}
        if w in irregular:
            return irregular[w]
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("shes") or w.endswith("ches") or w.endswith("sses"):
            return w[:-2]                      # dishes->dish, batches->batch, glasses->glass
        if w.endswith("ses"):
            return w[:-1]                      # horses->horse, roses->rose (singular ends in -se, strip only -s)
        # -us / -is / -ss endings are typically NOT plurals (virus, basis, glass) -> keep
        if w.endswith("s") and not w.endswith(("ss", "us", "is")) and len(w) > 3:
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

    @staticmethod
    def _bare_np(phrase: str) -> bool:
        """True if phrase is a short bare noun phrase (<=4 words, no conjunctions/prepositions/clause markers) —
        the guard that makes pattern extraction from real prose PRECISE (JEP-156): rejects clause fragments that
        the <=4-word _valid_concept check alone lets through."""
        bad = {"and", "or", "but", "that", "which", "who", "whom", "whose", "if", "then", "than", "as",
               "of", "in", "on", "at", "by", "to", "for", "with", "from", "into", "is", "are", "was", "were"}
        toks = phrase.split()
        return bool(toks) and len(toks) <= 4 and not any(t in bad for t in toks)

    def read(self, passage: str) -> dict:
        """LEARN FROM PROSE (the learn-from-sources capability, JEP-155..159): extract is-a + part-of + causal
        relations from an encyclopedic-register passage via classic Hearst-style lexico-syntactic patterns + a
        bare-NP guard, and ingest them. NO transformer. Returns counts of what was learned per relation.

        Works on encyclopedic/descriptive prose ('A dog is a mammal. A heart is part of a dog. A virus causes a
        fever.'); dense logic/argument prose (e.g. Boole) yields little — the gate is the GENRE, not the extractor."""
        art = r"(?:(?:an|a|the)\s+)?"
        np = rf"{art}([a-z][a-z\- ]*?)"
        learned = {"is_a": 0, "part_of": 0, "causal": 0}
        last_subject = None     # most-recent subject, for recency-based cross-sentence pronoun resolution
        for s in re.split(r"[.;:]\s+", passage.strip().lower()):
            s = s.strip().rstrip(".")
            if not s:
                continue
            # recency coreference: a sentence-initial pronoun ('It is a mammal') -> the last subject (heuristic)
            mp = re.match(r"^(it|they|this|these|he|she)\s+(is|are)\s+(.*)$", s)
            if mp and last_subject is not None:
                s = f"{last_subject} {mp.group(2)} {mp.group(3)}"
            # 'X such as A and B' -> (A,X),(B,X)  (do first; it is unambiguous)
            m = re.search(rf"\b{np}\s+such\s+as\s+(.+)$", s)
            if m:
                parent = self._norm_phrase(m.group(1))
                if self._bare_np(parent) and self._valid_concept(parent):
                    stop = {"is", "are", "was", "were", "can", "cannot", "have", "has", "which", "that"}
                    for kid in re.split(r"\s+and\s+|,\s*", m.group(2)):
                        # truncate each list item to its leading noun-phrase run (drop a trailing verb phrase,
                        # e.g. 'cats are common' -> 'cats') so a trailing VP does not lose the item
                        toks = kid.strip().split()
                        head = []
                        for t in toks:
                            if t in stop:
                                break
                            head.append(t)
                        kid = self._norm_phrase(" ".join(head))
                        if self._bare_np(kid) and self._valid_concept(kid):
                            self.tell(f"a {kid} is a {parent}."); learned["is_a"] += 1
                continue
            # NEGATION / correction: 'X is not a/an Y' -> route to tell() (retracts the belief + records a negative
            # fact), so a correcting passage from a source REVISES prior beliefs (belief revision from prose)
            m = re.match(rf"^{np}\s+is\s+not\s+an?\s+([a-z]+)$", s)
            if m:
                a, b = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
                if a not in self._PRONOUNS and self._bare_np(a) and self._bare_np(b):
                    self.tell(f"a {a} is not a {b}."); learned["is_a"] += 1
                    last_subject = a
                continue
            # spatial containment: 'X is located in Y' / 'X is in Y' -> X part-of Y (geographic/spatial whole)
            m = re.match(rf"^{np}\s+is\s+(?:located\s+in|situated\s+in|found\s+in)\s+{np}$", s)
            if m:
                a, b = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
                if a not in self._PRONOUNS and self._bare_np(a) and self._bare_np(b):
                    self.tell_part(a, b); learned["part_of"] += 1; last_subject = a
                continue
            # part-of: 'X is part of Y'
            m = re.search(rf"\b{np}\s+is\s+part\s+of\s+{np}$", s)
            if m:
                a, b = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
                if self._bare_np(a) and self._bare_np(b):
                    self.tell_part(a, b); learned["part_of"] += 1; last_subject = a
                continue
            # part-of via possession: 'X has Y' / 'X has Y and Z' -> Y (and Z) are part-of X (whole HAS part)
            m = re.match(rf"^{np}\s+(?:has|have)\s+(.+)$", s)
            if m:
                whole = self._norm_phrase(m.group(1))
                if whole not in self._PRONOUNS and self._bare_np(whole) and self._valid_concept(whole):
                    added = False
                    for obj in re.split(r"\s+and\s+|,\s*", m.group(2)):
                        obj = re.sub(r"^(?:a|an|the|many|some|several|few|most|two|three|four|five)\s+", "", obj.strip())
                        part = self._norm_phrase(obj)
                        if self._bare_np(part) and self._valid_concept(part) and part != whole:
                            self.tell_part(part, whole); learned["part_of"] += 1; added = True
                    if added:
                        last_subject = whole; continue
            # causal: 'X causes Y' / 'X leads to Y'
            m = re.search(rf"\b{np}\s+causes\s+{np}$", s) or re.search(rf"\b{np}\s+leads\s+to\s+{np}$", s)
            if m:
                a, b = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
                if self._bare_np(a) and self._bare_np(b):
                    self.tell_cause(a, b); learned["causal"] += 1
                continue
            # relative clause: 'X, which is a/an Y, ...' -> X is-a Y (then skip the main clause)
            m = re.match(rf"^{np},\s+which\s+is\s+an?\s+([a-z]+),", s)
            if m:
                a, b = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
                if a not in self._PRONOUNS and self._bare_np(a) and self._bare_np(b) and a != b:
                    self.tell(f"a {a} is a {b}."); learned["is_a"] += 1; last_subject = a
                continue
            # appositive: 'X, a kind of Y, ...' / 'X, an Y, ...' -> X is-a Y (then skip the main clause)
            m = re.match(rf"^{np},\s+(?:a\s+kind\s+of\s+|an?\s+)([a-z]+),", s)
            if m:
                a, b = self._norm_phrase(m.group(1)), self._norm_phrase(m.group(2))
                if self._bare_np(a) and self._bare_np(b) and a != b:
                    self.tell(f"a {a} is a {b}."); learned["is_a"] += 1
                continue
            # general copula 'SUBJ(s) is/are PRED(s)' with CONJOINED subjects and MULTI-FACT predicates (shallow parse)
            mc = re.match(r"^(.*?)\s+(?:is|are)\s+(.*)$", s)
            if mc:
                subjects = []
                for sub in re.split(r"\s+and\s+", mc.group(1)):
                    sub = self._norm_phrase(sub)
                    if sub not in self._PRONOUNS and self._bare_np(sub) and self._valid_concept(sub):
                        subjects.append(sub)
                parents = []
                for item in re.split(r"\s+and\s+", mc.group(2)):
                    item = item.strip().rstrip(".")
                    am = re.match(r"^(?:a\s+kind\s+of\s+|an?\s+|the\s+)([a-z][a-z\- ]*)$", item)
                    if am:                                     # article-led -> a noun parent
                        p = self._norm_phrase(am.group(1))
                        if not self._valid_concept(p) and self._bare_np(p):
                            p = p.split()[-1]                  # head-noun fallback: 'warm-blooded animal' -> 'animal'
                        if self._bare_np(p) and self._valid_concept(p):
                            parents.append(p)
                    elif re.fullmatch(r"[a-z]+s", item):       # bare PLURAL noun (ends -s, adjectives don't) -> is-a
                        p = self._norm_phrase(item)
                        if self._bare_np(p) and self._valid_concept(p):
                            parents.append(p)
                    # bare non-plural predicate (adjective/property: 'common','friendly') -> skip, not is-a
                if subjects:
                    last_subject = subjects[0]                 # remember for the next sentence's pronoun
                if subjects and parents:
                    for sub in subjects:
                        for par in parents:
                            if sub != par:
                                self.tell(f"a {sub} is a {par}."); learned["is_a"] += 1
                    # an adjective-modified parent IS-A its head noun ('a warm-blooded animal is an animal')
                    for par in set(parents):
                        head = par.split()[-1]
                        if head != par and self._valid_concept(head):
                            self.tell(f"a {par} is a {head}.")
                    continue
        return learned

    _PRONOUNS = {"it", "he", "she", "they", "this", "that", "these", "those", "i", "we", "you", "there", "which", "who"}

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

    def is_a_confidence(self, x: str, c: str) -> int:
        """Confidence-graded IS-A: the number of independent derivation PATHS from x to c in the IS-A DAG.
        Under noisy knowledge a TRUE conclusion typically has MORE supporting paths than a spurious one, so a
        path-count threshold improves precision over boolean is_a (operationalizes JEP-138's redundancy cure)."""
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        if (x, c) in self.neg_isa:
            return 0
        # count paths via memoized DP over the DAG (polynomial; acyclic assumed)
        memo = {}
        def npaths(u):
            if u == c:
                return 1
            if u in memo:
                return memo[u]
            memo[u] = 0  # guard against cycles
            total = sum(npaths(p) for p in self.parents.get(u, ()))
            memo[u] = total
            return total
        return npaths(x)

    def tell_prob(self, child: str, parent: str, p: float) -> None:
        """Record a PROBABILISTIC IS-A edge child->parent with probability p (also installs the hard edge)."""
        if not hasattr(self, "edge_prob"):
            self.edge_prob = {}
        c, pa = self._norm_phrase(child), self._norm_phrase(parent)
        self.edge_prob[(c, pa)] = float(p)
        self.parents.setdefault(c, set()).add(pa)

    def is_a_prob(self, x: str, c: str) -> float:
        """P(x is-a c): noisy-OR over derivation PATHS, each path's prob = product of its edge probs. Chains
        MULTIPLY (compounding decay, JEP-137); multiple paths noisy-OR (aggregation, JEP-138). Quantifies the
        compounding/aggregation insight. HONEST: assumes paths are INDEPENDENT (shared edges -> over-counts)."""
        x, c = self._norm_phrase(x), self._norm_phrase(c)
        ep = getattr(self, "edge_prob", {})
        paths = []
        def dfs(u, prob, seen):
            if u == c:
                paths.append(prob); return
            for par in self.parents.get(u, ()):
                if par not in seen:
                    dfs(par, prob * ep.get((u, par), 1.0), seen | {par})
        dfs(x, 1.0, {x})
        no = 1.0
        for pp in paths:
            no *= (1.0 - pp)
        return 1.0 - no

    def provenance(self, x: str, c: str):
        """Truth maintenance: the list of supporting IS-A facts (child->parent edges) along a derivation of
        'x is-a c' — the JUSTIFICATION. Returns [] if not derivable. (Returns ONE shortest justification.)"""
        chain = self._isa_chain(x, c)
        if not chain:
            return []
        return [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]

    def retract(self, child: str, parent: str) -> bool:
        """Retract a told IS-A fact (remove the edge). Conclusions depending ONLY on it become underivable;
        those with a redundant path survive — the truth-maintenance property."""
        ch, pa = self._norm_phrase(child), self._norm_phrase(parent)
        if pa in self.parents.get(ch, set()):
            self.parents[ch].discard(pa)
            return True
        return False

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

    def event(self, name: str, sets: dict = None) -> None:
        """Record a timed EVENT that sets fluents (states), e.g. event('open the door', {'door_open': True}).
        Events append to a timeline; fluents PERSIST until a later event changes them (the frame axiom)."""
        if not hasattr(self, "timeline"):
            self.timeline = []
        self.timeline.append((name, dict(sets or {})))

    def fluent_at(self, fluent: str, t: int = None):
        """Value of a fluent (state) at time t (= index in the event timeline; None = now/latest), by
        PERSISTENCE: the value set by the most recent event up to t that touched it (frame problem)."""
        tl = getattr(self, "timeline", [])
        end = len(tl) if t is None else min(t + 1, len(tl))
        val = None
        for name, sets in tl[:end]:
            if fluent in sets:
                val = sets[fluent]       # most recent change persists
        return val

    def tell_part(self, part: str, whole: str) -> None:
        """Mereology: record 'part is part-of whole' (e.g. finger part-of hand). Kept SEPARATE from IS-A —
        part-of is NOT type-of (a finger is part of a hand but is NOT a hand)."""
        if not hasattr(self, "part_of_g"):
            self.part_of_g = {}
        self.part_of_g.setdefault(self._norm(part), set()).add(self._norm(whole))

    def part_of(self, x: str, z: str) -> bool:
        """Is x part of z (transitively)? Part-of is transitive (finger->hand->body) but distinct from is_a."""
        g = getattr(self, "part_of_g", {})
        x, z = self._norm(x), self._norm(z)
        stack, seen = [x], {x}
        while stack:
            cur = stack.pop()
            for w in g.get(cur, ()):
                if w == z:
                    return True
                if w not in seen:
                    seen.add(w); stack.append(w)
        return False

    def tell_cause(self, x: str, y: str) -> None:
        """Record a causal edge x -> y (x causes y). Stored separately from IS-A (causation is not taxonomy)."""
        if not hasattr(self, "causes"):
            self.causes = {}
        self.causes.setdefault(self._norm(x), set()).add(self._norm(y))

    def achieve(self, goal: str):
        """Causal/means-ends planning: to bring about the goal EFFECT, return the ACTIONS (root causes, i.e. nodes
        with no incoming causal edge) whose causal consequences include the goal. The plan to do is any of these."""
        causes = getattr(self, "causes", {})
        g = self._norm(goal)
        has_incoming = set()
        for ys in causes.values():
            has_incoming |= ys
        roots = [n for n in causes if n not in has_incoming]   # actionable root causes
        def reaches(x):
            seen, st = {x}, [x]
            while st:
                c = st.pop()
                for d in causes.get(c, ()):
                    if d == g:
                        return True
                    if d not in seen:
                        seen.add(d); st.append(d)
            return False
        return sorted(r for r in roots if reaches(r))

    def abduce(self, effect: str):
        """Abduction (inference to the best explanation, Peirce): given an observed EFFECT, return the candidate
        CAUSES that could produce it (reverse causal closure), ranked by causal DISTANCE — the most DIRECT cause
        first (parsimony: fewest causal steps = simplest explanation)."""
        causes = getattr(self, "causes", {})
        z = self._norm(effect)
        # reverse edges
        rev = {}
        for a, ys in causes.items():
            for y in ys:
                rev.setdefault(y, set()).add(a)
        dist, frontier, seen = {}, [z], {z}
        d = 0
        while frontier:
            nxt = []
            for node in frontier:
                for cause in rev.get(node, ()):
                    if cause not in seen:
                        seen.add(cause); dist[cause] = d + 1; nxt.append(cause)
            frontier = nxt; d += 1
        return sorted(dist, key=lambda c: (dist[c], c))   # nearest cause first

    def causes_effect(self, x: str, z: str, intervene: str = None) -> bool:
        """Does x causally affect z (transitively)? Under do(intervene), the intervened node's INCOMING causal
        edges are cut (Pearl's do-operator): its value is set externally, so its usual causes no longer reach
        downstream THROUGH it from x."""
        causes = getattr(self, "causes", {})
        x, z = self._norm(x), self._norm(z)
        iv = self._norm(intervene) if intervene else None
        out, stack, seen = set(), [x], {x}
        while stack:
            cur = stack.pop()
            for nxt in causes.get(cur, ()):
                # do(iv) cuts edges INTO iv: a cause cur->iv no longer propagates (iv is set, not caused)
                if nxt == iv:
                    continue
                if nxt == z:
                    return True
                if nxt not in seen:
                    seen.add(nxt); stack.append(nxt)
        return False

    def add_rule(self, target: str, r1: str, r2: str) -> None:
        """Install a (possibly LEARNED, JEP-129) composition rule: target(x,z) :- r1(x,y) AND r2(y,z)."""
        if not hasattr(self, "rules"):
            self.rules = []
        self.rules.append((self._norm_rel(target), self._norm_rel(r1), self._norm_rel(r2)))

    def relation_holds(self, s: str, rel: str, o: str) -> bool:
        """Does relation `rel` hold between s and o — by a stored fact OR derived via a composition rule?"""
        s, rel, o = self._norm(s), self._norm_rel(rel), self._norm(o)
        if any(self._norm(fs) == s and self._norm_rel(fr) == rel and self._norm(fo) == o
               for fs, fr, fo in self.facts):
            return True
        for tgt, r1, r2 in getattr(self, "rules", []):
            if tgt == rel:
                mids = {self._norm(fo) for fs, fr, fo in self.facts
                        if self._norm(fs) == s and self._norm_rel(fr) == r1}
                for fs, fr, fo in self.facts:
                    if self._norm_rel(fr) == r2 and self._norm(fs) in mids and self._norm(fo) == o:
                        return True
        return False

    _SPATIAL_OPP = {"left": "right", "right": "left", "above": "below", "below": "above",
                    "front": "behind", "behind": "front"}

    def tell_spatial(self, a: str, rel: str, b: str) -> None:
        """Record a spatial relation 'a rel b' (e.g. a left b). Also records the inverse (b opp(rel) a)."""
        if not hasattr(self, "spatial"):
            self.spatial = {}
        a, b, rel = self._norm(a), self._norm(b), rel.lower()
        self.spatial.setdefault(rel, {}).setdefault(a, set()).add(b)
        if rel in self._SPATIAL_OPP:
            self.spatial.setdefault(self._SPATIAL_OPP[rel], {}).setdefault(b, set()).add(a)

    def spatial_holds(self, a: str, rel: str, b: str, viewpoint: str = "default") -> bool:
        """Does 'a rel b' hold (transitively)? From the OPPOSITE viewpoint, left<->right (and front<->behind) FLIP
        (allocentric perspective transform); above/below are viewpoint-invariant."""
        rel = rel.lower()
        if viewpoint == "opposite" and rel in ("left", "right", "front", "behind"):
            rel = self._SPATIAL_OPP[rel]
        g = getattr(self, "spatial", {}).get(rel, {})
        a, b = self._norm(a), self._norm(b)
        stack, seen = [a], {a}
        while stack:
            cur = stack.pop()
            for nxt in g.get(cur, ()):
                if nxt == b:
                    return True
                if nxt not in seen:
                    seen.add(nxt); stack.append(nxt)
        return False

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
        # mereology: parts that x HAS (things that are part-of x), and what x is part-of
        part_of_g = getattr(self, "part_of_g", {})
        xn = self._norm(x)
        has_parts = sorted(p for p, wholes in part_of_g.items() if xn in wholes)
        if has_parts:
            sents.append(("Its parts include " if len(has_parts) > 1 else "It has ")
                         + ", ".join(self._art(p) for p in has_parts) + ".")
        wholes = sorted(self._part_ancestors(xn)) if hasattr(self, "_part_ancestors") else sorted(part_of_g.get(xn, set()))
        if wholes:
            sents.append("It is part of " + ", ".join(self._art(w) for w in wholes) + ".")
        # causal: effects x brings about, and what causes x
        causes = getattr(self, "causes", {})
        effects = sorted(causes.get(xn, set()))
        if effects:
            sents.append("It causes " + ", ".join(self._art(e) for e in effects) + ".")
        triggers = sorted(c for c, ys in causes.items() if xn in ys)
        if triggers:
            sents.append("It is caused by " + ", ".join(self._art(t) for t in triggers) + ".")
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
        # MEREOLOGY / CAUSAL questions (read() learns these; route them before the generic WH/explain fallback)
        art = r"(?:(?:an|a|the)\s+)?"
        m = re.match(rf"(?:is|are)\s+{art}(\w+)\s+part\s+of\s+{art}(\w+)", q)   # 'is a heart part of a dog?'
        if m:
            a, b = self._norm(m.group(1)), self._norm(m.group(2))
            tail = (f"{self._art(a)} is part of {self._art(b)}." if self.part_of(a, b)
                    else f"{self._art(a)} is not part of {self._art(b)} as far as I know.")
            return ("Yes. " if self.part_of(a, b) else "No. ") + tail[0].upper() + tail[1:]
        m = re.match(rf"what\s+(?:is|are)\s+(?:the\s+)?parts?\s+of\s+{art}(\w+)", q)  # 'what is part of a dog?'
        if m:
            x = self._norm(m.group(1))
            parts = sorted(p for p, wholes in getattr(self, "part_of_g", {}).items() if x in wholes)
            if parts:
                joined = ", ".join(self._art(p) for p in parts)
                ans = f"{joined} {'is' if len(parts) == 1 else 'are'} part of {self._art(x)}."
                return ans[0].upper() + ans[1:]
            return f"I don't know what is part of {self._art(x)}."
        m = re.match(rf"does\s+{art}(\w+)\s+cause\s+{art}(\w+)", q)              # 'does a virus cause a fever?'
        if m:
            a, b = self._norm(m.group(1)), self._norm(m.group(2))
            if self.causes_effect(a, b):
                tail = f"{self._art(a)} causes {self._art(b)}."
                return "Yes. " + tail[0].upper() + tail[1:]
            return "No, not that I can tell."
        m = re.match(rf"what\s+causes\s+{art}(\w+)", q)                         # 'what causes a fever?'
        if m:
            z = self._norm(m.group(1)); causes = self.abduce(z)
            if causes:
                tail = f"{self._art(causes[0])} causes {self._art(z)}."
                return tail[0].upper() + tail[1:]
            return f"I don't know what causes {self._art(z)}."
        m = re.match(rf"what\s+does\s+{art}(\w+)\s+cause", q)                   # 'what does a virus cause?'
        if m:
            x = self._norm(m.group(1)); effs = sorted(getattr(self, "causes", {}).get(x, set()))
            if effs:
                tail = f"{self._art(x)} causes {', '.join(self._art(e) for e in effs)}."
                return tail[0].upper() + tail[1:]
            return f"I don't know what {self._art(x)} causes."
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
