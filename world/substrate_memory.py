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
    def __init__(self, D: int = DEFAULT_D, tau: float = 0.12):
        self.D = D
        self.accum = np.zeros(D, dtype=np.float64)   # running SUM of bound fact-vectors; mem = sign(accum)
        self.facts = []                              # list of (entity, role, value) for bookkeeping/growth
        self.values = []                             # value vocabulary (the cleanup dictionary)
        self.learner = ActiveLearner(tau=tau)        # perceptual memory (taught exemplars)

    # ---- atom / vector helpers ----
    def _vec(self, name):
        return atom_vector(name, self.D)

    @property
    def mem(self):
        m = np.sign(self.accum); m[m == 0] = 1.0     # the superposed memory vector
        return m

    def _cleanup(self):
        cm = CleanupMemory()
        for v in self.values:
            cm.add(v, self._vec(v))
        return cm

    # ---- relational facts ----
    def add_fact(self, entity: str, role: str, value: str):
        """Store 'entity's role IS value' by superposing bind(entity*role, value) into the bundle. Growth =
        call again; old facts stay (until bundle capacity K*~D/32 is reached -- then widen D or add a module)."""
        key = bind(self._vec(entity), self._vec(role))
        self.accum = self.accum + bind(key, self._vec(value))
        self.facts.append((entity, role, value))
        if value not in self.values:
            self.values.append(value)

    def query(self, entity: str, role: str):
        """Recover the value bound to (entity, role): (value_name, similarity)."""
        key = bind(self._vec(entity), self._vec(role))
        return self._cleanup().cleanup(unbind(self.mem, key))

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
        np.savez(os.path.join(d, "vectors.npz"), accum=self.accum, EX=EX,
                 ex_mod=np.array(ex_mod, dtype=object), ex_sym=np.array(ex_sym, dtype=object))
        meta = {
            "D": self.D, "facts": self.facts, "values": self.values,
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
        self = cls(D=meta["D"], tau=meta["learner"]["tau"])
        self.facts = [tuple(t) for t in meta["facts"]]
        self.values = list(meta["values"])
        z = np.load(os.path.join(d, "vectors.npz"), allow_pickle=True)
        self.accum = z["accum"].astype(np.float64)
        self.learner.max_exemplars = meta["learner"]["max_exemplars"]
        self.learner.n_asked = meta["learner"]["n_asked"]; self.learner.n_seen = meta["learner"]["n_seen"]
        self.learner._fit = {k: list(v) for k, v in meta["learner"]["fit"].items()}
        EX, mods, syms = z["EX"], z["ex_mod"], z["ex_sym"]
        for i in range(len(mods)):
            self.learner.protos.setdefault((str(mods[i]), str(syms[i])), []).append(EX[i].astype(np.float64))
        return self
