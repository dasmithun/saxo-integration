import time
import truststore
truststore.inject_into_ssl()

import requests
from src.utils.config import SIM_BASE

class SaxoClient:
    def __init__(self, base_url=SIM_BASE, token=None):
        assert "sim" in base_url, "Safety check: switch to LIVE only in Phase 6"
        self.base = base_url

        # Use OAuth token if none provided
        if token is None:
            from src.auth.token_manager import get_valid_token
            token = get_valid_token()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json"
        })

    def get(self, path, params=None, retries=3):
        for attempt in range(retries):
            try:
                r = self.session.get(
                    f"{self.base}{path}",
                    params=params,
                    timeout=10
                )
                if r.status_code == 429:
                    print(f"Rate limited — waiting {2 ** attempt}s...")
                    time.sleep(2 ** attempt)
                    continue
                if r.status_code == 401:
                    raise Exception("Token expired — run python -m src.auth.oauth to re-login")
                r.raise_for_status()
                return r.json()
            except requests.Timeout:
                if attempt == retries - 1:
                    raise
                time.sleep(1)

    def post(self, path, payload=None):
        r = self.session.post(
            f"{self.base}{path}",
            json=payload,
            timeout=10
        )
        if not r.ok:
            print(f"Error response: {r.text}")
        r.raise_for_status()
        return r.json()
    
    def delete(self, path):
        r = self.session.delete(
            f"{self.base}{path}",
            timeout=10
        )
        r.raise_for_status()
        return r.json() if r.text else {"status": "deleted"}
    
    def put(self, path, payload=None):
        r = self.session.put(
            f"{self.base}{path}",
            json=payload,
            timeout=10
        )
        if not r.ok:
            print(f"Error response: {r.text}")
        r.raise_for_status()
        return r.json() if r.text else {"status": "ok"}