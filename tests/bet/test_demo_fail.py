"""Demo BET test that always FAILS."""
import json
import os


def test_demo_fail():
    """Always fails."""
    out_dir = os.environ.get('EQMOD_BET_OUT_DIR', '/tmp')
    os.makedirs(out_dir, exist_ok=True)
    
    result = {
        "verdict": "failed",
        "item_id": os.environ.get('EQMOD_BET_ITEM_ID', 'unknown'),
        "message": "Demo test failed",
        "attempts": 1
    }
    
    with open(f'{out_dir}/result.json', 'w') as f:
        json.dump(result, f)
    
    assert False, "Demo failure"
