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

            # Futures P&L tracker
            print(f"\n  {'FUTURES P&L'}")
            print(f"  {'─'*50}")
            try:
                import yfinance as yf
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                nq = yf.download("NQ=F", period="1d", interval="1m", progress=False)
                if not nq.empty:
                    try:
                        current = float(nq['Close'].iloc[-1].iloc[0])
                    except:
                        current = float(nq['Close'].iloc[-1])
                    open_price = 28888.0
                    points     = current - open_price
                    pnl_usd    = points * 20
                    emoji      = "🟢" if pnl_usd > 0 else "🔴"
                    print(f"  NQM6  Open: {open_price:>10,.2f}  "
                        f"Current: {current:>10,.2f}  "
                        f"P&L: ${pnl_usd:>+8,.2f}  {emoji}")
            except Exception as e:
                print(f"  ⚠ NQ data unavailable: {e}")

            # AAPL P&L tracker
            print(f"\n  {'STOCKS P&L'}")
            print(f"  {'─'*50}")
            try:
                import yfinance as yf
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                aapl = yf.download("AAPL", period="1d", interval="1m", progress=False)
                if not aapl.empty:
                    try:
                        current = float(aapl['Close'].iloc[-1].iloc[0])
                    except:
                        current = float(aapl['Close'].iloc[-1])
                    open_price = 296.14
                    pnl        = (current - open_price) * 1
                    ret        = ((current - open_price) / open_price) * 100
                    emoji      = "🟢" if pnl > 0 else "🔴"
                    print(f"  AAPL  Open: ${open_price:.2f}  "
                        f"Current: ${current:.2f}  "
                        f"P&L: ${pnl:+.2f}  "
                        f"({ret:+.2f}%)  {emoji}")
            except Exception as e:
                print(f"  ⚠ AAPL data unavailable: {e}")

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
                    base     = p.get("PositionBase", {}) 
                    view     = p.get("PositionView", {})
                    pnl      = view.get("UnrealizedPnl", 0) or base.get("UnrealizedPnl", 0)
                    amount   = base.get("Amount", "")
                    direction = base.get("BuySell", "")
                    asset    = base.get("AssetType", "")
                    open_px  = base.get("OpenPrice", "")
                    print(f"  {p.get('PositionId')}  {direction:<5}  {amount:<6}  "
                        f"{asset:<20}  Open: {open_px:<10}  PnL: {pnl:>10,.2f}")
        
            print(f"\n  {'─'*50}")
            print(f"  Refreshing every {refresh}s  |  Ctrl+C to exit")
            time.sleep(refresh)

    except KeyboardInterrupt:
        poller.stop()
        print("\n\nDashboard stopped.")

if __name__ == "__main__":
    run_dashboard()