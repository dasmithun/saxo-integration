import time
from src.streaming.streamer import SaxoStreamer
from src.streaming.poller import SaxoPoller

tick_count = 0

def on_price(data):
    global tick_count
    tick_count += 1
    if isinstance(data, list):
        for item in data:
            quote = item.get("Quote", {})
            print(f"  [{tick_count}] EURUSD → Bid: {quote.get('Bid','—')}  Ask: {quote.get('Ask','—')}")
    else:
        print(f"  [{tick_count}] EURUSD → Bid: {data.get('Bid','—')}  Ask: {data.get('Ask','—')}")

# Try WebSocket first
streamer = SaxoStreamer()
streamer.on("price_001", on_price)
streamer.start()
time.sleep(1)

# Fall back to poller if WebSocket unavailable
if not streamer._running:
    print("Falling back to REST poller...")
    streamer = SaxoPoller(interval=2)
    streamer.on("price_001", on_price)

# Subscribe and start (order matters)
streamer.subscribe_prices(uic=21, asset_type="FxSpot", ref_id="price_001")

if isinstance(streamer, SaxoPoller):
    streamer.start()

print("Listening for 20 seconds...")
print("-" * 50)
time.sleep(20)
streamer.stop()
print(f"\nTotal ticks: {tick_count}")