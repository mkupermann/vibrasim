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
        return y in self._ancestors(x, "isa")[1:] or \
            y in [p for (p, _) in self.mem.query_all(x, "isa", self.gate)]

    def has_property(self, x, p):
        for a in self._ancestors(x, "isa"):           # most specific first (BFS order ~ depth)
            if self.mem.contains(a, "not_hasprop", p, self.gate):
                return False
            if self.mem.contains(a, "hasprop", p, self.gate):
                return True
        return False

    def why(self, effect):
        return sorted(c for (c, _) in self.mem.query_all(effect, "caused_by", self.gate))

    def how_many(self, x):
        for a in self._ancestors(x, "isa"):
            v, s = self.mem.query(a, "has_legs")
            if v is not None and s >= self.gate:
                try:
                    return int(v)
                except (ValueError, TypeError):
                    return v
        return None

    def part_of(self, y, x):
        for (p, _) in self.mem.query_all(y, "partof", self.gate):
            if p == x or p in self._ancestors(x, "isa"):
                return True
        return any(self.mem.contains(y, "partof", a, self.gate) for a in self._ancestors(x, "isa"))

    def describe(self, x):
        """A spoken summary of what is known about x."""
        bits = []
        parent, s = self.mem.query(x, "isa")
        if parent is not None and s >= self.gate:
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
        return ("; ".join(bits) + ".").capitalize() if bits else f"I don't know much about {x} yet."

    def what(self, x, verb):
        # try the verb plus simple morphological variants (eat->eats), so "what does a cat eat?" finds "eats"
        roles = {r for (_, r, _) in self.mem.facts}
        for v in [verb, verb + "s", verb + "es", verb.rstrip("s"), verb[:-1] if verb.endswith("e") else verb]:
            if v in roles:
                res = sorted(o for (o, _) in self.mem.query_all(x, v, self.gate))
                if res:
                    return res
        return sorted(o for (o, _) in self.mem.query_all(x, verb, self.gate))

    # ---- tiny natural-question parser ----
    def ask(self, q):
        s = q.strip().lower().rstrip("?").strip()
        s = re.sub(r"\b(a|an|the)\b", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        m = re.match(r"tell me about (\w+)$", s) or re.match(r"describe (\w+)$", s)
        if m:
            return self.describe(m.group(1))
        m = re.match(r"how many \w+ does (\w+) have$", s) or re.match(r"how many \w+ (?:does|do) (\w+) have$", s)
        if m:
            return self.how_many(m.group(1))
        m = re.match(r"is (\w+) (?:kind of |type of )?(\w+)$", s)   # 'a/an/the' already stripped above
        if m:
            return self.is_a(m.group(1), m.group(2))
        m = re.match(r"can (\w+) (\w+)$", s)
        if m:
            return self.has_property(m.group(1), m.group(2))
        m = re.match(r"does (\w+) have (?:any )?(\w+)$", s) or re.match(r"do (\w+)s? have (?:any )?(\w+)$", s)
        if m:
            x, p = m.group(1), m.group(2)
            # "have legs" -> numeric; "have <part>" -> part_of; else property
            if p in ("legs", "leg"):
                return self.how_many(x) not in (None, 0)
            return self.has_property(x, p) or self.part_of(p.rstrip("s"), x)
        m = re.match(r"what causes (\w+)$", s)
        if m:
            return self.why(m.group(1))
        m = re.match(r"what is (\w+)$", s)               # "what is a poodle?" -> its (most specific) parent class
        if m:
            v, sc = self.mem.query(m.group(1), "isa")
            return v if (v is not None and sc >= self.gate) else None
        m = re.match(r"what does (\w+) (\w+)$", s)
        if m:
            return self.what(m.group(1), m.group(2))
        return None
