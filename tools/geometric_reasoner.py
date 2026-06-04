"""
GeometricReasoner — a usable, generator-free neuro-symbolic reasoning layer over an LLM embedding space.

Packages the validated EQMOD-3 geometric programme (GEO-1..23) into one runnable module for the PC (CPU).
It does NOT generate text and does NOT replace an LLM — it is a grounded reasoning layer ON one:

  * geometric RETRIEVAL with grounded ABSTENTION  (GEO-15, GEO-23 — knows what it doesn't know)
  * multi-hop CHAINING by iterative retrieval       (GEO-16, GEO-17 — robust to distractors/paraphrase)
  * symbolic AGGREGATION over geometric resolutions  (GEO-18 — count/filter, which geometry alone can't do)

Honest scope (see docs/GEOMETRIC_ANSWER.md): sound + integrated on PC-scale (hundreds of facts, 2-3 hops);
NOT open-domain NLU; negation/comparison/counting require the symbolic layer; every primitive is an
established method (sentence-transformers retrieval + a similarity threshold + symbolic post-processing).

Requires: sentence-transformers, numpy. Model: all-MiniLM-L6-v2 (downloads once, then CPU).
"""
from __future__ import annotations
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:  # pragma: no cover
    SentenceTransformer = None


class GeometricReasoner:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", abstain_tau: float = 0.45,
                 rerank_k: int = 0, rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if SentenceTransformer is None:
            raise RuntimeError("pip install sentence-transformers")
        self._rerank_model = rerank_model
        self.model = SentenceTransformer(model_name)
        self.abstain_tau = abstain_tau          # similarity floor below which we say "unknown" (GEO-23)
        self.fact_texts: list[str] = []
        self.fact_meta: list[dict] = []          # arbitrary structured payload per fact (the symbolic side)
        self._F = None                           # cached embeddings
        self.rerank_k = rerank_k                 # if >0, re-rank top-k with a cross-encoder (GEO-40b)
        self._ce = None                          # lazy-loaded cross-encoder

    # ---- build the store -------------------------------------------------
    def add_fact(self, text: str, **meta):
        """Add one fact sentence plus an optional structured payload (subject/relation/object/...)."""
        self.fact_texts.append(text)
        self.fact_meta.append(meta)
        self._F = None

    def _embed(self, texts):
        return np.asarray(self.model.encode(texts, normalize_embeddings=True))

    @property
    def F(self):
        if self._F is None:
            self._F = self._embed(self.fact_texts) if self.fact_texts else np.zeros((0, 384))
        return self._F

    # ---- calibrate the abstention threshold (GEO-23, GEO-32) -------------
    def calibrate_abstention(self, answerable_qs, unanswerable_qs, margin: float = 0.5):
        """Set abstain_tau from labelled dev questions (GEO-23). A guessed constant is unreliable
        (GEO-32 caught only 2/3 out-of-KB); calibrated on a dev split it reaches ~1.0. tau = the
        margin-weighted midpoint between answerable and unanswerable max-similarities."""
        def maxsim(q):
            return float(np.max(self.F @ self._embed([q])[0])) if self.fact_texts else 0.0
        a = np.array([maxsim(q) for q in answerable_qs])
        u = np.array([maxsim(q) for q in unanswerable_qs])
        # weighted toward the unanswerable side by `margin` to favour precision (fewer false answers)
        self.abstain_tau = float(margin * a.mean() + (1 - margin) * u.mean())
        return self.abstain_tau

    # ---- core: grounded retrieval (GEO-15, GEO-23) + optional re-rank (GEO-40b)
    def retrieve(self, query: str):
        """Return (best_index, similarity) or (None, sim) if below the abstention threshold.
        If rerank_k>0, the top-k bi-encoder candidates are re-scored by a cross-encoder (GEO-40b:
        recovers multi-hop accuracy at scale, 2-hop 0.87->1.00 at 400 facts). Abstention still uses the
        bi-encoder similarity (calibrated tau)."""
        if not self.fact_texts:
            return None, 0.0
        q = self._embed([query])[0]
        sims = self.F @ q
        j = int(np.argmax(sims))
        if sims[j] < self.abstain_tau:
            return None, float(sims[j])         # ABSTAIN — grounded, no confabulation
        if self.rerank_k and len(self.fact_texts) > 1:
            if self._ce is None:
                from sentence_transformers import CrossEncoder
                self._ce = CrossEncoder(self._rerank_model)
            topk = np.argsort(-sims)[:self.rerank_k]
            ce_scores = self._ce.predict([(query, self.fact_texts[t]) for t in topk])
            j = int(topk[int(np.argmax(ce_scores))])
        return j, float(sims[j])

    def ask(self, query: str):
        """Answer a single-fact question, or 'I don't know' when ungrounded."""
        j, sim = self.retrieve(query)
        if j is None:
            return {"answer": None, "text": "I don't know.", "sim": sim, "grounded": False}
        return {"answer": self.fact_meta[j] or self.fact_texts[j], "text": self.fact_texts[j],
                "sim": sim, "grounded": True}

    # ---- multi-hop chaining (GEO-16, GEO-17) -----------------------------
    def chain(self, steps: list[str]):
        """Iterative retrieval: each step is a query template with {bridge} from the previous answer.

        steps[0] is a literal query; later steps use '{bridge}' filled by a chosen meta-field of the prior
        hit. Returns the list of per-hop hits (meta dicts); None if any hop abstains.
        """
        hits = []
        bridge = None
        for i, tmpl in enumerate(steps):
            q = tmpl.format(bridge=bridge) if bridge is not None else tmpl
            j, sim = self.retrieve(q)
            if j is None:
                return None
            meta = self.fact_meta[j] or {}
            hits.append(meta)
            # bridge = the 'object' field by convention, else the whole fact text
            bridge = meta.get("object", self.fact_texts[j])
        return hits

    # ---- symbolic aggregation (GEO-18) -----------------------------------
    def count_where(self, predicate):
        """Count facts whose meta satisfies a predicate — the symbolic layer geometry can't do alone."""
        return sum(1 for meta in self.fact_meta if predicate(meta))


# ---- self-test / demo (mirrors the validated rungs) ----------------------
def _demo():
    print("=== GeometricReasoner self-test ===", flush=True)
    r = GeometricReasoner()
    chains = [("Alice", "Acme", "Boston"), ("Bob", "Globex", "Boston"), ("Carol", "Initech", "Austin")]
    for p, c, city in chains:
        r.add_fact(f"{p} works at {c}.", subject=p, relation="works_at", object=c)
        r.add_fact(f"{c} is in {city}.", subject=c, relation="located_in", object=city)

    # 1) grounded retrieval + abstention (GEO-15/23)
    a = r.ask("Where does Alice work?")
    print(f"  ask grounded     : {a['text']!r} sim={a['sim']:.2f}", flush=True)
    u = r.ask("What is the capital of Mars?")
    print(f"  ask ungrounded   : {u['text']!r} sim={u['sim']:.2f} (correctly abstains: {not u['grounded']})", flush=True)

    # 2) multi-hop chain (GEO-16): Alice -> company -> city
    hits = r.chain(["What company does Alice work at?", "What city is {bridge} in?"])
    city = hits[-1]["object"] if hits else None
    print(f"  2-hop chain Alice-> city = {city!r} (expect 'Boston')", flush=True)

    # 3) symbolic aggregation (GEO-18): how many people work in Boston?
    #    resolve each person->city via chain, then count
    people = [m["subject"] for m in r.fact_meta if m.get("relation") == "works_at"]
    in_boston = 0
    for p in people:
        h = r.chain([f"What company does {p} work at?", "What city is {bridge} in?"])
        if h and h[-1].get("object") == "Boston":
            in_boston += 1
    print(f"  symbolic count in Boston = {in_boston} (expect 2)", flush=True)

    ok = (a["grounded"] and not u["grounded"] and city == "Boston" and in_boston == 2)
    print(f"\n  SELF-TEST: {'PASS' if ok else 'FAIL'}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    _demo()
