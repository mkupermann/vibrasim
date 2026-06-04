"""
LinearRouter — a tiny trained classifier that routes a query to a label (kind/intent) from a few examples.
Resolves the cross-type/intent routing problem (GEO-86: trained 1.00 vs keyword 0.88; GEO-48): routing is a
linear-probe task on query embeddings (GEO-66). Use it to pick the fact `kind` to scope retrieval to, or the
operator/intent to dispatch. ~8 examples per label suffice. CPU, sentence-transformers + numpy.
"""
from __future__ import annotations
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


class LinearRouter:
    def __init__(self, model="all-MiniLM-L6-v2", _shared=None):
        self.model = _shared or SentenceTransformer(model)
        self.labels = []
        self.W = None

    def fit(self, examples: dict, epochs: int = 500, lr: float = 0.5):
        """examples: {label: [query, ...]}. Trains a multinomial logistic classifier on query embeddings."""
        self.labels = list(examples)
        X, y = [], []
        for i, lab in enumerate(self.labels):
            for q in examples[lab]:
                X.append(q); y.append(i)
        Xe = np.asarray(self.model.encode(X, normalize_embeddings=True))
        y = np.array(y); Y = np.eye(len(self.labels))[y]
        self.W = np.zeros((len(self.labels), Xe.shape[1]))
        for _ in range(epochs):
            Z = Xe @ self.W.T; P = np.exp(Z - Z.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
            self.W -= lr * ((P - Y).T @ Xe) / len(Xe)
        return self

    def route(self, query: str):
        """Return the predicted label for a query."""
        v = self.model.encode([query], normalize_embeddings=True)[0]
        return self.labels[int(np.argmax(self.W @ v))]


if __name__ == "__main__":
    r = LinearRouter().fit({
        "contact": ["who is the plumber", "the dentist", "that lawyer guy"],
        "task": ["when is the tax due", "the sink fix job", "what's due in 2025"],
        "note": ["the budget note", "what I wrote about the trip", "that money cap thing"]})
    for q in ["when's the tax thing", "the pipe fixing person", "the trip plan note"]:
        print(f"  {q!r} -> {r.route(q)}")
