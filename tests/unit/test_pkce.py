import pytest
from src.auth.pkce import generate_pkce_pair
import base64, hashlib

def test_pkce_generates_two_strings():
    verifier, challenge = generate_pkce_pair()
    assert isinstance(verifier, str)
    assert isinstance(challenge, str)

def test_pkce_verifier_length():
    verifier, _ = generate_pkce_pair()
    # base64url of 32 bytes = 43 chars
    assert len(verifier) == 43

def test_pkce_challenge_is_sha256_of_verifier():
    verifier, challenge = generate_pkce_pair()
    digest = hashlib.sha256(verifier.encode()).digest()
    expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    assert challenge == expected

def test_pkce_pairs_are_unique():
    pair1 = generate_pkce_pair()
    pair2 = generate_pkce_pair()
    assert pair1[0] != pair2[0]
    assert pair1[1] != pair2[1]