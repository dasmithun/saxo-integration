import pytest
import json
import time
import os
from src.auth.token_manager import (
    save_tokens, load_tokens,
    is_access_token_expired
)

TEST_TOKEN_FILE = "tokens_test.json"

def make_tokens(expires_in=1200, age_seconds=0):
    return {
        "access_token":  "test_token",
        "refresh_token": "test_refresh",
        "expires_in":    expires_in,
        "obtained_at":   time.time() - age_seconds
    }

def test_token_not_expired_when_fresh():
    tokens = make_tokens(expires_in=1200, age_seconds=0)
    assert not is_access_token_expired(tokens)

def test_token_expired_when_old():
    tokens = make_tokens(expires_in=1200, age_seconds=1200)
    assert is_access_token_expired(tokens)

def test_token_expired_within_buffer():
    # 60s buffer — token expiring in 30s should be considered expired
    tokens = make_tokens(expires_in=1200, age_seconds=1171)
    assert is_access_token_expired(tokens, buffer_seconds=60)

def test_token_not_expired_outside_buffer():
    # Token expiring in 120s should NOT be expired with 60s buffer
    tokens = make_tokens(expires_in=1200, age_seconds=1020)
    assert not is_access_token_expired(tokens, buffer_seconds=60)