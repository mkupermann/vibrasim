"""P3 seeded open transport construction; no emergence claim."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

EDGES = ((0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5))
ARMS = ('full', 'no_feedback', 'no_capture', 'drive_off', 'damaged')
ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / 'docs/amendments/v2_p3_open_maintenance.md'


def initial():
    return dict(e=np.zeros(6), r=np.zeros(6), born=np.zeros(6, dtype=int),
                consumed=1.2, heat=0.0, damage=0.0, supplied=0.0)


def step(s, arm, tick, dt):
    """One fixed explicit step, all resource transfers locally accounted."""
    e, r, born = s['e'].copy(), s['r'].copy(), s['born'].copy()
    live = born >= 0
    change = np.zeros(6)
    for k, (a, b) in enumerate(EDGES):
        conductance = 0.02 + (2.0 if live[k] and arm != 'no_feedback' else 0.0)
        flow = dt * conductance * (e[a] - e[b])
        change[a] -= flow
        change[b] += flow
    source = 0.0 if arm == 'drive_off' and tick > round(40 / dt) else dt
    change[0] += source
    absorbed = dt * 0.3 * e
    e += change - absorbed
    heat = s['heat']
    if arm == 'no_capture':
        heat += float(absorbed.sum())
    else:
        r += absorbed
    leak = dt * 0.2 * r
    r -= leak
    overflow = np.maximum(r - 0.3, 0)
    r -= overflow
    heat += float(leak.sum() + overflow.sum())
    damage = s['damage']
    events = []
    if arm == 'damaged' and tick == round(40 / dt):
        for pair in ((1, 2), (4, 5)):
            born[EDGES.index(pair)] = -1
            events.append(['damage', *pair])
        damage += float(r.sum())
        r[:] = 0
    for k, pair in enumerate(EDGES):
        if born[k] >= 0 and tick - born[k] >= round(5 / dt):
            born[k] = -1
            events.append(['expired', *pair])
    consumed = s['consumed']
    for k, (a, b) in enumerate(EDGES):
        if born[k] < 0 and r[a] >= 0.1 and r[b] >= 0.1:
            r[a] -= 0.1
            r[b] -= 0.1
            consumed += 0.2
            born[k] = tick
            events.append(['formed', a, b])
    return dict(e=e, r=r, born=born, consumed=consumed, heat=heat,
                damage=damage, supplied=s['supplied'] + source), events


def record(s, tick, dt):
    residual = float(s['e'].sum() + s['r'].sum() + s['consumed'] +
                     s['heat'] + s['damage'] - 1.2 - s['supplied'])
    return dict(tick=tick, t=tick * dt, e=s['e'].tolist(), r=s['r'].tolist(),
                born=s['born'].tolist(), live=int((s['born'] >= 0).sum()),
                residual=residual, consumed=s['consumed'], heat=s['heat'],
                damage=s['damage'], supplied=s['supplied'])


def trajectory(arm, dt, horizon=120):
    if arm not in ARMS or dt not in (.02, .01) or horizon < 0:
        raise ValueError('Unregistered arm or timestep')
    s = initial()
    yield record(s, 0, dt), []
    for tick in range(1, round(horizon / dt) + 1):
        s, events = step(s, arm, tick, dt)
        yield record(s, tick, dt), events


def envelope(row, arm, sequence, complete=False):
    from vibrasim2.observation import (WireframeFrame, ObservationEnvelope,
        ObservationStatus, EdgeState, EdgeKind)
    angle = np.arange(6) * np.pi / 3
    xy = np.column_stack((15.5 + 8*np.cos(angle), 15.5 + 8*np.sin(angle)))
    points = np.column_stack((xy, 4 * np.asarray(row['e'])))
    return ObservationEnvelope(1, 'v2-p3-engineering', 'SEEDED TRANSPORT', arm,
        (0, 0), row['tick'], row['t'], sequence, time.monotonic_ns(),
        ObservationStatus.COMPLETE if complete else ObservationStatus.RUNNING,
        4.0, WireframeFrame(points, np.array(EDGES), tuple(
            EdgeState.LIVE if b >= 0 else EdgeState.AVAILABLE for b in row['born']),
            (EdgeKind.MATTER,)*6, particle_values=np.asarray(row['r'])/0.3))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def registered_cells():
    return [dict(id=a+'-'+p,arm=a,dt=dt)
            for p,dt in [('primary',.02),('half',.01)] for a in ARMS] + [
            dict(id='full-repeat',arm='full',dt=.02)]


def assess(root):
    try:
        return _assess(root)
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
        return dict(verdict='FAIL', error=str(exc))


def _assess(root):
    manifest = json.loads((root/'run.json').read_text())
    if manifest['cells'] != registered_cells():
        raise ValueError('Cell matrix differs from registration')
    if manifest['registration'] != digest(REGISTRATION) or manifest['core'] != digest(Path(__file__)):
        raise ValueError('Source or registration hash mismatch')
    metrics, all_events = {}, {}
    valid = True
    hashes = {}
    for cell in manifest['cells']:
        path = root/(cell['id']+'.jsonl')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if [r['tick'] for r in rows] != list(range(round(120/cell['dt'])+1)):
            raise ValueError('Incomplete tick sequence')
        hashes[path.name] = digest(path)
        for r in rows:
            if (len(r['e']) != 6 or len(r['r']) != 6 or len(r['born']) != 6
                    or r['live'] != sum(b >= 0 for b in r['born'])
                    or r['t'] != r['tick'] * cell['dt']):
                raise ValueError('Malformed state')
            ledger = sum(r['e']) + sum(r['r']) + r['consumed'] + r['heat'] + r['damage'] - 1.2 - r['supplied']
            values = r['e'] + r['r'] + [r['residual'],r['consumed'],r['heat'],r['damage'],r['supplied']]
            valid &= bool(np.isfinite(values).all() and min(r['e']+r['r']) >= -1e-12
                          and abs(r['residual']) <= 1e-9 and abs(ledger) <= 1e-9)
        late = [r['live'] for r in rows if 100 <= r['t'] <= 120]
        recovered = any(r['live'] >= 5 for r in rows if 40 < r['t'] <= 60)
        metrics[cell['id']] = dict(late_mean=float(np.mean(late)), recovered=recovered,
                                   max_residual=max(abs(r['residual']) for r in rows))
        all_events[cell['id']] = [(r['tick'], r['events']) for r in rows if r['events']]
    convergence = all(abs(metrics[a+'-primary']['late_mean'] - metrics[a+'-half']['late_mean']) <= .25 for a in ARMS)
    reproduction = all_events['full-primary'] == all_events['full-repeat']
    science = (all(metrics[a+'-primary']['late_mean'] >= 5 for a in ('full','damaged'))
        and metrics['no_feedback-primary']['late_mean'] <= 3
        and all(metrics[a+'-primary']['late_mean'] == 0 for a in ('no_capture','drive_off'))
        and metrics['damaged-primary']['recovered'])
    verdict = 'INCONCLUSIVE' if not(valid and convergence and reproduction) else ('PASS' if science else 'NULL')
    return dict(verdict=verdict, numerical_valid=bool(valid), convergence=convergence,
                reproduction=reproduction, scientific_gate=science, metrics=metrics, hashes=hashes)


def run(root, observe):
    root.mkdir(parents=True, exist_ok=False)
    cells = registered_cells()
    manifest = dict(experiment='P3 engineering',cells=cells,registration=digest(REGISTRATION),
                    core=digest(Path(__file__)), started=time.time())
    (root/'run.json').write_text(json.dumps(manifest, indent=2))
    handle = None
    if observe:
        from vibrasim2.viewer_process import start_viewer, ViewerProcessConfig
        handle = start_viewer(root, ViewerProcessConfig())
        if handle.process is None:
            raise RuntimeError('Visible observer could not start')
    sequence = 0
    for cell in cells:
        with (root/(cell['id']+'.jsonl')).open('x') as f:
            for row, events in trajectory(cell['arm'],cell['dt']):
                row['events'] = events
                f.write(json.dumps(row,allow_nan=False)+'\n')
                if row['tick'] % round(.2/cell['dt']) == 0:
                    f.flush()
                    if handle and handle.publisher:
                        sequence += 1
                        handle.publisher.publish(envelope(row,cell['id'],sequence))
                        time.sleep(.02)
        print(cell['id']+' persisted',flush=True)
    result = assess(root)
    result['elapsed_seconds'] = time.time()-manifest['started']
    (root/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    assert json.loads((root/'result.json').read_text()) == result
    print(json.dumps(result),flush=True)
    if handle and handle.publisher:
        handle.publisher.publish(envelope(row,'COMPLETE '+result['verdict'],sequence+1,True))


def replay(root):
    """Read existing records only; never execute trajectory or rewrite evidence."""
    from queue import Queue
    from threading import Thread
    from vibrasim2.viewer_process import ViewerProcessConfig
    from vibrasim2.observation_transport import LatestOnlyPublisher
    from vibrasim2.wireframe import WireframeViewer
    result = assess(root)
    if result['verdict'] == 'FAIL':
        raise ValueError(result['error'])
    frame_queue = Queue(maxsize=1)
    publisher = LatestOnlyPublisher(frame_queue)

    def feed():
        sequence = 0
        for cell in registered_cells():
            with (root/(cell['id']+'.jsonl')).open() as source:
                for line in source:
                    row = json.loads(line)
                    if row['tick'] % round(.2/cell['dt']) == 0:
                        sequence += 1
                        publisher.publish(envelope(row,cell['id'],sequence))
                        time.sleep(.05)
        publisher.publish(envelope(row,'COMPLETE '+result['verdict'],sequence+1,True))
    Thread(target=feed,daemon=True).start()
    WireframeViewer(frame_queue,None,ViewerProcessConfig(),stream_kind='replay',
                    recorded_verdict=result['verdict']).run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--observe',action='store_true')
    parser.add_argument('--replay',action='store_true')
    args = parser.parse_args()
    if args.replay:
        replay(args.output)
    else:
        run(args.output,args.observe)
