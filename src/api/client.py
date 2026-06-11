import time
import requests
from src.utils.config import SIM_BASE, TOKEN

class SaxoClient:
    def __init__(self, base_url=SIM_BASE, token=TOKEN):
        assert "sim" in base_url, "Safety check: switch to LIVE only in Phase 6"
        self.base = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
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
                    raise Exception("Token expired — get a new 24h token from developer.saxo")
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
        r.raise_for_status()
        return r.json()