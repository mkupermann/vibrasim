"""EQMOD-2 — substrate reservoir: emergent generalization + online learning.

The substrate's OWN random modular connectivity + nonlinear activation is a random
nonlinear feature map phi(x) = tanh(R x). A LINEAR readout on phi generalizes to
unseen inputs (function approximation, not memorization) and learns ONLINE via
recursive least squares (RLS) — one example at a time, as in conversation.
No transformer, no backprop, no pretraining: the features come from the substrate;
only a linear readout is fit, and that incrementally. Generalization emerges from
the substrate's own nonlinear projection — not from hand-designed structure.
"""
from __future__ import annotations
import numpy as np


class SubstrateReservoir:
    def __init__(self, in_dim, out_dim, D=800, spectral=1.5, seed=0, ridge=1e-2):
        rng = np.random.default_rng(seed)
        # random projection = the substrate's fixed modular connectivity
        self.R = rng.normal(0, spectral / np.sqrt(in_dim), (D, in_dim))
        self.bias = rng.normal(0, 0.3, D)
        self.D, self.out_dim = D, out_dim
        self.Wout = np.zeros((out_dim, D))
        self.P = np.eye(D) / ridge          # RLS inverse-covariance
    def features(self, x):
        return np.tanh(self.R @ np.asarray(x, float) + self.bias)   # nonlinear, ±1-ish
    def predict(self, x):
        return self.Wout @ self.features(x)
    def learn_online(self, x, y):
        """One RLS step — learn from a single (x,y) pair, as in live conversation."""
        phi = self.features(x); y = np.asarray(y, float)
        Pp = self.P @ phi
        g = Pp / (1.0 + phi @ Pp)           # Kalman gain
        err = y - self.Wout @ phi
        self.Wout += np.outer(err, g)
        self.P -= np.outer(g, Pp)
        return float(np.mean(err**2))
