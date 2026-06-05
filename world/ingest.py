"""ingest — pull plain text out of the sources Michael wants the brain to read: .txt files, web URLs, and PDFs.

No transformer, no pretrained model — just file reading, an HTTP fetch (requests/urllib), a regex HTML-stripper, and
optional pypdf for PDFs. Returns plain text that `Conversation.read_text` then learns.
"""
import os
import re
import html as _html


def _strip_html(s):
    s = re.sub(r"(?is)<(script|style|head|nav|footer)[^>]*>.*?</\1>", " ", s)   # drop noise blocks
    s = re.sub(r"(?s)<[^>]+>", " ", s)                                          # drop tags
    s = _html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def text_from_url(url, timeout=15):
    try:
        import requests
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "eqmod-substrate/1.0"})
        raw = r.text
    except Exception:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "eqmod-substrate/1.0"})
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    return _strip_html(raw)


def text_from_pdf(path):
    try:
        import pypdf
    except Exception:
        return "(PDF support needs pypdf — run: .venv\\Scripts\\python.exe -m pip install pypdf)"
    out = []
    reader = pypdf.PdfReader(path)
    for page in reader.pages:
        out.append(page.extract_text() or "")
    return "\n".join(out).strip()


def extract_text(source):
    """source = a .txt/.pdf file path, an http(s) URL, or raw text. Returns plain text."""
    s = (source or "").strip()
    if s.lower().startswith(("http://", "https://")):
        return text_from_url(s)
    if os.path.isfile(s):
        ext = os.path.splitext(s)[1].lower()
        if ext == ".pdf":
            return text_from_pdf(s)
        if ext in (".html", ".htm"):
            return _strip_html(open(s, encoding="utf-8", errors="ignore").read())
        return open(s, encoding="utf-8", errors="ignore").read()       # .txt and anything plain
    return s                                                            # treat as raw pasted text
