"""Active-learning TEACHER loop (per Michael's steer: 'if the substrate is not sure it asks me').

A modality-agnostic prototype learner that grounds SYMBOLS (letters now, words/sounds later) from perceptual
examples, reports its CONFIDENCE, and ASKS a teacher only when UNSURE. The teacher answers correct/incorrect (or
gives the label); later the same store accepts a second modality (audio) bound to the same symbol, so 'hear A' and
'write A' ground the same 'A'. Established (active learning / uncertainty sampling + nearest-prototype), named; no
novelty -- it is the teacher loop the directive asks for.

No transformer, no pretrained model.
"""
import numpy as np


class ActiveLearner:
    def __init__(self, tau: float = 0.10, max_exemplars: int = 40):
        # (modality, symbol) -> list of EXEMPLAR vectors (instance-based / 1-NN). Storing exemplars instead of one
        # running mean makes teacher CORRECTIONS stick: a corrected example matches a near-identical future percept
        # directly, instead of diluting into a blurry class mean (the D-called-B failure). Modalities keyed
        # separately but bound to the SAME symbol, so cross-modal (write 'A' + hear 'A') grounds one symbol.
        self.protos = {}            # (modality, symbol) -> [vectors]
        self.tau = tau              # confidence margin below which the learner is UNSURE and asks the teacher
        self.max_exemplars = max_exemplars   # per-symbol cap (bounds memory; keeps the most recent)
        self.n_asked = 0            # how many times it had to ask the teacher
        self.n_seen = 0
        self._fit = {}              # modality -> running [sum, n] of intra-class distances (how close a CORRECT match is)

    def _proto(self, modality, symbol):
        """Centroid of a symbol's exemplars (derived) — for cross-modal retrieval that wants one vector per symbol."""
        ex = self.protos[(modality, symbol)]
        return np.mean(ex, axis=0)

    def _nearest_in(self, modality, symbol, x):
        """Distance from x to the NEAREST exemplar of (modality, symbol)."""
        ex = self.protos[(modality, symbol)]
        return min(float(np.linalg.norm(x - e)) for e in ex)

    def _fit_dist(self, modality):
        f = self._fit.get(modality)
        return (f[0] / f[1]) if f and f[1] else None   # typical distance of a correct example to its nearest exemplar

    def teach(self, modality: str, symbol: str, x: np.ndarray):
        """The teacher provides the correct symbol for example x (in a modality) -> store it as an exemplar + update
        the running 'how close is a correct match' statistic (the novelty baseline)."""
        x = np.asarray(x, dtype=np.float64)
        key = (modality, symbol)
        if key in self.protos:                          # record the distance to the (current) nearest correct exemplar
            dfit = self._nearest_in(modality, symbol, x)
            f = self._fit.setdefault(modality, [0.0, 0]); f[0] += dfit; f[1] += 1
        ex = self.protos.setdefault(key, [])
        ex.append(x.copy())
        if len(ex) > self.max_exemplars:                # keep the most recent exemplars (bounded memory)
            del ex[0]

    def _ranked(self, modality, x):
        """Return symbols of this modality ranked by distance to x (nearest exemplar): [(symbol, dist), ...]."""
        x = np.asarray(x, dtype=np.float64)
        ds = [(sym, self._nearest_in(mod, sym, x))
              for (mod, sym) in self.protos if mod == modality]
        return sorted(ds, key=lambda t: t[1])

    def guess(self, modality: str, x: np.ndarray):
        """Return (best_symbol, confidence) in [0,1]. Confidence combines a NOVELTY gate (is x close to ANY known
        prototype, vs the typical correct-match distance?) with the MARGIN to the 2nd-nearest. Low if x fits nothing
        well (a new/unseen letter) OR two classes are equidistant."""
        r = self._ranked(modality, x)
        if not r:
            return None, 0.0
        d1 = r[0][1]
        fit = self._fit_dist(modality)
        # NOVELTY: how well x fits its nearest class vs a typical correct match. ->0 if far. NO baseline yet -> 0
        # (ask: the learner has no basis to be confident during bootstrap) until a fit baseline is established.
        novelty = 0.0 if fit is None or fit <= 1e-9 else float(np.clip(2.0 - d1 / fit, 0.0, 1.0))
        if len(r) == 1:
            return r[0][0], novelty                     # only one class known -> confidence is purely 'does it fit?'
        d2 = r[1][1]
        margin = (d2 - d1) / (d2 + d1 + 1e-9)
        return r[0][0], min(novelty, margin)            # unsure if EITHER it fits poorly OR the margin is small

    def observe(self, modality: str, x: np.ndarray, teacher):
        """The core loop: guess; if UNSURE (or unknown), ASK the teacher and learn the answer. Returns
        (predicted_symbol, asked: bool, correct: bool|None). `teacher(modality, x)` returns the true symbol."""
        self.n_seen += 1
        sym, conf = self.guess(modality, x)
        if sym is None or conf < self.tau:                 # UNSURE -> ask the teacher
            self.n_asked += 1
            truth = teacher(modality, x)
            correct = (sym == truth)
            self.teach(modality, truth, x)                 # learn from the teacher's answer
            return truth, True, correct
        return sym, False, None                            # confident -> answer without bothering the teacher

    def confirm(self, modality: str, x: np.ndarray, guessed: str, is_correct: bool, true_symbol: str = None):
        """GUI feedback path: the teacher clicked Correct / Not-correct on `guessed`. On 'Not correct' the GUI may
        supply the true_symbol (or, later, a sentence we parse). Learn accordingly."""
        if is_correct:
            self.teach(modality, guessed, x)
        elif true_symbol is not None:
            self.teach(modality, true_symbol, x)
