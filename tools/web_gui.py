"""web_gui — a browser UI to TALK to and TRAIN the substrate, and to feed it links / docs / pdf / txt.

Runs a small local web server (stdlib only) over the durable Conversation. Open the printed URL in a browser:
  .venv\\Scripts\\python.exe tools\\web_gui.py            (default brain ~/.eqmod/brain/web, port 8765)
  .venv\\Scripts\\python.exe tools\\web_gui.py --dir mybrain --port 8800
No transformer, no pretrained model — it serves the same substrate conversation as tools/talk.py.
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.conversation import Conversation
from world.ingest import extract_text


class WebBrain:
    """Thread-safe wrapper around the durable Conversation for the web layer."""
    def __init__(self, brain_dir=None):
        self.conv = Conversation(brain_dir=brain_dir)
        self.lock = threading.Lock()

    def say(self, text):
        with self.lock:
            r = self.conv.say(text); self.conv.save()
            return {"reply": r, "facts": self.conv.n_facts}

    def ingest(self, source):
        with self.lock:
            text = extract_text(source)
            res = self.conv.read_text(text); self.conv.save()
            gaps = self.conv.gaps()[:6]
            return {"learned": res["facts_learned"], "facts": res["total_facts"],
                    "concepts": res["concepts"], "chars": len(text), "gaps": gaps}

    def draw(self):
        with self.lock:
            from world.visualize import draw_knowledge
            return draw_knowledge(self.conv.sm, title="What I know")


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Talk to the substrate</title>
<style>body{font-family:system-ui,Arial;max-width:760px;margin:24px auto;padding:0 12px}
#log{border:1px solid #ccc;border-radius:8px;padding:12px;height:48vh;overflow:auto;background:#fafafa}
.you{color:#063}.it{color:#06c;margin:4px 0 12px}
input,button{font-size:16px;padding:8px}#q{width:74%}
.row{margin:10px 0}small{color:#666}</style></head><body>
<h2>Talk to the substrate <small>(no LLM — it learns as you teach it)</small></h2>
<div id="log"></div>
<div class="row"><input id="q" placeholder="Teach it ('A poodle is a dog.') or ask ('Is a poodle an animal?')"
 autofocus><button onclick="say()">Send</button></div>
<div class="row"><small>Train from a source (URL / .txt / .pdf path, or paste text):</small><br>
<input id="src" style="width:74%" placeholder="https://... or C:\\path\\file.txt or paste text">
<button onclick="ingest()">Read it</button></div>
<div class="row"><button onclick="say('draw what you know')">Draw what it knows</button>
<button onclick="say('what is not clear to you?')">What is unclear?</button> <span id="facts"></span></div>
<script>
const log=document.getElementById('log');
function add(c,t){const d=document.createElement('div');d.className=c;d.textContent=t;log.appendChild(d);log.scrollTop=log.scrollHeight;}
async function say(t){t=t||document.getElementById('q').value.trim();if(!t)return;document.getElementById('q').value='';
 add('you','you> '+t);const r=await fetch('/say',{method:'POST',body:JSON.stringify({text:t})});const j=await r.json();
 add('it','it > '+j.reply);document.getElementById('facts').textContent='('+j.facts+' facts)';}
async function ingest(){const s=document.getElementById('src').value.trim();if(!s)return;add('you','read> '+s.slice(0,80));
 const r=await fetch('/ingest',{method:'POST',body:JSON.stringify({source:s})});const j=await r.json();
 add('it','it > read '+j.chars+' chars, learned '+j.learned+' new facts (now '+j.facts+'). '+
 (j.gaps&&j.gaps.length?'Still unclear: '+j.gaps.join(', '):''));document.getElementById('facts').textContent='('+j.facts+' facts)';}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')say();});
</script></body></html>"""


def make_handler(brain):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            b = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(code); self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, PAGE, "text/html; charset=utf-8")
            elif self.path == "/knowledge.png":
                p = brain.draw()
                if p and os.path.exists(p):
                    self._send(200, open(p, "rb").read(), "image/png")
                else:
                    self._send(404, b"no image", "text/plain")
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/say":
                self._send(200, json.dumps(brain.say(data.get("text", ""))))
            elif self.path == "/ingest":
                self._send(200, json.dumps(brain.ingest(data.get("source", ""))))
            else:
                self._send(404, b"not found", "text/plain")

        def log_message(self, *a):
            pass
    return H


def main(argv):
    brain_dir = None; port = 8765
    if "--dir" in argv:
        brain_dir = argv[argv.index("--dir") + 1]
    if "--port" in argv:
        port = int(argv[argv.index("--port") + 1])
    brain_dir = brain_dir or os.path.join(os.path.expanduser("~"), ".eqmod", "brain", "web")
    brain = WebBrain(brain_dir)
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(brain))
    print(f"Talk to the substrate in your browser:  http://127.0.0.1:{port}")
    print(f"(brain folder: {brain_dir} — it remembers across sessions. Ctrl+C to stop.)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping…")
        srv.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
