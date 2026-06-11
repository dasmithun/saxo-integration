import os
import base64
import hashlib

def generate_pkce_pair():
    # Generate a random 32-byte code verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()

    # Hash it with SHA-256 to get the code challenge
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    return code_verifier, code_challenge

if __name__ == "__main__":
    verifier, challenge = generate_pkce_pair()
    print("Verifier: ", verifier)
    print("Challenge:", challenge)