# Saxo Bank API Integration

A complete Python integration with the Saxo Bank OpenAPI for programmatic trading,
real-time market data, portfolio management, and live order execution. Built and
fully tested against the Saxo SIM environment with 1,000,000 EUR virtual capital.
All 6 phases of development are complete.

---

## What this project can do

- Authenticate with Saxo Bank using OAuth 2.0 + PKCE with automatic token refresh
- Fetch live account balances, open positions, and open orders
- Search any tradeable instrument — FX, Stocks, ETFs, Futures, Options, CFDs
- Get live bid/ask prices with spread for any instrument
- Place market and limit orders with full payload validation
- Cancel open orders programmatically
- Fetch historical OHLCV bar data via yfinance (SIM fallback)
- Stream live price ticks via WebSocket (LIVE) or REST poller (SIM)
- Subscribe to real-time order state change events
- Run a self-refreshing live terminal dashboard
- Handle rate limits, token expiry, and API errors automatically

---

## Quick start

```bash
# 1. Create environment
conda create -n saxo python=3.11
conda activate saxo
pip install -r requirements.txt

# 2. Create .env (see Configuration below)

# 3. Login
python -m src.auth.oauth

# 4. Run dashboard
python -m src.dashboard
```

---

## Configuration

Create `.env` in the project root — never commit this file:

```
SAXO_SIM_TOKEN=your-24h-token-from-developer.saxo
SAXO_CLIENT_ID=22367165
SAXO_ACCOUNT_ID=22367165
SAXO_ACCOUNT_KEY=your-account-key
SAXO_CLIENT_KEY=your-client-key
SAXO_APP_KEY=your-app-key
SAXO_APP_SECRET=your-app-secret
SAXO_REDIRECT_URI=http://localhost:8080/callback
```

Get App Key and Secret from developer.saxo → Apps. Get ClientKey and AccountKey
by calling `/port/v1/accounts/me` after your first login.

---

## Commands

| Command | What it does |
|---|---|
| `python -m src.auth.oauth` | Browser login — saves tokens to tokens.json |
| `python -m src.dashboard` | Live terminal dashboard, refreshes every 5s |
| `python -m tests.test_connectivity` | Verify all endpoints reachable |
| `python -m tests.test_streaming` | Live price ticks via WebSocket or poller |
| `python -m tests.test_historical` | Historical OHLCV bars via yfinance |
| `python -m tests.check_cantrade` | Check CanTrade and TradeLevel permissions |
| `python -m pytest tests/unit/ tests/integration/ -v` | Run all 29 tests |
| `python -m pytest tests/unit/ tests/integration/ -v --cov=src` | Tests + coverage |

---

## Project structure

```
saxo-integration/
├── src/
│   ├── api/
│   │   ├── client.py          Base HTTP client — auth, retries, rate limiting
│   │   ├── account.py         Balances, positions, orders, trade history
│   │   ├── instruments.py     Instrument search and details
│   │   ├── prices.py          Live quotes and bid/ask pricing
│   │   ├── orders.py          Order placement and cancellation
│   │   └── historical.py      OHLCV bars via yfinance
│   ├── auth/
│   │   ├── oauth.py           Full OAuth 2.0 + PKCE login flow
│   │   ├── pkce.py            Code verifier/challenge generation
│   │   ├── callback_server.py Local HTTP server for OAuth redirect
│   │   └── token_manager.py   Token storage, expiry, auto-refresh
│   ├── streaming/
│   │   ├── streamer.py        WebSocket client + binary message decoder
│   │   └── poller.py          REST polling fallback (SIM / firewall)
│   ├── dashboard.py           Live terminal dashboard
│   └── utils/
│       └── config.py          .env loader
├── tests/
│   ├── unit/                  12 pure logic tests — no API calls needed
│   ├── integration/           17 live SIM tests
│   ├── test_connectivity.py   Full endpoint connectivity check
│   ├── test_streaming.py      Streaming with auto WebSocket/poller fallback
│   ├── test_historical.py     yfinance bar data test
│   └── check_cantrade.py      Trading permission check
├── docs/
│   ├── architecture.md        Full system architecture and data flows
│   ├── risk_register.md       10 risks with mitigations and current status
│   └── go_live_checklist.md   Pre-production checklist for LIVE switch
├── conftest.py
├── requirements.txt
└── .env                       Secrets — gitignored, never commit
```

---

## Module reference

### `src/utils/config.py`

Loads all secrets from `.env`. Exports `SIM_BASE`, `TOKEN`, `CLIENT_KEY`,
`ACCOUNT_KEY`, `APP_KEY`, `APP_SECRET`, `SAXO_REDIRECT_URI`. No credentials
are hardcoded anywhere else in the project.

---

### `src/api/client.py` — SaxoClient

Base HTTP client used by every API module.

- Auto-loads a valid OAuth token on startup via token_manager
- Sets `Authorization: Bearer` and `Content-Type` headers on all requests
- Safety assert blocks accidental use of LIVE URL during development
- GET: 3-retry exponential back-off on 429 and timeouts
- POST, DELETE, PUT: logs error body before raising exceptions
- 10 second timeout on all requests

```python
client = SaxoClient()
data = client.get("/root/v1/user")
client.post("/trade/v2/orders", payload={...})
client.delete("/trade/v2/orders/123", params={"AccountKey": "..."})
client.put("/root/v1/sessions/capabilities", payload={...})
```

---

### `src/api/account.py` — AccountAPI

```python
account = AccountAPI(client)
account.get_balance()       # cash, equity, margin, currency
account.get_positions()     # open positions with count
account.get_orders()        # open orders with count
account.get_trade_history() # historical fills
account.summary()           # formatted terminal print
```

---

### `src/api/instruments.py` — InstrumentsAPI

```python
instr = InstrumentsAPI(client)
instr.find("EURUSD", asset_type="FxSpot")      # prints table, returns list
instr.find("Apple", asset_type="Stock")
instr.search("SPY", asset_type="Etf")          # raw API response
instr.get_details(21, "FxSpot")                # full details by UIC
```

Key UICs:

| Instrument | UIC | Asset type |
|---|---|---|
| EURUSD | 21 | FxSpot |
| Apple Inc (NASDAQ) | 211 | Stock |
| SPY ETF | 36590 | Etf |
| E-mini NASDAQ-100 Jun 2026 | 52477965 | ContractFutures |

---

### `src/api/prices.py` — PricesAPI

```python
prices = PricesAPI(client)
prices.print_quote(21, "FxSpot")                    # formatted terminal print
q = prices.get_quote(21, "FxSpot")                  # raw quote object
prices.get_quotes([21, 211], "FxSpot")              # batch quotes
bid = q['Quote']['Bid']
ask = q['Quote']['Ask']
```

Note: FX prices work by default on SIM. US stock and futures prices require a
market data subscription and show `NoAccess` without one.

---

### `src/api/orders.py` — OrdersAPI

`mock=True` by default — prints payload without sending. Set `mock=False` for real orders.

```python
orders = OrdersAPI(client, mock=False)

# Market order
orders.place_order(uic=21, asset_type="FxSpot",
    direction="Buy", amount=100000)

# Limit order
orders.place_order(uic=21, asset_type="FxSpot",
    direction="Buy", amount=100000,
    order_type="Limit", price=1.10,
    duration="GoodTillCancel")

# Cancel
orders.cancel_order(order_id)

# Query
orders.get_open_orders()
orders.get_order_details(order_id)
```

The correct Saxo payload format (discovered through testing) requires
`OrderRelation: StandAlone` and `OrderDuration` — both handled automatically.

---

### `src/api/historical.py` — HistoricalData

Saxo's `/chart/v1/charts` returns 404 on SIM. This module uses yfinance as a
fallback. Add new instruments to `UIC_TO_YAHOO` dict.

```python
h = HistoricalData()
df = h.get_bars(21, period="5d", interval="1h")       # EURUSD 1h
df = h.get_bars(211, period="1mo", interval="1d")     # Apple daily
df = h.get_bars(52477965, period="1d", interval="1m") # NQ 1min
```

---

### `src/auth/pkce.py`

Generates a PKCE pair (code verifier + SHA-256 challenge) required by Saxo's OAuth
implementation. 32 random bytes base64url-encoded. New unique pair per login.

```python
verifier, challenge = generate_pkce_pair()
```

---

### `src/auth/callback_server.py`

Temporary local HTTP server on `localhost:8080` that catches the OAuth redirect from
Saxo after login. Runs in a background thread, waits up to 120 seconds, extracts and
returns the auth code from the callback URL.

---

### `src/auth/oauth.py`

Full OAuth 2.0 Authorization Code + PKCE flow:

1. Generate PKCE pair
2. Build Saxo authorize URL
3. Open browser to Saxo SIM login
4. Start callback server, wait for redirect
5. Exchange auth code for access + refresh tokens
6. Save to tokens.json

```bash
python -m src.auth.oauth
```

---

### `src/auth/token_manager.py`

Handles full token lifecycle. `get_valid_token()` is the main entry point — called
automatically by SaxoClient on every instantiation.

- Access tokens last 20 minutes
- Refresh tokens last 1 hour
- Buffer of 60 seconds — refreshes before expiry
- If refresh token expires, re-run `python -m src.auth.oauth`

```python
from src.auth.token_manager import get_valid_token, save_tokens, load_tokens
token = get_valid_token()  # auto-refreshes if needed
```

---

### `src/streaming/streamer.py` — SaxoStreamer

WebSocket client for real-time data. Decodes Saxo's binary message format:
`[8B msg ID][2B ref ID len][ref ID][1B format][4B payload len][JSON payload]`.

```python
streamer = SaxoStreamer()
streamer.on("price_001", lambda data: print(data))
streamer.start()
streamer.subscribe_prices(uic=21, asset_type="FxSpot", ref_id="price_001")
streamer.subscribe_orders(ref_id="orders_001")
streamer.stop()
```

WebSocket is not available on Saxo SIM (returns 404). Use SaxoPoller for SIM.
Works on LIVE automatically.

---

### `src/streaming/poller.py` — SaxoPoller

REST poller that provides the identical callback interface as SaxoStreamer. Works on
SIM and behind corporate firewalls. Only fires callbacks when price actually changes.

```python
poller = SaxoPoller(interval=2)
poller.on("price_eurusd", lambda data: print(f"Bid: {data['Bid']}"))
poller.subscribe_prices(uic=21, asset_type="FxSpot", ref_id="price_eurusd")
poller.start()
# ... later ...
poller.stop()
```

---

### `src/dashboard.py`

Self-refreshing terminal dashboard. Clears and redraws every 5 seconds.

Sections:
- Account: cash balance, total equity, margin used, position/order counts
- Live prices: EURUSD bid/ask/spread, ticking every 2 seconds
- Futures P&L: NQ real-time P&L from yfinance vs stored open price
- Open orders: OrderId, direction, amount, status
- Open positions: PositionId, direction, asset type, open price, unrealized P&L

```bash
python -m src.dashboard
```

---

## Tests — 29 passing

```bash
python -m pytest tests/unit/ tests/integration/ -v --cov=src
```

### Unit tests (12) — no API calls needed

- `test_pkce.py` — PKCE pair generation, length, SHA-256 hashing, uniqueness
- `test_token_manager.py` — expiry logic with and without buffer seconds
- `test_historical.py` — UIC-to-ticker mapping, error on unknown UIC

### Integration tests (17) — requires valid tokens.json

- `TestAuth` — user endpoint, UserId and ClientId match
- `TestAccount` — balance positive, currency EUR, positions/orders return counts
- `TestInstruments` — EURUSD returns UIC 21, Apple returns results, details correct
- `TestPrices` — bid and ask present, ask > bid, EURUSD in 0.5–2.0 range
- `TestOrders` — mock market and limit orders return simulated, open orders returns count

---

## Saxo entity hierarchy

```
Partner (your app)
  └── Client (the trader)
        └── Account (one client can have multiple)
              ├── Position (open trades)
              └── Order (pending orders)
```

Most API calls require both `ClientKey` and `AccountKey` as parameters.
Both are loaded from `.env` via `config.py`.

---

## Environments

| | SIM | LIVE |
|---|---|---|
| Base URL | gateway.saxobank.com/sim/openapi | gateway.saxobank.com/openapi |
| Auth URL | sim.logonvalidation.net | live.logonvalidation.net |
| When | All development | Go-live only |

---

## Known SIM limitations

## Limitations

### Saxo SIM environment
These resolve automatically when switching to LIVE.

| Limitation | Detail | Workaround |
|---|---|---|
| WebSocket streaming | `/streamingws/connect` returns 404 on SIM | REST poller — working |
| Historical chart data | `/chart/v1/charts` returns 404 on SIM | yfinance fallback — working |
| US stock prices | AAPL, SPY return `NoAccess` without data subscription | yfinance for P&L tracking |
| CME futures prices | NQ returns `NoAccess` without data subscription | yfinance for P&L tracking |
| `CanTrade` flag | Shows `False` despite trading working — misleading session flag | Ignore — `OAPI.OP.Trading` in Operations is what matters |
| Token lifetime | Access token 20 min, refresh token 1 hour | Re-run `python -m src.auth.oauth` after idle |

---

### Corporate network
These resolve by running from a personal network or VPS.

| Limitation | Detail | Workaround |
|---|---|---|
| WebSocket blocked | Corporate firewall blocks WSS | REST poller fallback |
| SSL interception | Corporate proxy intercepts HTTPS | `truststore` + `ssl._create_unverified_context` for yfinance |
| SaxoTraderGO unreachable | Platform UI not accessible on corporate network | Use personal network |

---

### Code — current gaps

| Limitation | Detail | Priority |
|---|---|---|
| Hardcoded open prices | NQ and AAPL open prices hardcoded in `dashboard.py` — update manually per position | 🟡 Medium |
| No persistent position tracking | Dashboard doesn't remember open prices across restarts | 🟡 Medium |
| No stop loss / take profit | Order exits are manual — no automated exit logic | 🟡 Medium |
| Token keepalive | Refresh token expires after 1 hour idle — no background keepalive | 🟡 Medium |
| Single account only | ClientKey/AccountKey hardcoded in `.env` — no multi-account support | 🟢 Low |
| yfinance UIC mapping is manual | `UIC_TO_YAHOO` in `historical.py` must be extended manually per instrument | 🟢 Low |
| No logging | Errors printed to terminal only — no log files or alerting | 🟢 Low |
| `mock=True` by default | `OrdersAPI` defaults to mock — must pass `mock=False` explicitly for real orders | 🟢 Low |

---

### Go-live blockers
Must be resolved before switching to LIVE.

| Blocker | Action |
|---|---|
| LIVE credentials not obtained | Create LIVE app at developer.saxo → obtain new App Key and Secret |
| WebSocket untested on LIVE | Test `python -m tests.test_streaming` from home network before go-live |
| Chart endpoint untested on LIVE | Verify `/chart/v1/charts` works after switching URLs |
| Safety assert must be removed | Delete `assert "sim" in base_url` from `SaxoClient.__init__` |
| No production monitoring | Set up logging, alerting, and uptime monitoring before LIVE |

---

## Go-live (SIM → LIVE)

Two URL changes required. See `docs/go_live_checklist.md` for full checklist.

`src/utils/config.py`:
```python
SIM_BASE = "https://gateway.saxobank.com/openapi"  # remove /sim/
```

`src/auth/oauth.py`:
```python
SIM_AUTH_URL  = "https://live.logonvalidation.net/authorize"
SIM_TOKEN_URL = "https://live.logonvalidation.net/token"
```

Remove `assert "sim" in base_url` from `SaxoClient.__init__`.

---

## Phase history

| Phase | Deliverable | Status |
|---|---|---|
| 1 | Environment, SaxoClient, connectivity | ✅ Complete |
| 2 | OAuth 2.0 + PKCE + token manager | ✅ Complete |
| 3 | Account, instruments, prices, orders, historical | ✅ Complete |
| 4 | WebSocket streamer + REST poller fallback | ✅ Complete |
| 5 | 29 tests passing, unit + integration suites | ✅ Complete |
| 6 | Live dashboard, go-live checklist, live NQ trade | ✅ Complete |
