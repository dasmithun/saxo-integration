from src.api.client import SaxoClient

client = SaxoClient()

# Test 1 — auth
user = client.get("/root/v1/user")
print("✓ UserId:", user["UserId"])

# Test 2 — accounts
accounts = client.get("/port/v1/accounts/me")
print("✓ AccountKey:", accounts["Data"][0]["AccountKey"])

# Test 3 — instrument search
instr = client.get("/ref/v1/instruments", params={
    "AssetTypes": "FxSpot",
    "Keywords": "EURUSD"
})
print("✓ EURUSD UIC:", instr["Data"][0]["Identifier"])

print("\n✅ SaxoClient is working!")