"""valence_reservoir — energy-driven non-linear learner (JEP-430).

Couples Michael's affective VALENCE/energy signal to a RESERVOIR (random nonlinear features) + an online linear readout,
so the system learns to predict the valence of NEW experiences from a non-linear rule WITHOUT enumerating conjunctions
and without labels beyond the scalar energy. Established methods (random features / Extreme Learning Machine —
Rahimi-Recht 2007, Huang 2006; recursive least squares), assembled — NO transformer, NO pretrained model. Ties to the
EQMOD-2 reservoir thread.
"""
import numpy as np


class ValenceReservoirLearner:
    def __init__(self, n_inputs, n_features=300, seed=0, ridge=1.0):
        rng = np.random.default_rng(seed)
        self.R = rng.standard_normal((n_inputs, n_features))      # fixed random projection
        self.b = rng.standard_normal(n_features)
        self.M = n_features
        # recursive-least-squares readout state (online, closed form, no backprop)
        self.P = np.eye(n_features + 1) / ridge
        self.w = np.zeros(n_features + 1)

    def _phi(self, x):
        return np.append(np.tanh(np.asarray(x, float) @ self.R + self.b), 1.0)   # +bias

    def experience(self, x, valence):
        """One experience: an input vector x carrying environmental energy `valence` (+/-). Online RLS update."""
        phi = self._phi(x)
        Pphi = self.P @ phi
        g = Pphi / (1.0 + phi @ Pphi)
        self.w = self.w + g * (float(valence) - phi @ self.w)
        self.P = self.P - np.outer(g, Pphi)

    def feel(self, x):
        """Predict the valence/energy of a (possibly new) input: +1 bright / -1 dark."""
        return float(self._phi(x) @ self.w)
