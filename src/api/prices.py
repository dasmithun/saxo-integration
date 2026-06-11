from src.api.client import SaxoClient

class PricesAPI:
    def __init__(self, client: SaxoClient):
        self.client = client

    def get_quote(self, uic, asset_type):
        return self.client.get("/trade/v1/infoprices", params={
            "Uic":         uic,
            "AssetType":   asset_type,
            "FieldGroups": "Quote,DisplayAndFormat,InstrumentPriceDetails"
        })

    def get_quotes(self, uics, asset_type):
        return self.client.get("/trade/v1/infoprices/list", params={
            "Uics":        ",".join(str(u) for u in uics),
            "AssetType":   asset_type,
            "FieldGroups": "Quote,DisplayAndFormat"
        })

    def print_quote(self, uic, asset_type):
        q = self.get_quote(uic, asset_type)
        fmt    = q.get("DisplayAndFormat", {})
        quote  = q.get("Quote", {})
        detail = q.get("InstrumentPriceDetails", {})

        bid    = quote.get("Bid", "N/A")
        ask    = quote.get("Ask", "N/A")
        mid    = round((bid + ask) / 2, 6) if isinstance(bid, float) else "N/A"
        spread = round(ask - bid, 6) if isinstance(bid, float) else "N/A"

        print(f"{'Symbol':<12} {fmt.get('Symbol','')}")
        print(f"{'Description':<12} {fmt.get('Description','')}")
        print(f"{'Bid':<12} {bid}")
        print(f"{'Ask':<12} {ask}")
        print(f"{'Mid':<12} {mid}")
        print(f"{'Spread':<12} {spread}")
        print(f"{'Decimals':<12} {fmt.get('Decimals','')}")
        print(f"{'Currency':<12} {fmt.get('Currency','')}")
        return q