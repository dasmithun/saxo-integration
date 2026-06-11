from src.api.client import SaxoClient

class InstrumentsAPI:
    def __init__(self, client: SaxoClient):
        self.client = client

    def search(self, keyword, asset_type=None, limit=10):
        params = {
            "Keywords":  keyword,
            "$top":      limit,
        }
        if asset_type:
            params["AssetTypes"] = asset_type
        return self.client.get("/ref/v1/instruments", params=params)

    def get_details(self, uic, asset_type):
        result = self.client.get("/ref/v1/instruments/details", params={
            "Uics":      uic,
            "AssetType": asset_type
        })
        return result["Data"][0] if result.get("Data") else None

    def find(self, keyword, asset_type=None):
        result = self.search(keyword, asset_type)
        instruments = result.get("Data", [])
        if not instruments:
            print(f"No instruments found for '{keyword}'")
            return None
        print(f"Found {len(instruments)} instrument(s) for '{keyword}':")
        print(f"{'#':<4} {'Symbol':<12} {'Description':<35} {'Type':<15} {'UIC'}")
        print("-" * 75)
        for i, instr in enumerate(instruments):
            print(
                f"{i+1:<4} "
                f"{instr.get('Symbol',''):<12} "
                f"{instr.get('Description',''):<35} "
                f"{instr.get('AssetType',''):<15} "
                f"{instr.get('Identifier','')}"
            )
        return instruments