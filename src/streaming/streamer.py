import asyncio
import json
import struct
import threading
import ssl
import websockets
import requests
from src.utils.config import SIM_BASE
from src.auth.token_manager import get_valid_token

SIM_STREAMING_URL = "wss://gateway.saxobank.com/sim/openapi/streamingws/connect"

class SaxoStreamer:
    def __init__(self):
        self.token        = get_valid_token()
        self.context_id   = "saxo_stream_001"
        self.callbacks    = {}
        self._running     = False
        self._ws          = None
        self._loop        = None
        self._thread      = None

    def _decode_message(self, raw):
        # Saxo streaming message format:
        # [8 bytes message id][2 bytes ref id length][ref id][1 byte payload format]
        # [4 bytes payload length][payload]
        messages = []
        offset = 0
        while offset < len(raw):
            msg_id       = struct.unpack_from("<q", raw, offset)[0]; offset += 8
            ref_len      = struct.unpack_from("<H", raw, offset)[0]; offset += 2
            ref_id       = raw[offset:offset+ref_len].decode(); offset += ref_len
            payload_fmt  = raw[offset]; offset += 1
            payload_len  = struct.unpack_from("<i", raw, offset)[0]; offset += 4
            payload      = raw[offset:offset+payload_len]; offset += payload_len
            if payload_fmt == 0:
                data = json.loads(payload.decode())
            else:
                data = payload
            messages.append({"msg_id": msg_id, "ref_id": ref_id, "data": data})
        return messages

    async def _listen(self):
        import ssl
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        url = f"{SIM_STREAMING_URL}?contextid={self.context_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        print(f"Connecting to Saxo streaming...")
        async with websockets.connect(url, ssl=ssl_context, additional_headers=headers) as ws:
            self._ws = ws
            self._running = True
            print("✓ WebSocket connected")
            async for raw in ws:
                if isinstance(raw, bytes):
                    messages = self._decode_message(raw)
                    for msg in messages:
                        ref_id = msg["ref_id"]
                        if ref_id in self.callbacks:
                            self.callbacks[ref_id](msg["data"])
                        else:
                            print(f"  [{ref_id}] {msg['data']}")

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._listen())

    def start(self):
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        import time; time.sleep(2)  # wait for connection

    def stop(self):
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def on(self, ref_id, callback):
        self.callbacks[ref_id] = callback

    def subscribe_prices(self, uic, asset_type, ref_id="price_001"):
        url = f"{SIM_BASE}/trade/v1/prices/subscriptions"
        token = get_valid_token()
        r = requests.post(url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "Arguments": {"Uic": uic, "AssetType": asset_type},
                "ContextId": self.context_id,
                "ReferenceId": ref_id,
            }
        )
        if r.status_code in (200, 201):
            print(f"✓ Subscribed to {asset_type} UIC={uic} → ref_id={ref_id}")
            return r.json()
        else:
            print(f"⚠ Subscription failed: {r.status_code} {r.text[:200]}")
            return None

    def subscribe_orders(self, ref_id="orders_001"):
        from src.utils.config import CLIENT_KEY
        url = f"{SIM_BASE}/port/v1/orders/subscriptions"
        token = get_valid_token()
        r = requests.post(url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "Arguments": {"ClientKey": CLIENT_KEY},
                "ContextId": self.context_id,
                "ReferenceId": ref_id,
            }
        )
        if r.status_code in (200, 201):
            print(f"✓ Subscribed to order updates → ref_id={ref_id}")
            return r.json()
        else:
            print(f"⚠ Order subscription failed: {r.status_code} {r.text[:200]}")
            return None