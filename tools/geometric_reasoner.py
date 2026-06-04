"""
GeometricReasoner — a usable, generator-free neuro-symbolic reasoning layer over an LLM embedding space.

Packages the validated EQMOD-3 geometric programme (GEO-1..52) into one runnable module for the PC (CPU).
It does NOT generate text and does NOT replace an LLM — it is a grounded reasoning layer ON one. Methods:

  * retrieve / ask     — grounded RETRIEVAL + ABSTENTION (GEO-15/23), optional cross-encoder re-rank (GEO-40b)
  * chain              — multi-hop iterative retrieval (GEO-16/17, robust to distractors/paraphrase)
  * count_where        — symbolic AGGREGATION over geometric resolutions (GEO-18)
  * resolve_entity     — typo-robust character-trigram entity resolution (GEO-44, noisy 0.53->1.00)
  * check_contradiction— same-subject conflict detection (GEO-41/52, 1.00)
  * calibrate_abstention— set the abstention threshold from a labelled dev split (GEO-23/32)

Companion modules: grounded_qa.py (adds a small LLM generator), unified_reasoner.py (auto-dispatch agent).
Principle: geometry for SEMANTICS (relevance/entities/relations), symbols for STRUCTURE (count/compare/join/
time-filter/contradiction). Honest scope (see docs/GEOMETRIC_ANSWER.md): sound + integrated on PC-scale
(hundreds of facts, 2-3 hops); NOT open-domain NLU; named-entity retrieval is partly lexical (GEO-25); every
primitive is an established method named as such.

Requires: sentence-transformers, numpy (+ transformers for re-rank/generation). Default model
all-MiniLM-L6-v2 (use all-mpnet-base-v2 for quality, paraphrase-multilingual-MiniLM-L12-v2 for cross-lingual).
"""
from __future__ import annotations
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:  # pragma: no cover
    SentenceTransformer = None


import re as _re_sanitize

_INJ_WORDS = ["ignore", "disregard", "forget", "system:", "new instruction", "must now", "only say",
              "regardless of input", "reply only", "respond with", "output:", "always answer", "###",
              "assistant must"]


def sanitize_text(text):
    """Strip instruction-like spans from untrusted content before it enters an LLM prompt (GEO-98:
    neutralizes prompt injection 0.17->0.00 while preserving legitimate facts). Use when ingesting untrusted
    store content. NOT exhaustive (matches known patterns) - combine with extractive answers for untrusted
    sources; a trusted private KB needs no sanitization."""
    parts = _re_sanitize.split(r"(?<=[.!?])\s+", text)
    kept = [p for p in parts if not any(w in p.lower() for w in _INJ_WORDS)]
    return " ".join(kept).strip() or "[redacted]"


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

    def add_document(self, text: str, source: str = None):
        """Ingest UNSTRUCTURED prose: sentence-split and add each sentence as a fact (GEO-56). Use with
        rerank_k>0 for best accuracy on prose (GEO-56b: 0.67 -> 0.83). Returns the number of sentences added."""
        import re as _re
        sents = [s.strip() for s in _re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        for s in sents:
            self.add_fact(s, source=source)
        return len(sents)

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

    # ---- core: grounded retrieval (GEO-15, GEO-23) + optional re-rank (GEO-40b) + kind scope (GEO-83)
    def retrieve(self, query: str, kind=None):
        """Return (best_index, similarity) or (None, sim) if below the abstention threshold.
        If rerank_k>0, the top-k bi-encoder candidates are re-scored by a cross-encoder (GEO-40b:
        recovers multi-hop accuracy at scale, 2-hop 0.87->1.00 at 400 facts). Abstention still uses the
        bi-encoder similarity (calibrated tau). Pass `kind` to SCOPE retrieval to facts of that meta kind —
        avoids cross-type confusion (GEO-83: "who can fix plumbing" matching a 'fix' task over the plumber
        contact)."""
        if not self.fact_texts:
            return None, 0.0
        q = self._embed([query])[0]
        sims = self.F @ q
        if kind is not None:                    # mask out facts of other kinds
            mask = np.array([m.get("kind") == kind for m in self.fact_meta])
            if not mask.any():
                return None, 0.0
            sims = np.where(mask, sims, -np.inf)
        j = int(np.argmax(sims))
        if sims[j] < self.abstain_tau:
            return None, float(sims[j])         # ABSTAIN — grounded, no confabulation
        if self.rerank_k and len(self.fact_texts) > 1:
            if self._ce is None:
                from sentence_transformers import CrossEncoder
                self._ce = CrossEncoder(self._rerank_model)
            order = np.argsort(-sims)
            topk = [int(t) for t in order[:self.rerank_k] if np.isfinite(sims[t])]
            if topk:
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

    # ---- typo-robust entity resolution (GEO-44) --------------------------
    def resolve_entity(self, name: str, candidates=None):
        """Fuzzy-match `name` to the closest stored entity (by character-trigram Jaccard) — robust to typos
        and near-duplicate names where pure embedding retrieval fails (GEO-43 0.53 -> GEO-44 1.00). Returns
        the best-matching candidate string. Use this for entity IDENTITY; embeddings for relevance."""
        if candidates is None:
            candidates = sorted({m.get("subject") for m in self.fact_meta if m.get("subject")})
        if not candidates:
            return None
        def tri(s):
            s = "  " + s.lower().replace(" ", "") + "  "
            return set(s[i:i + 3] for i in range(len(s) - 2))
        def sim(a, b):
            A, B = tri(a), tri(b)
            return len(A & B) / len(A | B) if A | B else 0.0
        return max(candidates, key=lambda c: sim(name, c))

    # ---- query-time conflict surfacing (GEO-62) --------------------------
    def values_for(self, subject, field="object", kind=None):
        """Return (status, values) for an entity's field: status is 'CONFLICT' if the store holds >1 distinct
        value (a data inconsistency), else 'OK'. Surfaces conflicts at query time instead of silently picking
        one (GEO-62). Purely symbolic over same-subject facts."""
        vals = {m.get(field) for m in self.fact_meta
                if m.get("subject") == subject and (kind is None or m.get("kind") == kind) and m.get(field) is not None}
        return ("CONFLICT" if len(vals) > 1 else "OK"), vals

    # ---- contradiction detection (GEO-41, hardened GEO-52) ---------------
    def check_contradiction(self, subject: str, object: str, kind=None, text: str = None):
        """Return the index of a stored fact that contradicts (same subject, different object — a functional
        relation), else None. Over a STRUCTURED store this is purely SYMBOLIC (scan same-subject facts);
        the same-subject pre-filter is robust to token collisions that fooled the embedding-nearest version
        (GEO-52: 0.94 -> 1.00). Pass `kind` to restrict to one fact type (e.g. 'person'). `text` is accepted
        for backward compatibility and ignored."""
        for j, m in enumerate(self.fact_meta):
            if m.get("subject") == subject and (kind is None or m.get("kind") == kind)                     and m.get("object") not in (None, object):
                return j
        return None


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
