from src.api.client import SaxoClient
from src.utils.config import ACCOUNT_KEY, CLIENT_KEY

class OrdersAPI:
    def __init__(self, client: SaxoClient, mock=True):
        self.client = client
        self.mock   = mock

    def place_order(self, uic, asset_type, direction, amount, order_type="Market", price=None):
        payload = {
            "Uic":          uic,
            "AssetType":    asset_type,
            "BuySell":      direction,
            "Amount":       amount,
            "OrderType":    order_type,
            "ManualOrder":  True,
            "AccountKey":   ACCOUNT_KEY,
        }
        if order_type == "Limit" and price:
            payload["Price"] = price
            payload["OrderDuration"] = {"DurationType": "DayOrder"}

        if self.mock:
            print(f"[MOCK] Order would be placed:")
            for k, v in payload.items():
                print(f"  {k:<20} {v}")
            return {"MockOrderId": "MOCK-001", "status": "simulated"}

        return self.client.post("/trade/v2/orders", payload=payload)

    def cancel_order(self, order_id):
        if self.mock:
            print(f"[MOCK] Would cancel order: {order_id}")
            return {"status": "simulated"}

        return self.client.delete(f"/trade/v2/orders/{order_id}/{ACCOUNT_KEY}")

    def get_open_orders(self):
        return self.client.get("/port/v1/orders", params={
            "ClientKey":  CLIENT_KEY,
            "AccountKey": ACCOUNT_KEY
        })

    def get_order_details(self, order_id):
        orders = self.get_open_orders()
        for o in orders.get("Data", []):
            if o.get("OrderId") == order_id:
                return o
        return None