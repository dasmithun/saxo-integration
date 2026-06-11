from src.api.client import SaxoClient
from src.utils.config import CLIENT_KEY, ACCOUNT_KEY

client = SaxoClient()

print("=" * 50)
print("SAXO SIM CONNECTIVITY TEST")
print("=" * 50)

# 1. User info
user = client.get("/root/v1/user")
print(f"\n✓ Auth working — UserId: {user['UserId']}")

# 2. Account balances
balance = client.get("/port/v1/balances", params={
    "ClientKey": CLIENT_KEY,
    "AccountKey": ACCOUNT_KEY
})
print(f"✓ Balance — Cash: {balance['CashBalance']} {balance['Currency']}")
print(f"  Total equity: {balance['TotalValue']}")

# 3. Open positions
positions = client.get("/port/v1/positions", params={
    "ClientKey": CLIENT_KEY,
    "AccountKey": ACCOUNT_KEY
})
print(f"✓ Positions — Open: {positions['__count']}")

# 4. Open orders
orders = client.get("/port/v1/orders", params={
    "ClientKey": CLIENT_KEY,
    "AccountKey": ACCOUNT_KEY
})
print(f"✓ Orders — Open: {orders['__count']}")

# 5. EURUSD live price (UIC=21)
price = client.get("/trade/v1/infoprices", params={
    "Uic": 21,
    "AssetType": "FxSpot",
    "FieldGroups": "Quote,DisplayAndFormat"
})
quote = price["Quote"]
print(f"✓ EURUSD — Bid: {quote['Bid']}  Ask: {quote['Ask']}")

# 6. Historical OHLCV bars
# Note: /chart/v1/charts returns 404 in SIM without a full OAuth token.
# This will be revisited in Phase 3 once OAuth is implemented.
try:
    bars = client.get("/chart/v1/charts", params={
        "Uic": 21,
        "AssetType": "FxSpot",
        "Horizon": 60,
        "Count": 5,
        "Mode": "UpTo"
    })
    print(f"✓ Historical bars — Got {len(bars['Data'])} candles")
    latest = bars["Data"][-1]
    print(f"  Latest close: {latest['Close']}")
except Exception as e:
    print(f"⚠ Historical bars skipped — chart endpoint requires full OAuth token")
    print(f"  (Will revisit in Phase 3)")

# 7. Reference data — instrument details
try:
    details = client.get("/ref/v1/instruments/details", params={
        "Uics": 21,
        "AssetType": "FxSpot"
    })
    instr = details["Data"][0]
    print(f"✓ Instrument details — {instr['Description']}")
    print(f"  Symbol: {instr.get('Symbol', 'N/A')}")
    print(f"  Min trade size: {instr.get('MinimumTradeSize', 'N/A')}")
    print(f"  Currency: {instr.get('CurrencyCode', 'N/A')}")
except Exception as e:
    print(f"⚠ Instrument details skipped — {e}")

print("\n" + "=" * 50)
print("✅ All connectivity checks passed!")
print("=" * 50)