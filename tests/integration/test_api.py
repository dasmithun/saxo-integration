import pytest
from src.api.client import SaxoClient
from src.api.account import AccountAPI
from src.api.instruments import InstrumentsAPI
from src.api.prices import PricesAPI
from src.api.orders import OrdersAPI
from src.utils.config import CLIENT_KEY, ACCOUNT_KEY

@pytest.fixture(scope="module")
def client():
    return SaxoClient()

@pytest.fixture(scope="module")
def account(client):
    return AccountAPI(client)

@pytest.fixture(scope="module")
def instruments(client):
    return InstrumentsAPI(client)

@pytest.fixture(scope="module")
def prices(client):
    return PricesAPI(client)

# ── Auth ──────────────────────────────────────────────
class TestAuth:
    def test_user_endpoint(self, client):
        user = client.get("/root/v1/user")
        assert "UserId" in user
        assert user["UserId"] == 22367165

    def test_client_key_matches(self, client):
        user = client.get("/root/v1/user")
        assert user["ClientId"] == 22367165

# ── Account ───────────────────────────────────────────
class TestAccount:
    def test_balance_returns_cash(self, account):
        balance = account.get_balance()
        assert "CashBalance" in balance
        assert balance["CashBalance"] > 0

    def test_balance_currency_is_eur(self, account):
        balance = account.get_balance()
        assert balance["Currency"] == "EUR"

    def test_positions_returns_count(self, account):
        positions = account.get_positions()
        assert "__count" in positions

    def test_orders_returns_count(self, account):
        orders = account.get_orders()
        assert "__count" in orders

    def test_summary_runs_without_error(self, account):
        account.summary()

# ── Instruments ───────────────────────────────────────
class TestInstruments:
    def test_eurusd_search(self, instruments):
        result = instruments.search("EURUSD", asset_type="FxSpot")
        assert result["Data"][0]["Identifier"] == 21

    def test_search_returns_data(self, instruments):
        result = instruments.search("Apple", asset_type="Stock")
        assert len(result["Data"]) > 0

    def test_instrument_details_eurusd(self, instruments):
        detail = instruments.get_details(21, "FxSpot")
        assert detail is not None
        assert detail["Symbol"] == "EURUSD"

    def test_min_trade_size_eurusd(self, instruments):
        detail = instruments.get_details(21, "FxSpot")
        assert detail["MinimumTradeSize"] == 1000.0

# ── Prices ────────────────────────────────────────────
class TestPrices:
    def test_eurusd_quote_has_bid_ask(self, prices):
        q = prices.get_quote(21, "FxSpot")
        quote = q.get("Quote", {})
        assert "Bid" in quote
        assert "Ask" in quote

    def test_eurusd_spread_is_positive(self, prices):
        q = prices.get_quote(21, "FxSpot")
        quote = q.get("Quote", {})
        assert quote["Ask"] > quote["Bid"]

    def test_eurusd_price_is_realistic(self, prices):
        q = prices.get_quote(21, "FxSpot")
        bid = q["Quote"]["Bid"]
        assert 0.5 < bid < 2.0  # EURUSD should always be in this range

# ── Orders (mock) ─────────────────────────────────────
class TestOrders:
    def test_mock_market_order(self, client):
        orders = OrdersAPI(client, mock=True)
        result = orders.place_order(21, "FxSpot", "Buy", 10000)
        assert result["status"] == "simulated"

    def test_mock_limit_order(self, client):
        orders = OrdersAPI(client, mock=True)
        result = orders.place_order(
            211, "Stock", "Buy", 10,
            order_type="Limit", price=280.00
        )
        assert result["status"] == "simulated"

    def test_open_orders_returns_count(self, client):
        orders = OrdersAPI(client, mock=True)
        result = orders.get_open_orders()
        assert "__count" in result