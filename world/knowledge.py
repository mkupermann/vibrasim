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


class KnowledgeBase:
    def __init__(self, dim: int = 4096):
        self.hd = HDSpace(dim)
        self.dim = dim
        self.passages: list[str] = []
        self.vectors: list[np.ndarray] = []        # normalized passage HD vectors
        self.df: dict[str, int] = {}               # document frequency per word
        self.n_docs = 0
        self._tok_cache: list[list[str]] = []
        # online re-ranker (RLS): maps query HD vector -> a small bias per stored passage
        self._W = None                              # lazily sized

    # --- IDF -----------------------------------------------------------------
    def _idf(self, word: str) -> float:
        df = self.df.get(word, 0)
        return float(np.log((1.0 + self.n_docs) / (1.0 + df)) + 1.0)

    def _encode(self, tokens) -> np.ndarray:
        if not tokens:
            return np.zeros(self.dim)
        acc = np.zeros(self.dim)
        for w in tokens:
            acc += self._idf(w) * self.hd.word_vec(w)   # IDF-weighted analog bundle
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
            self.passages.append(p)
            self._tok_cache.append(toks)
        # (re)encode all passages so IDF reflects the full corpus
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
