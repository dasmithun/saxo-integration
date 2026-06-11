import time
from src.streaming.streamer import SaxoStreamer

streamer = SaxoStreamer()

# Register price callback
def on_price(data):
    if isinstance(data, list):
        for item in data:
            quote = item.get("Quote", {})
            bid   = quote.get("Bid", "—")
            ask   = quote.get("Ask", "—")
            print(f"  EURUSD → Bid: {bid}  Ask: {ask}")
    else:
        print(f"  Price update: {data}")

streamer.on("price_001", on_price)

# Start WebSocket connection
streamer.start()

# Subscribe to EURUSD prices
streamer.subscribe_prices(uic=21, asset_type="FxSpot", ref_id="price_001")

# Listen for 30 seconds
print("Listening for price updates for 30 seconds...")
print("-" * 50)
time.sleep(30)

streamer.stop()
print("Done.")