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
import numpy as np

from world.vsa import bind, unbind, sim, CleanupMemory
from world.active_learner import ActiveLearner

DEFAULT_D = 4096


def atom_vector(name: str, D: int) -> np.ndarray:
    """A deterministic, cross-process-stable bipolar hypervector for a symbol name (hashlib-seeded, NOT builtin
    hash() which is per-process salted). Same name -> same vector everywhere; different names -> near-orthogonal."""
    seed = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
    return np.random.default_rng(seed).choice([-1.0, 1.0], D)


class SubstrateMemory:
    def __init__(self, D: int = DEFAULT_D, tau: float = 0.12, module_cap: int = None):
        self.D = D
        # GROWING store (JEP-296): a STACK of bundle modules. When the current module saturates (~0.8*D/32 facts)
        # a new empty module is added (neurogenesis), so total capacity is unbounded (linear in #modules).
        self.module_cap = module_cap or max(1, int(0.8 * D / 32))
        self.modules = [np.zeros(D, dtype=np.float64)]   # running SUM per module; mem_m = sign(module)
        self.module_counts = [0]
        self.facts = []                              # list of (entity, role, value) for bookkeeping/growth
        self.values = []                             # value vocabulary (the cleanup dictionary)
        self.learner = ActiveLearner(tau=tau)        # perceptual memory (taught exemplars)

    # ---- atom / vector helpers ----
    def _vec(self, name):
        return atom_vector(name, self.D)

    @property
    def accum(self):
        return self.modules[0]                       # back-compat alias (single-module callers)

    def _mem(self, m):
        s = np.sign(self.modules[m]); s[s == 0] = 1.0
        return s

    def _cleanup(self):
        cm = CleanupMemory()
        for v in self.values:
            cm.add(v, self._vec(v))
        return cm

    # ---- relational facts ----
    def add_fact(self, entity: str, role: str, value: str):
        """Store 'entity's role IS value' as bind(entity*role, value) superposed into the current module. When that
        module fills (module_cap), auto-add a fresh module so growth is unbounded (JEP-296)."""
        if self.module_counts[-1] >= self.module_cap:
            self.modules.append(np.zeros(self.D, dtype=np.float64))   # neurogenesis: a new module
            self.module_counts.append(0)
        bound = bind(bind(self._vec(entity), self._vec(role)), self._vec(value))
        self.modules[-1] = self.modules[-1] + bound
        self.module_counts[-1] += 1
        self.facts.append((entity, role, value))
        if value not in self.values:
            self.values.append(value)

    def query(self, entity: str, role: str):
        """Recover the value bound to (entity, role): (value_name, similarity). Searches ALL modules and returns the
        single best cleanup match (the module that actually holds this fact wins)."""
        key = bind(self._vec(entity), self._vec(role))
        cm = self._cleanup()
        best_name, best_sim = None, -1e9
        for m in range(len(self.modules)):
            name, s = cm.cleanup(unbind(self._mem(m), key))
            if s > best_sim:
                best_name, best_sim = name, s
        return best_name, best_sim

    # ---- perceptual facts (taught letters/sounds) ----
    def teach_percept(self, modality: str, symbol: str, x):
        self.learner.teach(modality, symbol, np.asarray(x, dtype=np.float64))

    def recognize(self, modality: str, x):
        return self.learner.guess(modality, np.asarray(x, dtype=np.float64))

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
            "facts": self.facts, "values": self.values,
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
        self = cls(D=meta["D"], tau=meta["learner"]["tau"], module_cap=meta.get("module_cap"))
        self.facts = [tuple(t) for t in meta["facts"]]
        self.values = list(meta["values"])
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
