import json
import time
import requests
import truststore
truststore.inject_into_ssl()

from src.utils.config import APP_KEY, APP_SECRET, SAXO_REDIRECT_URI

SIM_TOKEN_URL = "https://sim.logonvalidation.net/token"
TOKEN_FILE    = "tokens.json"

def save_tokens(tokens):
    tokens["obtained_at"] = time.time()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"✓ Tokens saved to {TOKEN_FILE}")

def load_tokens():
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def is_access_token_expired(tokens, buffer_seconds=60):
    age = time.time() - tokens["obtained_at"]
    return age >= (tokens["expires_in"] - buffer_seconds)

def refresh_access_token(tokens):
    print("Refreshing access token...")
    response = requests.post(SIM_TOKEN_URL, data={
        "grant_type":    "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id":     APP_KEY,
        "client_secret": APP_SECRET,
        "redirect_uri":  SAXO_REDIRECT_URI,
    })
    response.raise_for_status()
    new_tokens = response.json()
    new_tokens["obtained_at"] = time.time()
    save_tokens(new_tokens)
    print("✓ Access token refreshed")
    return new_tokens

def get_valid_token():
    tokens = load_tokens()
    if not tokens:
        raise Exception("No tokens found — run oauth.py first to login")
    if is_access_token_expired(tokens):
        tokens = refresh_access_token(tokens)
    return tokens["access_token"]