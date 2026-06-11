from src.api.client import SaxoClient
from src.utils.config import CLIENT_KEY, ACCOUNT_KEY

class AccountAPI:
    def __init__(self, client: SaxoClient):
        self.client = client

    def get_balance(self):
        return self.client.get("/port/v1/balances", params={
            "ClientKey":  CLIENT_KEY,
            "AccountKey": ACCOUNT_KEY
        })

    def get_positions(self):
        return self.client.get("/port/v1/positions", params={
            "ClientKey":  CLIENT_KEY,
            "AccountKey": ACCOUNT_KEY
        })

    def get_orders(self):
        return self.client.get("/port/v1/orders", params={
            "ClientKey":  CLIENT_KEY,
            "AccountKey": ACCOUNT_KEY
        })

    def get_trade_history(self):
        return self.client.get("/port/v1/historicalorders", params={
            "ClientKey":  CLIENT_KEY,
            "AccountKey": ACCOUNT_KEY
        })

    def summary(self):
        balance   = self.get_balance()
        positions = self.get_positions()
        orders    = self.get_orders()

        print("=" * 50)
        print("ACCOUNT SUMMARY")
        print("=" * 50)
        print(f"Cash balance:   {balance['CashBalance']} {balance['Currency']}")
        print(f"Total equity:   {balance['TotalValue']}")
        print(f"Margin used:    {balance.get('MarginUsedByCurrentPositions', 0)}")
        print(f"Open positions: {positions['__count']}")
        print(f"Open orders:    {orders['__count']}")
        print("=" * 50)