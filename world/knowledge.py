"""EQMOD — substrate-native knowledge / retrieval system (NO LLM, NO transformer).

Goal: a system you can communicate with in writing, that learns from text SOURCES,
builds a knowledge store, answers written questions, and improves online — strictly on
the substrate's own primitives (VSA hypervectors + online readout + cleanup), no LLM,
no transformer, no pretrained embedding, no BPE.

Honest provenance: this is Hyperdimensional/VSA text encoding (Kanerva; Rahimi et al.)
+ classic vector-space IR with IDF weighting (Salton) + an online reservoir/RLS
re-ranker. Established methods, run locally. Not a generative chatbot — it answers by
retrieving and composing the passages it has read.

Design:
- Word-level tokenizer (no BPE). Each word -> a deterministic random +-1 hypervector
  (seeded by a stable hash, so we never store a full embedding matrix).
- A passage -> IDF-weighted analog bundle of its word hypervectors (a random projection
  of the IDF bag-of-words; cosine in HD space ~ cosine in BoW space, Johnson-
  Lindenstrauss). This is the substrate's analog VSA superposition (bundle_analog).
- KnowledgeBase: ingest(text) splits into passages and stores (text, vector). query(q)
  ranks passages by cosine. learn(q, idx) reinforces a query->passage association in an
  online linear re-ranker (RLS), so feedback improves future answers.
"""
from __future__ import annotations

import hashlib
import re
import numpy as np

_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]+")


def tokenize(text: str):
    return _TOKEN_RE.findall(text.lower())


def split_passages(text: str):
    """Split a source into passages (sentence-ish units)."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


class HDSpace:
    """Deterministic word hypervectors, generated on demand (no stored matrix)."""

    def __init__(self, dim: int = 4096):
        self.dim = dim
        self._cache: dict[str, np.ndarray] = {}

    def word_vec(self, word: str) -> np.ndarray:
        v = self._cache.get(word)
        if v is None:
            seed = int.from_bytes(hashlib.blake2b(word.encode("utf-8"), digest_size=8).digest(), "little")
            rng = np.random.default_rng(seed)
            v = rng.choice([-1.0, 1.0], self.dim)
            self._cache[word] = v
        return v


def _trigrams(word: str):
    w = f"#{word}#"
    return [w[i:i + 3] for i in range(len(w) - 2)]


class KnowledgeBase:
    def __init__(self, dim: int = 4096, lam_ctx: float = 0.7, lam_ng: float = 0.5):
        self.hd = HDSpace(dim)
        self.dim = dim
        self.lam_ctx = lam_ctx          # weight of distributional (co-occurrence) semantics
        self.lam_ng = lam_ng            # weight of character n-gram (morphology) channel
        self.passages: list[str] = []
        self.vectors: list[np.ndarray] = []        # normalized passage HD vectors
        self.df: dict[str, int] = {}               # document frequency per word
        self.n_docs = 0
        self._tok_cache: list[list[str]] = []
        self._ctx: dict[str, np.ndarray] = {}      # Random-Indexing context vectors
        self._rep_cache: dict[str, np.ndarray] = {}
        # online re-ranker: maps query HD vector -> a small bias per stored passage
        self._W = None

    # --- IDF -----------------------------------------------------------------
    def _idf(self, word: str) -> float:
        df = self.df.get(word, 0)
        return float(np.log((1.0 + self.n_docs) / (1.0 + df)) + 1.0)

    # --- word representation: index + co-occurrence context + char n-grams ----
    def _ngram_vec(self, word: str) -> np.ndarray:
        acc = np.zeros(self.dim)
        for t in _trigrams(word):
            acc += self.hd.word_vec("§" + t)
        n = np.linalg.norm(acc)
        return acc / n if n > 0 else acc

    def _rep(self, word: str) -> np.ndarray:
        """Word vector = random index (lexical) + distributional context + morphology."""
        v = self._rep_cache.get(word)
        if v is not None:
            return v
        rep = self.hd.word_vec(word).copy()
        ctx = self._ctx.get(word)
        if ctx is not None:
            cn = np.linalg.norm(ctx)
            if cn > 0:
                rep = rep + self.lam_ctx * (ctx / cn) * np.sqrt(self.dim)
        if self.lam_ng > 0:
            rep = rep + self.lam_ng * self._ngram_vec(word) * np.sqrt(self.dim)
        n = np.linalg.norm(rep)
        rep = rep / n if n > 0 else rep
        self._rep_cache[word] = rep
        return rep

    def _encode(self, tokens) -> np.ndarray:
        if not tokens:
            return np.zeros(self.dim)
        acc = np.zeros(self.dim)
        for w in tokens:
            acc += self._idf(w) * self._rep(w)
        n = np.linalg.norm(acc)
        return acc / n if n > 0 else acc

    # --- ingestion -----------------------------------------------------------
    def ingest(self, text: str):
        new = split_passages(text)
        for p in new:
            toks = tokenize(p)
            if not toks:
                continue
            self.n_docs += 1
            for w in set(toks):
                self.df[w] = self.df.get(w, 0) + 1
            # Random Indexing: accumulate co-occurring words' index vectors as context
            for i, w in enumerate(toks):
                if w not in self._ctx:
                    self._ctx[w] = np.zeros(self.dim)
                for j, nb in enumerate(toks):
                    if i != j:
                        self._ctx[w] += self.hd.word_vec(nb)
            self.passages.append(p)
            self._tok_cache.append(toks)
        self._rep_cache.clear()                     # context changed -> rebuild reps
        self.vectors = [self._encode(t) for t in self._tok_cache]
        return len(new)

    # --- query ---------------------------------------------------------------
    def _scores(self, query: str) -> np.ndarray:
        q = self._encode(tokenize(query))
        if not self.vectors:
            return np.zeros(0)
        M = np.asarray(self.vectors)
        base = M @ q
        if self._W is not None:
            base = base + self._W @ q                # online re-ranker contribution
        return base

    def query(self, query: str, k: int = 3):
        s = self._scores(query)
        if s.size == 0:
            return []
        order = np.argsort(-s)[:k]
        return [(int(i), self.passages[i], float(s[i])) for i in order]

    def answer(self, query: str) -> str:
        top = self.query(query, k=1)
        return top[0][1] if top else "(no knowledge yet)"

    # --- online learning from feedback --------------------------------------
    def learn(self, query: str, correct_idx: int, lr: float = 0.5):
        """Reinforce: this query should rank passage `correct_idx` higher. Online,
        local outer-product update on the re-ranker (one passage row)."""
        if self._W is None:
            self._W = np.zeros((len(self.passages), self.dim))
        elif self._W.shape[0] != len(self.passages):
            W2 = np.zeros((len(self.passages), self.dim))
            W2[: self._W.shape[0]] = self._W
            self._W = W2
        q = self._encode(tokenize(query))
        pred = self._scores(query)
        target = np.full(len(self.passages), -0.1)
        target[correct_idx] = 1.0
        err = target - np.tanh(pred)
        self._W += lr * np.outer(err, q)             # local delta update
