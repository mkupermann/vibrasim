"""Frozen MM3 stress test. No test video, text or labels enter spring memory."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import numpy as np
from .learning import LearningConfig, SensoryPorts, SpringMemory, retrieval_score, verdict
from .media import Clip

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'archive/run-logs/media-screening/20260912'
PROTOCOL = ROOT / 'docs/amendments/mm3_real_scene_transfer.md'
TRAIN = ['M5IJoW6arps', 'NQnwh6eAuIY', 'dfxOv8kx-KI', 'eo-6hkzQ7vs', '3tUlhM80ObM', 'U83UYsdrXmQ']
TEST = ['napC3T9u3xs', '0XyB9NziBto', 'QdIH7AcPbKw']


def probe(model, clips, candidates, encoder):
    before = model.strength.copy()
    trials = []
    for expected, clip in enumerate(clips):
        responses = []
        for i in range(40):
            # Held-out images/text deliberately absent from the sensory call.
            a, _ = encoder.encode(np.zeros((32, 32)), clip.sample(i)[1])
            responses.append(model.cue(a)[:64].tolist())
        credit, scores = retrieval_score(np.mean(responses, axis=0), candidates, expected)
        trials.append(dict(source=clip.source, expected=expected, credit=credit,
                           scores=scores, responses=responses))
    if not np.array_equal(before, model.strength):
        raise RuntimeError('Probe changed persistent springs')
    return dict(accuracy=float(np.mean([t['credit'] for t in trials])), trials=trials,
                immutable=True)


def run(output):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('status', '--porcelain', '--', str(PROTOCOL), 'vibrasim2/transfer.py', 'vibrasim2/learning.py'):
        raise RuntimeError('Commit protocol and implementation before running')
    seal = git('log', '-1', '--format=%H', '--', str(PROTOCOL))
    if not seal:
        raise RuntimeError('Missing protocol seal')
    clips = {}
    for video_id in TRAIN + TEST:
        metadata = json.loads((DATA/video_id/'clip.json').read_text())
        with np.load(DATA/video_id/'clip.npz') as arrays:
            clip = Clip(metadata['title'], arrays['frames'], arrays['audio'], source=metadata['url'])
        if clip.digest != metadata['sha256'] or len(clip.frames) != 40:
            raise RuntimeError('Source integrity failure')
        clips[video_id] = clip
    if len({c.digest for c in clips.values()}) != 9:
        raise RuntimeError('Duplicate media')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    config = LearningConfig()
    encoder = SensoryPorts(config)
    candidates = [encoder.encode(clips[TRAIN[i]].frames[0], np.zeros(1600))[1][:64] for i in (0, 2, 4)]
    arms = {name: SpringMemory(config) for name in ('trained', 'frozen', 'shuffled')}
    evidence = dict(protocol_commit=seal, protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
                    head=git('rev-parse', 'HEAD'), dirty=bool(git('status', '--porcelain')),
                    config=config.as_dict(), train=TRAIN, test=TEST,
                    hashes={k: c.digest for k,c in clips.items()}, candidates=[x.tolist() for x in candidates],
                    checkpoints=[], limitations='Three provisional-category test clips; scene retrieval only; no human comparison.')
    started = time.perf_counter()
    for i in range(40):
        for j, video_id in enumerate(TRAIN):
            image, audio, _ = clips[video_id].sample(i)
            a, b = encoder.encode(image, audio)
            _, wrong = encoder.encode(clips[TRAIN[(j+2)%6]].frames[i], audio)
            arms['trained'].expose(a, b, .1)
            arms['frozen'].expose(a, b, .1, plastic=False)
            arms['shuffled'].expose(a, wrong, .1)
        if i + 1 in (10, 20, 40):
            checkpoint = dict(seconds_per_clip=(i+1)/10, exposure_seconds=6*(i+1)/10, arms={})
            models = dict(arms)
            for name in ('retained', 'erased'):
                models[name] = SpringMemory(config)
                models[name].restore(arms['trained'].snapshot())
            models['retained'].idle(5)
            checkpoint['erasure_before_mass'] = float(models['erased'].strength.sum())
            models['erased'].strength.fill(0)
            models['erased'].reset_activity()
            for name, model in models.items():
                # Probe a copy so even transient activity cannot affect training.
                copy = SpringMemory(config)
                copy.restore(model.snapshot())
                checkpoint['arms'][name] = probe(copy, [clips[k] for k in TEST], candidates, encoder)
                checkpoint['arms'][name]['state'] = model.snapshot()
            evidence['checkpoints'].append(checkpoint)
            (output/'progress.json').write_text(json.dumps(evidence))
            print(json.dumps({k: checkpoint[k] for k in ('exposure_seconds', 'seconds_per_clip')}), flush=True)
        if time.perf_counter() - started > 120:
            evidence['verdict'] = 'INCONCLUSIVE'
            evidence['run_status'] = 'FAILED'
            evidence['failure'] = 'Exceeded preregistered compute cap; requires LOGBOOK post-mortem'
            break
    evidence['wall_seconds'] = time.perf_counter() - started
    if 'verdict' not in evidence:
        evidence['verdict'] = verdict({k:v['accuracy'] for k,v in evidence['checkpoints'][-1]['arms'].items()}, True)
    (output/'result.json').write_text(json.dumps(evidence, indent=2)+'\n')
    return evidence


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(result['verdict'])
