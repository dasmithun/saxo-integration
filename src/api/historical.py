import ssl
import urllib.request
import yfinance as yf

# Fix for corporate SSL environments
ssl._create_default_https_context = ssl._create_unverified_context

class HistoricalData:
    UIC_TO_YAHOO = {
        21:    "EURUSD=X",
        211:   "AAPL",
        36590: "SPY",
    }

    def get_bars(self, uic, period="5d", interval="1h"):
        ticker = self.UIC_TO_YAHOO.get(uic)
        if not ticker:
            raise ValueError(f"No Yahoo ticker mapped for UIC {uic}")

        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            print(f"⚠ No data returned for {ticker}")
            return None

        print(f"✓ {ticker} — {len(df)} bars ({interval})")
        print(f"  From: {df.index[0]}")
        print(f"  To:   {df.index[-1]}")
        print(f"\n  Last 3 candles:")
        print(f"  {'Time':<25} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8}")
        print(f"  {'-'*65}")
        for ts, row in df.tail(3).iterrows():
            try:
                o = float(row['Open'].iloc[0])
                h_ = float(row['High'].iloc[0])
                l = float(row['Low'].iloc[0])
                c = float(row['Close'].iloc[0])
            except Exception:
                o, h_, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
            print(f"  {str(ts):<25} {o:>8.4f} {h_:>8.4f} {l:>8.4f} {c:>8.4f}")
        return df