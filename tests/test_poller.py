import time
from src.streaming.poller import SaxoPoller

poller = SaxoPoller(interval=2)

tick_count = 0

def on_price(data):
    global tick_count
    tick_count += 1
    print(f"  [{tick_count}] EURUSD → Bid: {data['Bid']}  Ask: {data['Ask']}")

poller.on("price_eurusd", on_price)
poller.subscribe_prices(uic=21, asset_type="FxSpot", ref_id="price_eurusd")
poller.start()

print("Listening for price updates for 30 seconds...")
print("-" * 50)
time.sleep(30)

poller.stop()
print(f"\nTotal price updates received: {tick_count}")