import truststore
truststore.inject_into_ssl()

import requests
from urllib.parse import urlencode
from src.auth.pkce import generate_pkce_pair
from src.auth.callback_server import wait_for_auth_code
from src.utils.config import APP_KEY, APP_SECRET, SAXO_REDIRECT_URI
import webbrowser

SIM_AUTH_URL  = "https://sim.logonvalidation.net/authorize"
SIM_TOKEN_URL = "https://sim.logonvalidation.net/token"

def get_token():
    # 1. Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # 2. Build the login URL
    params = {
        "response_type":         "code",
        "client_id":             APP_KEY,
        "redirect_uri":          SAXO_REDIRECT_URI,
        "code_challenge":        code_challenge,
        "code_challenge_method": "S256",
        "scope":                 "openid trade",
    }
    login_url = SIM_AUTH_URL + "?" + urlencode(params)

    # 3. Open browser and wait for callback
    print("Opening browser for Saxo login...")
    webbrowser.open(login_url)
    print("Waiting for login... (120s timeout)")
    auth_code = wait_for_auth_code()
    print("✓ Auth code received")

    # 4. Exchange auth code for tokens
    response = requests.post(SIM_TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "code":          auth_code,
        "redirect_uri":  SAXO_REDIRECT_URI,
        "client_id":     APP_KEY,
        "client_secret": APP_SECRET,
        "code_verifier": code_verifier,
    })

    response.raise_for_status()
    tokens = response.json()
    print("✓ Tokens received")
    print(f"  Access token expires in: {tokens['expires_in']}s")
    print(f"  Refresh token present:   {'refresh_token' in tokens}")
    from src.auth.token_manager import save_tokens
    save_tokens(tokens)
    return tokens

if __name__ == "__main__":
    tokens = get_token()
    print("\nFull token response:")
    for k, v in tokens.items():
        if k in ("access_token", "refresh_token"):
            print(f"  {k}: {str(v)[:40]}...")
        else:
            print(f"  {k}: {v}")