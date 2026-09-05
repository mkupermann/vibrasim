from hashlib import sha256
from pathlib import Path

from vibrasim2.p1.registration import P0_INPUT_DIGEST, P1_DESIGN_PATH, P1_DESIGN_SHA256


ROOT = Path(__file__).resolve().parents[2]


def test_p1_design_identity_matches_committed_contract():
    data = (ROOT / P1_DESIGN_PATH).read_text(encoding="utf-8").replace("\r\n", "\n")
    assert sha256(data.encode("utf-8")).hexdigest() == P1_DESIGN_SHA256


def test_p0_input_digest_is_frozen_to_completed_null():
    assert P0_INPUT_DIGEST == "bdf94735ba80fb719ac7f8e5c78b75705f706b9e5d8a179f09c199b6d838826e"
