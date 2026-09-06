import numpy as np
import json
import pytest
from vibrasim2.p3 import initial, step, record, trajectory


def test_ledger_balances_for_all_transfer_modes():
    for arm in ('full','no_capture','no_feedback','drive_off','damaged'):
        s=initial()
        s['e'][:]=[1,2,3,4,5,6]
        s['r'][:]=.29
        s['supplied']=float(s['e'].sum()+s['r'].sum())
        next_s,_=step(s,arm,2000,.02)
        assert abs(record(next_s,2000,.02)['residual']) < 1e-12
        assert np.all(next_s['e'] >= 0)
        assert np.all(next_s['r'] >= 0)


def test_unfunded_bonds_expire_at_exact_lifetime():
    s=initial()
    s,events=step(s,'no_capture',250,.02)
    assert (s['born'] == -1).all()
    assert len(events)==6


def test_local_payment_and_stream_yields_initial_before_stepping():
    stream=trajectory('full',.02,horizon=.04)
    assert next(stream)[0]['supplied']==0
    assert next(stream)[0]['supplied']==.02
    s=initial()
    s['born'][:]=-1
    s['r'][:2]=.11
    n,events=step(s,'full',1,.02)
    assert events==[['formed',0,1]]
    assert abs(n['consumed']-1.4)<1e-12


def test_invalid_artifacts_are_fail_not_a_scientific_verdict(tmp_path):
    from vibrasim2.p3 import assess
    (tmp_path/'run.json').write_text(json.dumps({'cells': []}))
    assert assess(tmp_path)['verdict'] == 'FAIL'


def test_unknown_arm_is_rejected():
    with pytest.raises(ValueError):
        next(trajectory('typo', .02))


def test_envelope_identifies_p3_and_maps_energy():
    from vibrasim2.p3 import envelope
    from vibrasim2.viewer_process import ViewerController
    row=record(initial(),0,.02)
    row['e'][0]=2
    frame=envelope(row,'full-primary',1)
    assert frame.frame.positions[0,2] == 8
    controller=ViewerController(stream_kind='replay')
    controller.accept(frame)
    assert 'P3 · REPLAY' in controller.hud()
