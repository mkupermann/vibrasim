"""
DocumentLearner — give it a LINK, file, or raw text and it autonomously ingests the content (chunks + embeds
into a queryable grounded store) and OPTIONALLY adapts the embedder to the document via SELF-SUPERVISED
learning (SimCSE-style contrastive on the document's own sentences — no labels). Then ask/summarize the doc.

Honest scope (EQMOD-3, see docs/GEOMETRIC_ANSWER.md): "learning the content" here means (1) INGESTION — the
content becomes queryable/answerable/summarizable via grounded retrieval (the practical win, immediate); and
(2) SELF-SUPERVISED ADAPTATION — contrastive fine-tuning on the document's sentences tunes the embedding space
to the document's vocabulary/domain (modest benefit, GEO-94/101). It is NOT human-like understanding: the
system does grounded lookup + symbolic computation, not inference (GEO-75). No hallucinated facts (grounded).

Deps: sentence-transformers, numpy, requests (URL). PDF needs `pip install pypdf`. Self-supervised adaptation
needs transformers + accelerate + datasets (for .adapt()).
"""
from __future__ import annotations
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner, sanitize_text


def _fetch(source: str) -> str:
    """Return raw text from a URL, a local file, or a raw string."""
    if source.startswith("http://") or source.startswith("https://"):
        import urllib.request
        req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        html = re.sub(r"(?is)<(script|style|table|sup|ref)[^>]*>.*?</\1>", " ", html)
        text = re.sub(r"(?s)<[^>]+>", " ", html)            # strip tags
        text = re.sub(r"&[a-z]+;", " ", text)
        return re.sub(r"\s+", " ", text)
    if source.endswith(".pdf"):
        from pypdf import PdfReader
        return " ".join(p.extract_text() or "" for p in PdfReader(source).pages)
    if os.path.exists(source):
        return open(source, encoding="utf-8", errors="ignore").read()
    return source  # raw text


def _chunk(text: str, min_len: int = 40, max_len: int = 300) -> list:
    """Split into sentence-ish chunks of a reasonable length (skip boilerplate)."""
    sents = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for s in sents:
        s = s.strip()
        if min_len <= len(s) <= max_len and not re.search(r"\b(edit|jump to|retrieved|ISBN|doi)\b", s, re.I):
            out.append(sanitize_text(s))
    return out


class DocumentLearner:
    def __init__(self, model="all-MiniLM-L6-v2", **kw):
        self.r = GeometricReasoner(model_name=model, rerank_k=kw.pop("rerank_k", 5), **kw)
        self.chunks = []

    def learn(self, source, source_name=None):
        """Ingest a link/file/text into the queryable store. Returns the number of chunks added."""
        text = _fetch(source)
        new = _chunk(text)
        for c in new:
            self.r.add_fact(c, source=source_name or source, kind="doc")
        self.chunks += new
        return len(new)

    def adapt(self, epochs: int = 1, batch_size: int = 16):
        """SELF-SUPERVISED adaptation (SimCSE): each chunk is its own positive via dropout; in-batch negatives.
        Tunes the embedder to the document's vocabulary. Needs transformers+accelerate+datasets."""
        from sentence_transformers import InputExample
        from sentence_transformers.sentence_transformer import losses
        from torch.utils.data import DataLoader
        ex = [InputExample(texts=[c, c]) for c in self.chunks]      # SimCSE: (x, x) with dropout noise
        loader = DataLoader(ex, shuffle=True, batch_size=batch_size)
        loss = losses.MultipleNegativesRankingLoss(self.r.model)
        self.r.model.fit(train_objectives=[(loader, loss)], epochs=epochs, warmup_steps=max(1, len(ex)//10),
                         show_progress_bar=False)
        self.r._F = None                                            # invalidate cached embeddings
        return self

    def ask(self, question):
        return self.r.ask(question)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "https://en.wikipedia.org/wiki/Octopus"
    dl = DocumentLearner()
    n = dl.learn(src)
    print(f"learned {n} chunks from {src}")
    for q in ["How many hearts does an octopus have?", "What are octopuses known for?"]:
        a = dl.ask(q)
        print(f"  Q: {q}\n     -> {a['text'][:100]!r} (grounded={a['grounded']})")
