"""EQMOD-2 — energy-based, predictive, self-supervised geometric memory.

A clean re-design after the spontaneous-substrate memory programme hit its
structural ceiling (docs/NEW_DIRECTION.md). NOT a transformer, no backprop, no
pretrained model. The pieces:

- **Geometric / energy-based.** N nodes sit at fixed 3D positions, grouped into
  modules. A symmetric weight matrix W (gated by an engineered sparse, modular
  connectivity mask M) defines a Hopfield-style energy
  E(s) = -1/2 sᵀ(W∘M)s - bᵀs. Memories are ATTRACTOR VALLEYS; recall is relaxation
  to the nearest minimum, so pattern completion falls out for free.

- **Self-supervised.** No labels. Training presents a pattern with part masked
  (a "cue"), relaxes the free units, and nudges W so the full pattern becomes an
  attractor. The only signal is the substrate's own completion error.

- **Local, non-transformer learning.** Contrastive Hebbian / equilibrium-prop
  rule: ΔW ∝ ⟨s sᵀ⟩_clamped − ⟨s sᵀ⟩_free, applied only on existing connections.
  Purely local, the established backprop alternative.
"""
from __future__ import annotations

import numpy as np


class EnergyNet:
    def __init__(self, n_per_module: int = 40, n_modules: int = 2,
                 p_in: float = 0.6, p_cross: float = 0.05,
                 beta: float = 1.5, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.N = n_per_module * n_modules
        self.beta = beta

        # 3D positions: modules as spatially separated clusters (the geometry).
        pos, module = [], []
        for m in range(n_modules):
            cx = (m - (n_modules - 1) / 2.0) * 7.0
            center = np.array([cx, 0.0, 0.0])
            for _ in range(n_per_module):
                pos.append(center + rng.normal(0.0, 1.8, 3))
                module.append(m)
        self.pos = np.asarray(pos, dtype=np.float64)
        self.module = np.asarray(module, dtype=np.int64)

        # Engineered modular connectivity mask: dense within a module, sparse
        # across (bounds percolation by construction — the lesson from BET-102).
        M = np.zeros((self.N, self.N), dtype=np.float64)
        for i in range(self.N):
            for j in range(i + 1, self.N):
                p = p_in if self.module[i] == self.module[j] else p_cross
                if rng.random() < p:
                    M[i, j] = M[j, i] = 1.0
        self.M = M

        self.W = np.zeros((self.N, self.N), dtype=np.float64)   # symmetric (attractors)
        self.T = np.zeros((self.N, self.N), dtype=np.float64)   # asymmetric (transitions)
        self.b = np.zeros(self.N, dtype=np.float64)
        self.state = rng.choice([-1.0, 1.0], self.N)
        self._rng = rng

    # --- dynamics -----------------------------------------------------------
    def field(self, s):
        return (self.W * self.M) @ s + self.b

    def relax(self, clamp_idx=None, clamp_val=None, steps: int = 25, record=None):
        """Mean-field relaxation to an energy minimum. Clamped units are held;
        free units settle. If `record` is a list, append a state copy each step
        (for the live visualization of the relaxation trajectory)."""
        s = self.state.copy()
        if clamp_idx is not None:
            s[clamp_idx] = clamp_val
        for _ in range(steps):
            s = np.tanh(self.beta * self.field(s))
            if clamp_idx is not None:
                s[clamp_idx] = clamp_val
            if record is not None:
                record.append(s.copy())
        self.state = s
        return s

    def energy(self, s=None):
        s = self.state if s is None else s
        return float(-0.5 * s @ (self.W * self.M) @ s - self.b @ s)

    # --- self-supervised learning ------------------------------------------
    def train_epoch(self, patterns, cue_frac: float = 0.5, lr: float = 0.02,
                    relax_steps: int = 20):
        """One self-supervised pass: for each pattern, clamp a random cue subset,
        relax the rest (free phase = the substrate's own prediction), then nudge
        W toward the clamped full pattern. Contrastive Hebbian — local, label-free."""
        for p in patterns:
            cue = self._rng.random(self.N) < cue_frac
            cue_idx = np.where(cue)[0]
            # free / prediction phase
            self.state = self._rng.choice([-1.0, 1.0], self.N)
            s_free = self.relax(cue_idx, p[cue_idx], relax_steps).copy()
            # clamped / data phase = the full pattern is the target equilibrium
            s_clamp = p.astype(np.float64)
            # local contrastive update, restricted to existing connections
            dW = (np.outer(s_clamp, s_clamp) - np.outer(s_free, s_free)) * self.M
            self.W += lr * dW
            np.fill_diagonal(self.W, 0.0)
            self.W = 0.5 * (self.W + self.W.T)

    # --- sequences / prediction (predictive world-model step) ---------------
    def train_sequence(self, seq, lr_T: float = 0.06, lr_W: float = 0.02,
                       assoc_epochs: int = 80):
        """Learn a temporal sequence: each pattern becomes a clean-up ATTRACTOR
        (symmetric W, via the self-supervised rule) AND directed transitions are
        stored in the asymmetric T (Hebbian: next outer current). Self-supervised:
        the only target is the sequence predicting its own next step."""
        for _ in range(assoc_epochs):
            self.train_epoch(seq, cue_frac=0.5, lr=lr_W, relax_steps=12)
        for t in range(len(seq) - 1):
            a = seq[t].astype(np.float64); b = seq[t + 1].astype(np.float64)
            self.T += lr_T * np.outer(b, a) * self.M
        np.fill_diagonal(self.T, 0.0)

    def predict_step(self, s, cleanup_steps: int = 12):
        """Predict the next state via the transition matrix, then clean it up to
        the nearest stored attractor (energy relaxation)."""
        nxt = np.tanh(self.beta * ((self.T * self.M) @ s))
        self.state = nxt
        self.relax(None, None, cleanup_steps)
        return self.state.copy()

    def recall_sequence(self, start, length: int, cleanup_steps: int = 12):
        s = np.sign(np.asarray(start, dtype=np.float64))
        out = [s.copy()]
        for _ in range(length - 1):
            s = self.predict_step(s, cleanup_steps)
            out.append(s.copy())
        return out

    # --- evaluation ---------------------------------------------------------
    def complete(self, pattern, cue_frac: float = 0.5, relax_steps: int = 30,
                 record=None):
        """Present a partial cue of `pattern`, relax, return (recalled_state,
        accuracy_on_masked_units, cue_idx)."""
        cue = self._rng.random(self.N) < cue_frac
        cue_idx = np.where(cue)[0]
        masked = np.where(~cue)[0]
        self.state = self._rng.choice([-1.0, 1.0], self.N)
        s = self.relax(cue_idx, pattern[cue_idx], relax_steps, record=record)
        if len(masked) == 0:
            acc = 1.0
        else:
            acc = float(np.mean(np.sign(s[masked]) == np.sign(pattern[masked])))
        return s, acc, cue_idx

    def recall_accuracy(self, patterns, cue_frac: float = 0.5, trials: int = 20,
                        relax_steps: int = 30):
        accs = []
        for _ in range(trials):
            p = patterns[self._rng.integers(len(patterns))]
            _, a, _ = self.complete(p, cue_frac, relax_steps)
            accs.append(a)
        return float(np.mean(accs))


def make_patterns(net: EnergyNet, n_patterns: int = 5, seed: int = 7):
    """Random ±1 target patterns over the nodes (clean completion metric)."""
    rng = np.random.default_rng(seed)
    return [rng.choice([-1.0, 1.0], net.N) for _ in range(n_patterns)]


class SequencePredictor:
    """Order-2, least-squares (projection) sequence memory — the mechanism that
    breaks the sequence-prediction wall (BET-121).

    Two ideas, both non-transformer:
    1. **Order-2 context.** The next state is predicted from the PAIR
       [state(t), state(t-1)], so a repeated token in different contexts
       ("L after E" vs "L after L") predicts differently — fixes HELLO -> HELLO.
    2. **Least-squares (projection) learning.** The transition operator T2 is the
       ridge least-squares fit of all (context -> next) pairs, not a Hebbian
       outer-product sum. This stores many overlapping sequences with essentially
       zero cross-talk (up to ~2·dim transitions), where Hebbian interferes.

    Prediction is exact, so no attractor clean-up is needed (clean-up actually
    corrupts it). Purely linear algebra + a sign nonlinearity; no attention, no
    backprop, no transformer.
    """
    def __init__(self, dim: int, order: int = 2, lam: float = 0.05):
        self.dim = dim
        self.order = order              # how many past states form the context
        self.lam = lam
        self.X, self.Y = [], []
        self.START = np.zeros(dim)
        self.T = None

    def _context(self, hist):
        """Concatenate the last `order` states (START-padded) into one vector."""
        h = list(hist)[-self.order:]
        while len(h) < self.order:
            h = [self.START] + h
        return np.concatenate(h[::-1])   # [most-recent, ..., oldest]

    def add_sequence(self, seq):
        for t in range(len(seq) - 1):
            self.X.append(self._context(seq[:t + 1]))
            self.Y.append(seq[t + 1])

    def fit(self):
        X = np.asarray(self.X, dtype=np.float64)
        Y = np.asarray(self.Y, dtype=np.float64)
        A = X.T @ X + self.lam * np.eye(X.shape[1])
        self.T = np.linalg.solve(A, X.T @ Y).T        # (dim, order*dim)
        return self

    def predict(self, hist):
        return np.sign(self.T @ self._context([np.sign(h) for h in hist]))

    def recall(self, start, length):
        hist = [np.sign(np.asarray(start, dtype=np.float64))]
        out = [hist[0].copy()]
        for _ in range(length - 1):
            nxt = self.predict(hist)
            hist.append(nxt)
            out.append(nxt.copy())
        return out
