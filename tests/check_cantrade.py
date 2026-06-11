from src.api.client import SaxoClient

client = SaxoClient()
user  = client.get("/root/v1/user")
caps  = client.get("/root/v1/sessions/capabilities")
ops   = user.get("Operations", [])

print("=== Trading Permission Summary ===")
print(f"CanTrade flag      : {user['AccessRights']['CanTrade']}")
print(f"TradeLevel         : {caps.get('TradeLevel')}")
print(f"OAPI.OP.Trading    : {'✅ Present' if 'OAPI.OP.Trading' in ops else '❌ Missing'}")
print(f"TakeTradeSession   : {'✅' if 'OAPI.OP.TakeTradeSession' in ops else '❌'}")
print(f"TakePriceSession   : {'✅' if 'OAPI.OP.TakePriceSession' in ops else '❌'}")
print()
if "OAPI.OP.Trading" in ops:
    print("✅ You CAN place orders — OAPI.OP.Trading is present")
    print("   CanTrade: False is a session flag, not a trading block")
else:
    print("❌ Trading not available — OAPI.OP.Trading missing from Operations")