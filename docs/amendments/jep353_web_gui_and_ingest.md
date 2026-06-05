# JEP-353 — Web GUI for talking/training + multi-source ingestion (URL/PDF/txt)

## Motivation (Michael)
"I need a full web GUI for talking and training, and to provide links to websites, docs, pdf, txt and other
sources." Build a browser UI over the existing durable `Conversation` (talk + teach + draw + ask), plus an ingestion
layer that pulls text from a .txt file, a URL (HTML stripped), or a PDF — feeding it into the brain. Stdlib
http.server (no Flask), `requests` for URLs, regex HTML-strip, optional pypdf for PDF. No transformer.

## Method
`world/ingest.py`: `extract_text(source)` → text from .txt / http(s) URL (strip tags) / .pdf (pypdf if installed,
else a clear message). `tools/web_gui.py`: a `WebBrain` wrapper (say / ingest over the durable Conversation) served
by a stdlib HTTP server — GET `/` chat page; POST `/say`; POST `/ingest` (text, file path, or URL); `/knowledge.png`.

## Pre-registered bars (BEFORE the run)
- **J353a (ingestion):** `extract_text` returns the right text for a .txt file and for an HTML string/URL (tags
  stripped, readable text), and PDF either extracts (if pypdf) or returns a clear "install pypdf" message — both
  seeds / deterministic.
- **J353b (web endpoints):** the `WebBrain.say` path teaches (memory grows) and answers correctly; `WebBrain.ingest`
  grows the brain from text; the HTTP server starts and `GET /` serves the chat page (live socket smoke).
- **J353c (durable + behaviors):** statements teach, questions answer, "draw what you know" works, all through the
  web layer; persists.

Predicted most-likely failure: the HTML-strip regex leaves script/style noise that the engine can't parse (low
ingest yield) — strip script/style blocks first; or a port clash in the smoke (use port 0 / a high port). If J353a
under-extracts from HTML, report the noise.

## Result: **PASS**
- **J353a:** `extract_text` reads a .txt file; `_strip_html` removes script/style/tags (readable text, no markup);
  PDF path is graceful (extracts with pypdf, else a clear install message). **PASS.**
- **J353b:** `WebBrain.say` teaches (memory grows) and answers ("Is a poodle a mammal?" → "Yes."); `WebBrain.ingest`
  grows the brain from text; the stdlib HTTP server starts, `GET /` serves the chat page, and POST `/say` teaches +
  answers correctly over a live socket. **PASS.**
- **J353c:** durable + the conversation behaviors (teach/answer/draw/ingest) all run through the web layer. **PASS.**

## Verdict: **PASS**
A full browser web GUI to TALK to and TRAIN the substrate (`tools/web_gui.py`, stdlib server — open
http://127.0.0.1:8765), plus multi-source ingestion (`world/ingest.py`: .txt, http(s) URL with HTML stripped, PDF
via pypdf). Michael can paste a link or point at a file and the brain reads it, then discuss it in the same page.
No Flask, no transformer, no pretrained model. (PDF needs `pip install pypdf`; everything else is stdlib + requests.)

