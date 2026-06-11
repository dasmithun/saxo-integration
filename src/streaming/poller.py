import time
import threading
import truststore
truststore.inject_into_ssl()
import requests
from src.auth.token_manager import get_valid_token
from src.utils.config import SIM_BASE

class SaxoPoller:
    """
    REST-based price poller — fallback when WebSocket is blocked.
    Polls Saxo REST API on an interval and fires callbacks on price changes.
    Functionally equivalent to streaming for development purposes.
    """
    def __init__(self, interval=2):
        self.interval    = interval
        self.callbacks   = {}
        self.last_prices = {}
        self._running    = False
        self._thread     = None
        self._subscriptions = []

    def _get_headers(self):
        token = get_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def subscribe_prices(self, uic, asset_type, ref_id=None):
        ref_id = ref_id or f"price_{uic}"
        self._subscriptions.append({
            "uic": uic,
            "asset_type": asset_type,
            "ref_id": ref_id
        })
        print(f"✓ Polling subscription: {asset_type} UIC={uic} → ref_id={ref_id}")

    def on(self, ref_id, callback):
        self.callbacks[ref_id] = callback

    def _poll(self):
        while self._running:
            for sub in self._subscriptions:
                try:
                    r = requests.get(
                        f"{SIM_BASE}/trade/v1/infoprices",
                        headers=self._get_headers(),
                        params={
                            "Uic":         sub["uic"],
                            "AssetType":   sub["asset_type"],
                            "FieldGroups": "Quote,DisplayAndFormat"
                        },
                        timeout=5
                    )
                    if r.status_code == 200:
                        data  = r.json()
                        quote = data.get("Quote", {})
                        bid   = quote.get("Bid")
                        ask   = quote.get("Ask")
                        ref_id = sub["ref_id"]

                        # Only fire callback if price changed
                        last = self.last_prices.get(ref_id)
                        if bid and (last is None or last != bid):
                            self.last_prices[ref_id] = bid
                            if ref_id in self.callbacks:
                                self.callbacks[ref_id]({
                                    "Bid": bid,
                                    "Ask": ask,
                                    "Uic": sub["uic"]
                                })
                except Exception as e:
                    print(f"  ⚠ Poll error: {e}")
            time.sleep(self.interval)

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()
        print(f"✓ Poller started — polling every {self.interval}s")

    def stop(self):
        self._running = False
        print("Poller stopped.")