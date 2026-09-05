from hashlib import sha256
from pathlib import Path

from vibrasim2.p2.registration import P2_REGISTRATION_PATH, P2_REGISTRATION_SHA256


def test_committed_registration_digest_matches_frozen_identity():
    root = Path(__file__).resolve().parents[2]
    payload = (root / P2_REGISTRATION_PATH).read_bytes()

    assert sha256(payload).hexdigest() == P2_REGISTRATION_SHA256

