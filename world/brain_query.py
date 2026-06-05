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
        self._gates = {}
        self.gate = self._gate_for("isa")            # default/global gate (back-compat)

    def _gate_for(self, role):
        """Gate calibrated on THIS relation's own edges (cached). High-fan-out relations need their own gate
        (JEP-323): an isa-calibrated gate over-rejects a key holding many values. Falls back to the global isa gate
        when a relation has too few edges to calibrate."""
        if role in self._gates:
            return self._gates[role]
        m = self.mem
        edges = [(a, b) for (a, r, b) in m.facts if r == role]
        rng = np.random.default_rng(self.seed)
        if len(edges) < 3 and role != "isa":
            g = self._gate_for("isa")                # too sparse -> fall back
            self._gates[role] = g
            return g
        samp = [edges[i] for i in rng.choice(len(edges), min(30, len(edges)), replace=False)] if edges else []
        t = np.mean([m.edge_sim(a, role, b) for (a, b) in samp]) if samp else 0.2
        u = np.mean([m.query(f"none_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
        g = float((t + u) / 2)
        self._gates[role] = g
        return g

    # ---- ancestors / climb ----
    def _ancestors(self, x, role="isa", mx=30):
        from collections import deque
        g = self._gate_for(role)
        q, seen, out = deque([x]), {x}, [x]
        while q and len(out) < mx:
            cur = q.popleft()
            for (p, _) in self.mem.query_all(cur, role, g):
                if p not in seen:
                    seen.add(p); out.append(p); q.append(p)
        return out

    # ---- answer types (each uses the gate calibrated for ITS relation) ----
    def is_a(self, x, y):
        if self.mem.contains(x, "not_isa", y, self._gate_for("not_isa")):
            return False
        return y in self._ancestors(x, "isa")[1:] or \
            y in [p for (p, _) in self.mem.query_all(x, "isa", self._gate_for("isa"))]

    def has_property(self, x, p):
        gp, gn = self._gate_for("hasprop"), self._gate_for("not_hasprop")
        for a in self._ancestors(x, "isa"):           # most specific first (BFS order ~ depth)
            if self.mem.contains(a, "not_hasprop", p, gn):
                return False
            if self.mem.contains(a, "hasprop", p, gp):
                return True
        return False

    def why(self, effect):
        return sorted(c for (c, _) in self.mem.query_all(effect, "caused_by", self._gate_for("caused_by")))

    def what(self, x, verb):
        # try the verb plus simple morphological variants (eat->eats), so "what does a cat eat?" finds "eats"
        roles = {r for (_, r, _) in self.mem.facts}
        for v in [verb, verb + "s", verb + "es", verb.rstrip("s"), verb[:-1] if verb.endswith("e") else verb]:
            if v in roles:
                res = sorted(o for (o, _) in self.mem.query_all(x, v, self._gate_for(v)))
                if res:
                    return res
        return sorted(o for (o, _) in self.mem.query_all(x, verb, self._gate_for(verb)))

    # ---- tiny natural-question parser ----
    def ask(self, q):
        s = q.strip().lower().rstrip("?").strip()
        s = re.sub(r"\b(a|an|the)\b", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        m = re.match(r"is (\w+) (\w+)$", s)
        if m:
            return self.is_a(m.group(1), m.group(2))
        m = re.match(r"can (\w+) (\w+)$", s)
        if m:
            return self.has_property(m.group(1), m.group(2))
        m = re.match(r"does (\w+) have (\w+)$", s)
        if m:
            return self.has_property(m.group(1), m.group(2))
        m = re.match(r"what causes (\w+)$", s)
        if m:
            return self.why(m.group(1))
        m = re.match(r"what does (\w+) (\w+)$", s)
        if m:
            return self.what(m.group(1), m.group(2))
        return None
