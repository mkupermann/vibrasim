"""Demo BET test that always returns NULL."""
import json
import os


def test_demo_null():
    """Always returns NULL verdict (informative failure)."""
    out_dir = os.environ.get('EQMOD_BET_OUT_DIR', '/tmp')
    os.makedirs(out_dir, exist_ok=True)
    
    result = {
        "verdict": "null",
        "item_id": os.environ.get('EQMOD_BET_ITEM_ID', 'unknown'),
        "message": "Demo test returned NULL (informative failure)",
        "attempts": 1
    }
    
    with open(f'{out_dir}/result.json', 'w') as f:
        json.dump(result, f)
    
    assert True
