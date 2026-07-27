"""Demo BET test that always PASSES."""
import json
import os


def test_demo_pass():
    """Always passes and writes result.json with passed verdict."""
    out_dir = os.environ.get('EQMOD_BET_OUT_DIR', '/tmp')
    os.makedirs(out_dir, exist_ok=True)
    
    result = {
        "verdict": "passed",
        "item_id": os.environ.get('EQMOD_BET_ITEM_ID', 'unknown'),
        "message": "Demo test passed successfully",
        "attempts": 1
    }
    
    with open(f'{out_dir}/result.json', 'w') as f:
        json.dump(result, f)
    
    assert True
