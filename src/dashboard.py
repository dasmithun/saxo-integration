import time
import os
import truststore
truststore.inject_into_ssl()

from src.api.client import SaxoClient
from src.api.account import AccountAPI
from src.api.prices import PricesAPI
from src.api.instruments import InstrumentsAPI
from src.streaming.poller import SaxoPoller

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def run_dashboard(refresh=5):
    client      = SaxoClient()
    account     = AccountAPI(client)
    prices      = PricesAPI(client)
    instruments = InstrumentsAPI(client)

    # Start price poller
    poller = SaxoPoller(interval=2)
    latest_prices = {}

    def on_eurusd(data):
        latest_prices["EURUSD"] = data

    poller.on("price_eurusd", on_eurusd)
    poller.subscribe_prices(uic=21, asset_type="FxSpot", ref_id="price_eurusd")
    poller.start()

    print("Starting dashboard... (press Ctrl+C to exit)")
    time.sleep(2)

    try:
        while True:
            clear()
            now = time.strftime("%Y-%m-%d %H:%M:%S")

            # Header
            print("=" * 55)
            print(f"  SAXO BANK — LIVE DASHBOARD          {now}")
            print("=" * 55)

            # Account summary
            try:
                balance   = account.get_balance()
                positions = account.get_positions()
                orders    = account.get_orders()

                print(f"\n  {'ACCOUNT'}")
                print(f"  {'─'*50}")
                print(f"  Cash balance   : {balance['CashBalance']:>15,.2f} {balance['Currency']}")
                print(f"  Total equity   : {balance['TotalValue']:>15,.2f} {balance['Currency']}")
                print(f"  Margin used    : {balance.get('MarginUsedByCurrentPositions', 0):>15,.2f} {balance['Currency']}")
                print(f"  Open positions : {positions['__count']:>15}")
                print(f"  Open orders    : {orders['__count']:>15}")
            except Exception as e:
                print(f"  ⚠ Account error: {e}")

            # Live prices
            print(f"\n  {'LIVE PRICES'}")
            print(f"  {'─'*50}")
            if "EURUSD" in latest_prices:
                p = latest_prices["EURUSD"]
                bid = p.get("Bid", "—")
                ask = p.get("Ask", "—")
                spread = round(ask - bid, 5) if isinstance(bid, float) else "—"
                print(f"  EURUSD         :  Bid {bid:<10}  Ask {ask:<10}  Spread {spread}")
            else:
                print(f"  EURUSD         :  waiting for tick...")

            # Open orders detail
            if orders["__count"] > 0:
                print(f"\n  {'OPEN ORDERS'}")
                print(f"  {'─'*50}")
                for o in orders.get("Data", []):
                    print(f"  {o.get('OrderId')}  {o.get('BuySell',''):<5}  {o.get('Amount',''):<10}  {o.get('Status','')}")

            # Open positions detail
            if positions["__count"] > 0:
                print(f"\n  {'OPEN POSITIONS'}")
                print(f"  {'─'*50}")
                for p in positions.get("Data", []):
                    pnl = p.get("PositionBase", {}).get("UnrealizedPnl", 0)
                    print(f"  {p.get('PositionId')}  PnL: {pnl:>10,.2f}")

            print(f"\n  {'─'*50}")
            print(f"  Refreshing every {refresh}s  |  Ctrl+C to exit")
            time.sleep(refresh)

    except KeyboardInterrupt:
        poller.stop()
        print("\n\nDashboard stopped.")

if __name__ == "__main__":
    run_dashboard()