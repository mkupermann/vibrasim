"""Constraint checker — guards the project's hard rules on ACTIVE code.

Run before every commit, before every experiment. If any check fails,
STOP and rethink. These are laws, not guidelines.

Scope: the active substrate (world/ excluding flux/, the chain tools,
autopilot orchestration). Excludes:
  - .venv, __pycache__
  - Brian2 work (archived side-investigation)
  - world/flux/ (separate flux-substrate bet, its own rules)
  - archived BET test files (tests/bet/, tests/)
  - this checker itself (it names the banned tokens by definition)

Detection uses import statements and word boundaries, not substring
matches, so np.clip does not trigger 'clip'.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
VIOLATIONS = []

# Active substrate code — the chain work that must obey the rules.
ACTIVE = [
    REPO / "world" / "physics.py",
    REPO / "world" / "bridges.py",
    REPO / "world" / "state.py",
    REPO / "world" / "config.py",
    REPO / "world" / "reading.py",   # if it ever returns, it gets checked
    REPO / "world" / "interactive.py",
]
ACTIVE = [p for p in ACTIVE if p.exists()]


def fail(rule, detail):
    VIOLATIONS.append(f"[{rule}] {detail}")


def read(p):
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ""


def check_no_imports():
    """No LLM / ML-framework / pre-trained imports in active substrate."""
    banned = [
        'torch', 'tensorflow', 'transformers', 'openai', 'anthropic',
        'whisper', 'wav2vec', 'vosk', 'huggingface', 'keras', 'fastai',
        'sklearn', 'brian2', 'nengo', 'nest',
    ]
    for p in ACTIVE:
        for ln, line in enumerate(read(p).splitlines(), 1):
            s = line.strip()
            if s.startswith('#'):
                continue
            m = re.match(r'(?:from|import)\s+([\w.]+)', s)
            if not m:
                continue
            mod = m.group(1).split('.')[0]
            if mod in banned:
                fail("NO-IMPORT", f"{p.name}:{ln}: imports '{mod}'")


def check_no_backprop():
    """No gradient/backprop tokens in active substrate."""
    banned = [r'\.backward\(', r'optimizer', r'autograd',
              r'requires_grad', r'nn\.Module', r'nn\.Linear']
    for p in ACTIVE:
        text = read(p)
        for pat in banned:
            for m in re.finditer(pat, text):
                # ignore inside comments/docstrings is hard; report line
                ln = text[:m.start()].count('\n') + 1
                line = text.splitlines()[ln-1].strip()
                if line.startswith('#') or line.startswith('"') or line.startswith('*'):
                    continue
                fail("NO-BACKPROP", f"{p.name}:{ln}: '{m.group(0)}'")


def check_no_labels():
    """No supervised-training / label tokens in active substrate code
    (word-boundary, code lines only)."""
    banned = [r'\by_train\b', r'\by_test\b', r'\blabel_map\b',
              r'\bclass_labels\b', r'CrossEntropyLoss', r'\bone_hot\b',
              r'\boutput_atoms\b', r'\bclass_neuron\b']
    for p in ACTIVE:
        text = read(p)
        for pat in banned:
            for m in re.finditer(pat, text):
                ln = text[:m.start()].count('\n') + 1
                line = text.splitlines()[ln-1].strip()
                if line.startswith('#'):
                    continue
                fail("NO-LABELS", f"{p.name}:{ln}: '{m.group(0)}'")


def check_substrate_only():
    """Learning must emerge from substrate physics — no brian2 in world/."""
    for p in (REPO / "world").rglob("*.py"):
        if '__pycache__' in str(p) or 'flux' in str(p):
            continue
        text = read(p)
        if re.search(r'(from|import)\s+brian2', text):
            fail("SUBSTRATE-ONLY", f"{p.name}: imports brian2")


def main():
    print("EQMOD Constraint Checker (active substrate)", flush=True)
    print("=" * 50, flush=True)
    print(f"Scope: {', '.join(p.name for p in ACTIVE)}", flush=True)
    print("-" * 50, flush=True)

    check_no_imports()
    check_no_backprop()
    check_no_labels()
    check_substrate_only()

    if VIOLATIONS:
        print(f"VIOLATIONS: {len(VIOLATIONS)}", flush=True)
        for v in VIOLATIONS:
            print(f"  {v}", flush=True)
        print("\nSTOP. Fix before proceeding.", flush=True)
        return 1
    print("ALL CLEAR. Active substrate obeys the rules.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
