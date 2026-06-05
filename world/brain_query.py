"""brain_query — one interface to ASK the durable substrate brain.

Wraps a loaded SubstrateMemory, auto-calibrates the retrieval gate once, and answers the common question types by
routing to the right substrate operation (multi-hop is-a with negation/exception, defeasible properties, abduction,
open relations). A tiny string parser maps natural questions to these. No transformer, no pretrained model.
"""
import re
import numpy as np


class BrainQuery:
    def __init__(self, mem, seed: int = 0):
        self.mem = mem
        self.seed = seed
        self.gate = self._gate_for("isa")            # one auto-calibrated gate suffices (JEP-326: per-value sim is
        #                                              governed by module load, shared across relations -> a
        #                                              per-relation gate gave no meaningful benefit, gap <=0.033)
        # analog gate for closed (consolidated) is-a: the magnitude-preserving readout has its own scale (JEP-378)
        self._gate_analog = self._gate_for_analog("isa") if "isa" in getattr(mem, "closed_relations", ()) else None

    def _gate_for_analog(self, role):
        m = self.mem
        edges = [(a, b) for (a, r, b) in m.facts if r == role]
        if not edges:
            return None
        rng = np.random.default_rng(self.seed)
        samp = [edges[i] for i in rng.choice(len(edges), min(30, len(edges)), replace=False)]
        t = np.mean([m.edge_sim_analog(a, role, b) for (a, b) in samp])
        u = np.mean([m.edge_sim_analog(f"none_{int(rng.integers(1e9))}", role,
                                       f"non_{int(rng.integers(1e9))}") for _ in range(30)])
        return float((t + u) / 2)

    def _gate_for(self, role):
        m = self.mem
        edges = [(a, b) for (a, r, b) in m.facts if r == role]
        rng = np.random.default_rng(self.seed)
        if len(edges) < 3 and role != "isa" and any(r == "isa" for (_, r, _) in m.facts):
            return self.gate                          # too sparse to calibrate -> use the global gate
        samp = [edges[i] for i in rng.choice(len(edges), min(30, len(edges)), replace=False)] if edges else []
        t = np.mean([m.edge_sim(a, role, b) for (a, b) in samp]) if samp else 0.2
        u = np.mean([m.query(f"none_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
        return float((t + u) / 2)

    # ---- ancestors / climb ----
    def _ancestors(self, x, role="isa", mx=30):
        from collections import deque
        q, seen, out = deque([x]), {x}, [x]
        while q and len(out) < mx:
            cur = q.popleft()
            for (p, _) in self.mem.query_all(cur, role, self.gate):
                if p not in seen:
                    seen.add(p); out.append(p); q.append(p)
        return out

    # ---- answer types (one auto-calibrated gate; see JEP-326) ----
    def is_a(self, x, y):
        if self.mem.contains(x, "not_isa", y, self.gate):
            return False
        # JEP-375/378: if the is-a closure is materialized, every true ancestor is a DIRECT edge -> answer by single-hop
        # membership and SKIP the recursive walk (the BFS over a consolidated store inflates false-positives). Use the
        # ANALOG readout (magnitude-preserving) which separates faint deep edges from near-misses where sign cannot,
        # closing the deep-recall floor (JEP-377).
        if "isa" in getattr(self.mem, "closed_relations", ()) and self._gate_analog is not None:
            return self.mem.edge_sim_analog(x, "isa", y) >= self._gate_analog
        return y in [p for (p, _) in self.mem.query_all(x, "isa", self.gate)] or \
            y in self._ancestors(x, "isa")[1:]

    def has_property(self, x, p):
        # most-specific-first is REQUIRED for exceptions to win (penguin not_hasprop fly beats bird hasprop fly).
        # After closure consolidation _ancestors is FLAT (arbitrary cleanup order), so sort by specificity = number of
        # own ancestors (deeper = more specific) so the answer is provably correct, not cleanup-order-dependent (JEP-398).
        anc = self._ancestors(x, "isa")
        anc = sorted(anc, key=lambda a: len(self._ancestors(a, "isa")), reverse=True)
        for a in anc:
            if self.mem.contains(a, "not_hasprop", p, self.gate):
                return False
            if self.mem.contains(a, "hasprop", p, self.gate):
                return True
        return False

    def why(self, effect):
        # trace the causal chain transitively (immediate causes first, then their causes) — JEP-400.
        out, seen, frontier = [], {effect}, [effect]
        while frontier:
            nxt = []
            for e in frontier:
                for (c, _) in self.mem.query_all(e, "caused_by", self.gate):
                    if c not in seen:
                        seen.add(c); out.append(c); nxt.append(c)
            frontier = nxt
        return out

    def how_many(self, x, part="legs"):
        role = f"has_{part}"                              # JEP-390: any counted part, not just legs
        for a in self._ancestors(x, "isa"):
            v, s = self.mem.query(a, role)
            if v is not None and s >= self.gate:
                try:
                    return int(v)
                except (ValueError, TypeError):
                    return v
        return None

    @staticmethod
    def _vstem(w):
        return w[:5] if len(w) >= 5 else w               # crude verb stem (domesticate ~ domesticated)

    def who_did(self, verb, obj):
        """Reverse open-relation: subjects of stored (subject, ~verb, obj)."""
        vs = self._vstem(verb)
        return sorted({s for (s, r, o) in self.mem.facts if o == obj and self._vstem(r) == vs})

    def what_did(self, subj, verb):
        """Forward open-relation: objects of stored (subj, ~verb, object)."""
        vs = self._vstem(verb)
        return sorted({o for (s, r, o) in self.mem.facts if s == subj and self._vstem(r) == vs})

    def part_of(self, y, x):
        for (p, _) in self.mem.query_all(y, "partof", self.gate):
            if p == x or p in self._ancestors(x, "isa"):
                return True
        return any(self.mem.contains(y, "partof", a, self.gate) for a in self._ancestors(x, "isa"))

    def _most_specific_parent(self, x):
        """The most-specific is-a parent of x. After closure consolidation every ancestor is a DIRECT edge, so pick the
        deepest candidate (most ancestors of its own) rather than an arbitrary one (JEP-397)."""
        cands = [p for (p, _) in self.mem.query_all(x, "isa", self.gate)]
        if not cands:
            v, s = self.mem.query(x, "isa")
            return v if (v is not None and s >= self.gate) else None
        return max(cands, key=lambda c: len(self._ancestors(c, "isa")))

    def describe(self, x):
        """A spoken summary of what is known about x."""
        bits = []
        parent = self._most_specific_parent(x)
        if parent is not None:
            bits.append(f"a {x} is {'an' if parent[0] in 'aeiou' else 'a'} {parent}")
        props = []
        for a in self._ancestors(x, "isa"):
            for (p, _) in self.mem.query_all(a, "hasprop", self.gate):
                if not self.mem.contains(x, "not_hasprop", p, self.gate) and p not in props:
                    props.append(p)
        if props:
            bits.append("it can " + ", ".join(props[:4]))
        n = self.how_many(x)
        if n is not None:
            bits.append(f"it has {n} legs")
        # parts: things that are part-of x or an ancestor of x (JEP-396)
        targets = set(self._ancestors(x, "isa"))
        parts = sorted({p for (p, r, o) in self.mem.facts if r == "partof" and o in targets})
        if parts:
            bits.append("it has " + ", ".join(f"{'an' if p[0] in 'aeiou' else 'a'} {p}" for p in parts[:4]))
        # open relations where x is the subject (actions/attributes): 'it likes coffee', 'its name is X' (JEP-409)
        _STRUCT = {"isa", "hasprop", "not_hasprop", "not_isa", "partof", "caused_by", "located_in"}
        for (s, r, o) in self.mem.facts:
            if s == x and r not in _STRUCT and not r.startswith("has_"):
                val = str(o).replace("_", " ")
                bits.append(f"its {r} is {val}" if r in ("name", "role", "creator", "capital", "age", "color")
                            else f"it {r} {val}")
        return ("; ".join(bits[:8]) + ".").capitalize() if bits else f"I don't know much about {x} yet."

    def what(self, x, verb):
        # try the verb plus simple morphological variants (eat->eats), so "what does a cat eat?" finds "eats"
        roles = {r for (_, r, _) in self.mem.facts}
        for v in [verb, verb + "s", verb + "es", verb.rstrip("s"), verb[:-1] if verb.endswith("e") else verb]:
            if v in roles:
                res = sorted(o for (o, _) in self.mem.query_all(x, v, self.gate))
                if res:
                    return res
        return sorted(o for (o, _) in self.mem.query_all(x, verb, self.gate))

    def _sing(self, w):
        """Singular fallback: 'poodles' -> 'poodle' when only the singular is a known concept."""
        subjects = {a for (a, _, _) in self.mem.facts}
        if w in subjects:
            return w
        for cand in (w[:-1] if w.endswith("s") else None, w[:-2] if w.endswith("es") else None):
            if cand and cand in subjects:
                return cand
        return w

    def _attr(self, entity, attr):
        """Look up a taught attribute value (entity, attr, value); display joined proper nouns nicely (JEP-404)."""
        v, sc = self.mem.query(entity, attr)
        if v is None or sc < self.gate:
            return None
        return " ".join(w.capitalize() for w in str(v).split("_"))

    # ---- tiny natural-question parser ----
    def ask(self, q):
        s = q.strip().lower().rstrip("?").strip()
        s = re.sub(r"\bwas\b", "is", s); s = re.sub(r"\bwere\b", "are", s)   # past tense -> present (JEP-405)
        # attribute questions FIRST (before articles are stripped, to keep 'your'): JEP-404
        m = re.match(r"^(?:who|what)\s+is\s+your\s+([a-z]+)$", s)
        if m:
            return self._attr("you", self._sing(m.group(1)))
        m = re.match(r"^(?:who|what)\s+is\s+my\s+([a-z]+)$", s)            # first-person attribute (JEP-405)
        if m:
            return self._attr("user", self._sing(m.group(1)))
        if s in ("what am i", "what am i?"):                              # first/second-person is-a (JEP-406)
            return self._most_specific_parent("user")
        if s in ("what are you", "what are you?"):
            return self._most_specific_parent("you")
        m = re.match(r"^where\s+is\s+(?:the\s+)?([a-z]+)$", s)             # 'where is Paris?' -> located_in (JEP-406)
        if m:
            v, sc = self.mem.query(self._sing(m.group(1)), "located_in")
            return (v.capitalize() if (v is not None and sc >= self.gate) else None)
        m = re.match(r"^(?:who|what)\s+is\s+(?:the\s+)?([a-z]+)\s+of\s+(.+)$", s)   # 'what is the name of your creator'
        if m:
            ent = re.sub(r"^(?:your|the|a|an)\s+", "", m.group(2).strip())
            ent = "you" if ent in ("you", "yours") else self._sing(ent.split()[0])
            return self._attr(ent, self._sing(m.group(1)))
        m = re.match(r"^what\s+is\s+([a-z]+)'s\s+([a-z]+)$", s)                      # "what is michael's role"
        if m:
            return self._attr(self._sing(m.group(1)), self._sing(m.group(2)))
        s = re.sub(r"\b(a|an|the)\b", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        m = re.match(r"who (\w+) (\w+)$", s)             # "who domesticated the cat?" -> reverse open-relation
        if m:
            r = self.who_did(m.group(1), self._sing(m.group(2))) or self.who_did(m.group(1), m.group(2))
            return r or None
        m = re.match(r"what was (\w+) (\w+) by$", s)      # "what was the cat domesticated by?" -> reverse
        if m:
            r = self.who_did(m.group(2), self._sing(m.group(1))) or self.who_did(m.group(2), m.group(1))
            return r or None
        m = re.match(r"what did (\w+) (\w+)$", s)         # "what did humans domesticate?" -> forward open-relation
        if m:
            return self.what_did(m.group(1), m.group(2)) or None
        m = re.match(r"do (\w+) (\w+)$", s)              # "do poodles bark?" -> has_property(poodle, bark)
        if m:
            return self.has_property(self._sing(m.group(1)), m.group(2))
        m = re.match(r"tell me about (\w+)$", s) or re.match(r"describe (\w+)$", s)
        if m:
            return self.describe(m.group(1))
        m = re.match(r"how many (\w+) (?:does|do) (\w+) have$", s)   # capture the part (JEP-390)
        if m:
            return self.how_many(m.group(2), part=m.group(1))
        m = re.match(r"is (\w+) part of (\w+)$", s)                 # 'a/an/the' already stripped above (JEP-388)
        if m:
            return self.part_of(self._sing(m.group(1)), self._sing(m.group(2)))
        m = re.match(r"is (\w+) (?:kind of |type of )?([\w-]+)$", s)   # allow hyphenated property/class (JEP-394)
        if m:
            x, y = m.group(1), m.group(2)
            # 'is X Y?' is ambiguous between class membership and property -> yes if EITHER holds (JEP-394)
            return bool(self.is_a(x, y) or self.has_property(x, y))
        m = re.match(r"can (\w+) (\w+)$", s)
        if m:
            return self.has_property(m.group(1), m.group(2))
        m = re.match(r"are (\w+) ([\w-]+)$", s)         # "are dogs loyal?" -> is_a OR has_property (JEP-405)
        if m:
            x = self._sing(m.group(1))
            return bool(self.is_a(x, m.group(2)) or self.has_property(x, m.group(2)))
        m = re.match(r"does (\w+) have (?:any )?(\w+)$", s) or re.match(r"do (\w+)s? have (?:any )?(\w+)$", s)
        if m:
            x, p = m.group(1), m.group(2)
            # "have legs" -> numeric; "have <part>" -> part_of; else property
            if p in ("legs", "leg"):
                return self.how_many(x) not in (None, 0)
            return self.has_property(x, p) or self.part_of(p.rstrip("s"), x)
        m = re.match(r"what causes (\w+)$", s)
        if m:
            return self.why(m.group(1)) or None
        m = re.match(r"why does (\w+) happen$", s) or re.match(r"why (\w+)$", s)   # 'why does X happen?' -> abduction
        if m:
            return self.why(self._sing(m.group(1))) or None
        m = re.match(r"what is (\w+)$", s)               # "what is a poodle?" -> its most-specific parent class
        if m:
            return self._most_specific_parent(m.group(1))   # deepest ancestor after consolidation (JEP-397)
        m = re.match(r"what (?:does|do) (\w+)s? have$", s)    # 'what does a dog have?' -> its parts (JEP-407)
        if m:
            x = self._sing(m.group(1))
            targets = set(self._ancestors(x, "isa"))
            parts = sorted({p for (p, r, o) in self.mem.facts if r == "partof" and o in targets})
            return parts or None
        m = re.match(r"what do (\w+) (\w+)$", s)              # 'what do dogs eat?' -> forward open-relation (JEP-407)
        if m:
            x = self._sing(m.group(1))
            return self.what_did(x, m.group(2)) or self.what(x, m.group(2)) or None
        m = re.match(r"what does (\w+) (\w+)$", s)
        if m:
            return self.what(m.group(1), m.group(2))
        return None
