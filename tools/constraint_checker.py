"""Constraint checker — guards the project's hard rules.

Run before every commit, before every experiment, before every
design decision. If any check fails, STOP and rethink.

These are not guidelines. They are laws.
"""
import ast
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
VIOLATIONS = []


def fail(rule: str, detail: str):
    VIOLATIONS.append(f"VIOLATION [{rule}]: {detail}")


def check_no_llm_imports():
    """No LLM, transformer, pre-trained model imports anywhere."""
    banned = [
        'torch', 'tensorflow', 'transformers', 'openai', 'anthropic',
        'whisper', 'wav2vec', 'vosk', 'huggingface', 'sentence_transformers',
        'gensim', 'spacy', 'nltk.classify', 'sklearn.neural_network',
        'keras', 'fastai',
    ]
    for py in REPO.rglob("*.py"):
        if 'brian2' in str(py) or '.venv' in str(py) or '__pycache__' in str(py):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore')
        except:
            continue
        for ban in banned:
            if f"import {ban}" in text or f"from {ban}" in text:
                fail("NO-LLM", f"{py.relative_to(REPO)}: imports '{ban}'")


def check_no_labels():
    """No human labeling, no forced alignment, no supervised training."""
    label_patterns = [
        'label_map', 'class_labels', 'y_train', 'y_test',
        'supervised', 'CrossEntropyLoss', 'categorical_crossentropy',
        'one_hot', 'softmax_output', 'classification_report',
    ]
    for py in REPO.rglob("*.py"):
        if '.venv' in str(py) or '__pycache__' in str(py):
            continue
        if 'brian2' in str(py):
            continue  # Brian2 work is archived, not active
        if 'autopilot' in str(py):
            continue  # Autopilot evaluates bars, not trains
        if 'tools/constraint_checker' in str(py):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore')
        except:
            continue
        for pat in label_patterns:
            if pat in text:
                fail("NO-LABELS", f"{py.relative_to(REPO)}: contains '{pat}'")


def check_no_backprop():
    """No gradient descent, no backpropagation, no optimizer."""
    banned = [
        '.backward()', 'optimizer.step', 'optimizer.zero_grad',
        'nn.Module', 'nn.Linear', 'nn.Conv', 'loss.backward',
        'autograd', 'requires_grad',
    ]
    for py in REPO.rglob("*.py"):
        if '.venv' in str(py) or '__pycache__' in str(py):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore')
        except:
            continue
        for ban in banned:
            if ban in text:
                fail("NO-BACKPROP", f"{py.relative_to(REPO)}: contains '{ban}'")


def check_no_pretrained():
    """No pre-trained embeddings, no foundation models."""
    banned = [
        'from_pretrained', 'load_model(', 'resnet', 'vgg16', 'bert_',
        'gpt2', 'openai_clip', 'dino_', 'imagenet', 'word2vec', 'glove_',
        'fasttext_', 'BPETokenizer', 'AutoTokenizer',
    ]
    for py in REPO.rglob("*.py"):
        if '.venv' in str(py) or '__pycache__' in str(py):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore').lower()
        except:
            continue
        for ban in banned:
            if ban in text:
                # Skip comments and strings that explain what we DON'T use
                lines = text.split('\n')
                for ln, line in enumerate(lines):
                    stripped = line.strip()
                    if ban in stripped and not stripped.startswith('#') and 'not' not in stripped and 'no ' not in stripped and 'keine' not in stripped:
                        fail("NO-PRETRAINED", f"{py.relative_to(REPO)}:{ln+1}: contains '{ban}'")


def check_no_output_per_class():
    """No one-neuron-per-class, no output atom per label."""
    patterns = [
        'output_atoms', 'output_per_class', 'class_neuron',
        'output_labels', 'winner_class',
    ]
    for py in REPO.rglob("*.py"):
        if '.venv' in str(py) or '__pycache__' in str(py):
            continue
        if 'constraint_checker' in str(py):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore')
        except:
            continue
        for pat in patterns:
            if pat in text:
                fail("NO-CLASSIFIER", f"{py.relative_to(REPO)}: contains '{pat}' — this is supervised ML")


def check_substrate_only():
    """Learning must come from substrate physics, not imported equations.

    Allowed: STDP/Hebbian that emerges from bridge co-activation in
    the vibration substrate. NOT allowed: STDP equations imported
    from Brian2 or any neuroscience library applied to substrate objects.
    """
    # Check that no file imports Brian2 for substrate learning
    for py in (REPO / "world").rglob("*.py"):
        if '__pycache__' in str(py):
            continue
        try:
            text = py.read_text(encoding='utf-8', errors='ignore')
        except:
            continue
        if 'from brian2' in text or 'import brian2' in text:
            fail("SUBSTRATE-ONLY", f"{py.relative_to(REPO)}: imports brian2 in substrate code")


def check_pre_registration():
    """Every BET must have pre-registered bars before any run."""
    bet_dirs = list((Path.home() / ".eqmod" / "bet").glob("BET-*"))
    amendments = list((REPO / "docs" / "amendments").glob("bet_*.md"))
    amendment_names = {a.stem.replace('bet_', 'BET-').replace('_', '-').upper() for a in amendments}

    for bet_dir in bet_dirs:
        name = bet_dir.name
        if name not in amendment_names:
            # Check if result exists without pre-registration
            if (bet_dir / "result.json").exists():
                fail("PRE-REGISTER", f"{name}: has result.json but no pre-registration in docs/amendments/")


def main():
    print("EQMOD Constraint Checker", flush=True)
    print("=" * 50, flush=True)

    checks = [
        ("NO LLM/Transformer/Pre-trained", check_no_llm_imports),
        ("NO Labels/Supervised Training", check_no_labels),
        ("NO Backpropagation", check_no_backprop),
        ("NO Pre-trained Models", check_no_pretrained),
        ("NO Output-per-Class Classifier", check_no_output_per_class),
        ("Substrate Physics Only", check_substrate_only),
        ("Pre-registration Discipline", check_pre_registration),
    ]

    for name, fn in checks:
        try:
            fn()
            status = "PASS" if not any(name.split()[0] in v for v in VIOLATIONS) else "FAIL"
        except Exception as e:
            fail(name, f"Check crashed: {e}")
            status = "ERROR"
        # Count new violations
        print(f"  [{status}] {name}", flush=True)

    print(f"\n{'=' * 50}", flush=True)
    if VIOLATIONS:
        print(f"VIOLATIONS: {len(VIOLATIONS)}", flush=True)
        for v in VIOLATIONS:
            print(f"  {v}", flush=True)
        print(f"\nSTOP. Fix violations before proceeding.", flush=True)
        return 1
    else:
        print("ALL CLEAR. No constraint violations.", flush=True)
        return 0


if __name__ == "__main__":
    sys.exit(main())
