"""substrate_memory — make the substrate's memory DURABLE and GROWABLE (per Michael: 'it can't die when the program
closes; store it and let it grow like a brain').

Until now the memory lived only in RAM: the VSA relational store (facts superposed in one bundle vector + a
cleanup dictionary) and the perceptual ActiveLearner (taught exemplars). This wraps both and serializes them to a
real FOLDER OF FILES you can copy, back up, and keep growing:
    <dir>/vectors.npz   - the superposed memory vector (accum), value vocabulary, exemplar block
    <dir>/meta.json     - dimension, atom/value/fact registry, learner scalars

Teach -> save -> close -> reopen -> load: the knowledge is still there, and you can add more without erasing the
old (lifelong learning). Atom vectors are derived DETERMINISTICALLY from their name via hashlib (cross-process
stable), so a separate program reading the folder reconstructs the identical vectors. No transformer, no
pretrained model -- only the substrate's own VSA primitives (world/vsa).
"""
import os
import json
import hashlib
import functools
import numpy as np

from world.vsa import bind, unbind, sim, CleanupMemory
from world.active_learner import ActiveLearner

DEFAULT_D = 4096


@functools.lru_cache(maxsize=200_000)
def atom_vector(name: str, D: int) -> np.ndarray:
    """A deterministic, cross-process-stable bipolar hypervector for a symbol name (hashlib-seeded, NOT builtin
    hash() which is per-process salted). Same name -> same vector everywhere; different names -> near-orthogonal.
    Cached: the VSA ops never mutate their inputs, so returning the shared array is safe and avoids re-hashing."""
    seed = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
    return np.random.default_rng(seed).choice([-1.0, 1.0], D)


class SubstrateMemory:
    def __init__(self, D: int = DEFAULT_D, tau: float = 0.12, module_cap: int = None, directed: bool = False):
        self.D = D
        # DIRECTED edges (JEP-298): store the value PERMUTED (rho = circular shift) so an edge is recovered forward
        # only; a backward probe yields rho(x)*x noise the cleanup rejects. Needed for transitive inference; the
        # default symmetric path (JEP-294/295/296 key->value) is unchanged.
        self.directed = directed
        # GROWING store (JEP-296): a STACK of bundle modules. When the current module saturates (~0.8*D/32 facts)
        # a new empty module is added (neurogenesis), so total capacity is unbounded (linear in #modules).
        self.module_cap = module_cap or max(1, int(0.8 * D / 32))
        self.modules = [np.zeros(D, dtype=np.float64)]   # running SUM per module; mem_m = sign(module)
        self.module_counts = [0]
        # module-aware routing (JEP-307): which module(s) hold each (entity, role) key -> search only those, so a
        # multi-hop chain never gets hijacked by a spurious global-argmax match in a non-holding module.
        self.key_modules = {}                            # "entity\x1frole" -> sorted list of module indices
        self.facts = []                              # list of (entity, role, value) for bookkeeping/growth
        self.values = []                             # value vocabulary (the cleanup dictionary)
        self.sentences = []                          # taught PROSE (JEP-302) — replayed to rebuild the engine
        self.learner = ActiveLearner(tau=tau)        # perceptual memory (taught exemplars)

    # ---- atom / vector helpers ----
    def _vec(self, name):
        return atom_vector(name, self.D)

    @property
    def accum(self):
        return self.modules[0]                       # back-compat alias (single-module callers)

    @staticmethod
    def _kk(entity, role):
        return f"{entity}\x1f{role}"

    def _route(self, entity, role):
        """Module indices to search for (entity, role). Empty routing table -> all modules (back-compat); known
        table but key absent -> [] (untaught key -> clean no-match)."""
        if not self.key_modules:
            return range(len(self.modules))
        return self.key_modules.get(self._kk(entity, role), [])

    def _mem(self, m):
        s = np.sign(self.modules[m]); s[s == 0] = 1.0
        return s

    def _value_matrix(self):
        """(V, D) matrix of value vectors + names, cached and rebuilt only when the vocabulary grows."""
        if getattr(self, "_vm_n", -1) != len(self.values):
            self._vm = np.stack([self._vec(v) for v in self.values]) if self.values else np.zeros((0, self.D))
            self._vm_names = list(self.values)
            self._vm_n = len(self.values)
        return self._vm, self._vm_names

    # ---- relational facts ----
    def add_fact(self, entity: str, role: str, value: str):
        """Store 'entity's role IS value' as bind(entity*role, value) superposed into the current module. When that
        module fills (module_cap), auto-add a fresh module so growth is unbounded (JEP-296)."""
        if self.module_counts[-1] >= self.module_cap:
            self.modules.append(np.zeros(self.D, dtype=np.float64))   # neurogenesis: a new module
            self.module_counts.append(0)
        val = np.roll(self._vec(value), 1) if self.directed else self._vec(value)
        bound = bind(bind(self._vec(entity), self._vec(role)), val)
        self.modules[-1] = self.modules[-1] + bound
        self.module_counts[-1] += 1
        m = len(self.modules) - 1
        ms = self.key_modules.setdefault(self._kk(entity, role), [])
        if m not in ms:
            ms.append(m)
        self.facts.append((entity, role, value))
        if value not in self.values:
            self.values.append(value)

    def query(self, entity: str, role: str):
        """Recover the value bound to (entity, role): (value_name, similarity). Searches ALL modules and returns the
        single best cleanup match (the module that actually holds this fact wins)."""
        key = bind(self._vec(entity), self._vec(role))
        VM, names = self._value_matrix()
        mods = list(self._route(entity, role))
        if not names or not mods:
            return None, 0.0
        Mstack = np.stack([self._mem(m) for m in mods])                       # only holding modules (routing)
        retrieved = Mstack * key                                              # unbind each module by the key
        if self.directed:
            retrieved = np.roll(retrieved, -1, axis=1)                        # rho^-1: undo the value permutation
        scores = retrieved @ VM.T / self.D                                    # (n_mod, V) cleanup similarities
        flat = int(np.argmax(scores))
        return names[flat % len(names)], float(scores.flat[flat])

    def query_all(self, entity: str, role: str, gate: float):
        """Set-valued retrieval (JEP-303): ALL values bound to (entity, role) with cleanup similarity >= gate, for
        multi-parent / DAG relations. Returns [(value_name, sim), ...] sorted by sim."""
        key = bind(self._vec(entity), self._vec(role))
        VM, names = self._value_matrix()
        mods = list(self._route(entity, role))
        if not names or not mods:
            return []
        Mstack = np.stack([self._mem(m) for m in mods])
        retrieved = Mstack * key
        if self.directed:
            retrieved = np.roll(retrieved, -1, axis=1)
        scores = (retrieved @ VM.T / self.D).max(axis=0)        # best holding-module per value
        out = [(names[i], float(scores[i])) for i in range(len(names)) if scores[i] >= gate]
        return sorted(out, key=lambda t: -t[1])

    def edge_sim(self, entity: str, role: str, value: str):
        """Similarity that (entity, role, value) is a stored edge — max over modules of the cleaned retrieval vs the
        value vector. Works for MULTI-valued relations (causal/property) where several values share one key."""
        key = bind(self._vec(entity), self._vec(role))
        vv = self._vec(value)
        best = -1e9
        for m in self._route(entity, role):
            r = self._mem(m) * key
            if self.directed:
                r = np.roll(r, -1)
            best = max(best, float(r @ vv / self.D))
        return best if best > -1e8 else 0.0

    def contains(self, entity: str, role: str, value: str, gate: float):
        """Membership probe for a (possibly multi-valued) relation: is `value` bound to (entity, role)?"""
        return self.edge_sim(entity, role, value) >= gate

    def detect_conflicts(self, gate, pairs=(("hasprop", "not_hasprop"), ("isa", "not_isa"))):
        """Find genuine CONTRADICTIONS: a node holding both a positive and negative DIRECT edge for the same target.
        Uses direct-edge contains(), so a defeasible exception (inherited positive + explicit negative) is NOT a
        contradiction — only a direct double-assertion is. Returns [(entity, pos_role, value), ...]."""
        out = []
        for pos, neg in pairs:
            pset = {(s, o) for (s, r, o) in self.facts if r == pos}
            nset = {(s, o) for (s, r, o) in self.facts if r == neg}
            for (x, v) in sorted(pset & nset):
                if self.contains(x, pos, v, gate) and self.contains(x, neg, v, gate):
                    out.append((x, pos, v))
        return out

    # ---- taught prose -> durable knowledge (JEP-302) ----
    def ingest_engine(self, eng):
        """Bridge an UnderstandingEngine's learned relation graphs into the directed substrate store — including
        NEGATIVE facts (exceptions, negative is-a) and the inverse causal edge (for abduction). Idempotent: skips
        facts already present, so repeated calls (one per taught sentence) don't bloat the store."""
        have = set(self.facts)

        def _add(a, r, b):
            if (a, r, b) not in have:
                self.add_fact(a, r, b); have.add((a, r, b))

        for attr, role in [("parents", "isa"), ("part_of_g", "partof"), ("causes", "causes"),
                           ("properties", "hasprop"), ("not_properties", "not_hasprop")]:
            for a, bs in dict(getattr(eng, attr, {}) or {}).items():
                for b in bs:
                    _add(a, role, b)
                    if role == "causes":
                        _add(b, "caused_by", a)               # inverse, enables abduction (why?)
        for (a, b) in (getattr(eng, "neg_isa", set()) or set()):
            _add(a, "not_isa", b)

    def learn_sentence(self, sentence: str, eng):
        """Record taught prose AND bridge its facts into the substrate (the engine parses; we store both)."""
        eng.read(sentence)
        self.sentences.append(sentence)
        self.ingest_engine(eng)

    def rebuild_engine(self, seed: int = 0):
        """Replay the taught corpus into a fresh UnderstandingEngine (the durable knowledge, re-read)."""
        from world.understanding import UnderstandingEngine
        eng = UnderstandingEngine(seed=seed)
        for s in self.sentences:
            eng.read(s)
        return eng

    # ---- perceptual facts (taught letters/sounds) ----
    def teach_percept(self, modality: str, symbol: str, x):
        self.learner.teach(modality, symbol, np.asarray(x, dtype=np.float64))

    def recognize(self, modality: str, x):
        return self.learner.guess(modality, np.asarray(x, dtype=np.float64))

    def has_resolvable_corrections(self):
        """True if some direct positive fact is overridden by a negation (so compaction would reclaim it)."""
        facts = set(self.facts)
        for (pos, neg) in (("isa", "not_isa"), ("hasprop", "not_hasprop")):
            for (s, r, o) in facts:
                if r == neg and (s, pos, o) in facts:
                    return True
        return False

    def compact(self):
        """Rebuild from LIVE facts only, reclaiming capacity from resolved corrections (JEP-334). A direct positive
        fact that a negation overrides is dropped together with that now-moot negation; standalone negations
        (exceptions over INHERITED facts) are kept. Returns a fresh compacted SubstrateMemory; answers are preserved."""
        facts = set(self.facts)
        dead = set()
        for (pos, neg) in (("isa", "not_isa"), ("hasprop", "not_hasprop")):
            for (s, r, o) in list(facts):
                if r == neg and (s, pos, o) in facts:        # a resolved DIRECT correction -> both die
                    dead.add((s, pos, o)); dead.add((s, neg, o))
        live = [f for f in self.facts if f not in dead]
        new = SubstrateMemory(D=self.D, tau=self.learner.tau, module_cap=self.module_cap, directed=self.directed)
        for (a, r, b) in live:
            new.add_fact(a, r, b)
        new.sentences = list(self.sentences)
        new.learner = self.learner
        return new

    # ---- persistence ----
    def save(self, d: str):
        os.makedirs(d, exist_ok=True)
        # flatten ActiveLearner exemplars into one block + parallel label arrays
        ex_rows, ex_mod, ex_sym = [], [], []
        for (mod, sym), lst in self.learner.protos.items():
            for v in lst:
                ex_rows.append(np.asarray(v, dtype=np.float64)); ex_mod.append(mod); ex_sym.append(sym)
        EX = np.stack(ex_rows) if ex_rows else np.zeros((0, 0))
        modules = np.stack(self.modules)             # (n_modules, D) — the growing brain
        np.savez(os.path.join(d, "vectors.npz"), modules=modules, EX=EX,
                 ex_mod=np.array(ex_mod, dtype=object), ex_sym=np.array(ex_sym, dtype=object))
        meta = {
            "D": self.D, "module_cap": self.module_cap, "module_counts": self.module_counts,
            "directed": self.directed, "facts": self.facts, "values": self.values,
            "sentences": self.sentences, "key_modules": self.key_modules,
            "learner": {"tau": self.learner.tau, "max_exemplars": self.learner.max_exemplars,
                        "n_asked": self.learner.n_asked, "n_seen": self.learner.n_seen,
                        "fit": {k: list(v) for k, v in self.learner._fit.items()}},
        }
        with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(cls, d: str):
        with open(os.path.join(d, "meta.json"), "r", encoding="utf-8") as f:
            meta = json.load(f)
        self = cls(D=meta["D"], tau=meta["learner"]["tau"], module_cap=meta.get("module_cap"),
                   directed=meta.get("directed", False))
        self.facts = [tuple(t) for t in meta["facts"]]
        self.values = list(meta["values"])
        self.sentences = list(meta.get("sentences", []))
        self.key_modules = {k: list(v) for k, v in meta.get("key_modules", {}).items()}
        z = np.load(os.path.join(d, "vectors.npz"), allow_pickle=True)
        if "modules" in z:                            # growing multi-module store (JEP-296)
            self.modules = [row.astype(np.float64) for row in z["modules"]]
            self.module_counts = list(meta.get("module_counts", [len(self.facts)]))
        else:                                         # back-compat: single-module file (pre-JEP-296)
            self.modules = [z["accum"].astype(np.float64)]
            self.module_counts = [len(self.facts)]
        self.learner.max_exemplars = meta["learner"]["max_exemplars"]
        self.learner.n_asked = meta["learner"]["n_asked"]; self.learner.n_seen = meta["learner"]["n_seen"]
        self.learner._fit = {k: list(v) for k, v in meta["learner"]["fit"].items()}
        EX, mods, syms = z["EX"], z["ex_mod"], z["ex_sym"]
        for i in range(len(mods)):
            self.learner.protos.setdefault((str(mods[i]), str(syms[i])), []).append(EX[i].astype(np.float64))
        return self
