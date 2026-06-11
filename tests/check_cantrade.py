from src.api.client import SaxoClient

client = SaxoClient()
user = client.get("/root/v1/user")

can_trade    = user["AccessRights"]["CanTrade"]
trade_level  = None

# Also check session capabilities
caps = client.get("/root/v1/sessions/capabilities")
trade_level = caps.get("TradeLevel")

print(f"CanTrade     : {can_trade}")
print(f"TradeLevel   : {trade_level}")

if can_trade:
    print("\n✅ Trading enabled — set mock=False in OrdersAPI")
else:
    print("\n⏳ Trading not yet enabled — orders will be rejected with 403")