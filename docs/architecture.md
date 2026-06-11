# Architecture — Saxo Bank API Integration

## Overview

Python integration with the Saxo Bank OpenAPI for programmatic trading, real-time
market data, and portfolio management. All 6 phases of development are complete.
The system runs against the SIM environment by default. Two URL changes switch it to LIVE.

---

## Environment URLs

| Environment | Base URL | Auth URL | When used |
|---|---|---|---|
| SIM | `https://gateway.saxobank.com/sim/openapi` | `https://sim.logonvalidation.net` | Development (all phases) |
| LIVE | `https://gateway.saxobank.com/openapi` | `https://live.logonvalidation.net` | Production only |

---

## Full module structure

```
saxo-integration/
├── src/
│   ├── api/
│   │   ├── client.py          Base HTTP client — auth, retries, rate limiting
│   │   ├── account.py         Balances, positions, orders, trade history
│   │   ├── instruments.py     Instrument search and UIC lookup
│   │   ├── prices.py          Live bid/ask quotes
│   │   ├── orders.py          Order placement and cancellation
│   │   └── historical.py      OHLCV bars via yfinance (SIM fallback)
│   ├── auth/
│   │   ├── oauth.py           OAuth 2.0 + PKCE browser login flow
│   │   ├── pkce.py            Code verifier/challenge generation
│   │   ├── callback_server.py Local HTTP server for OAuth redirect
│   │   └── token_manager.py   Token storage, expiry, auto-refresh
│   ├── streaming/
│   │   ├── streamer.py        WebSocket client + binary message decoder
│   │   └── poller.py          REST polling fallback for SIM / firewalled networks
│   ├── dashboard.py           Live terminal dashboard
│   └── utils/
│       └── config.py          .env loader — all secrets come from here
├── tests/
│   ├── unit/                  Pure logic tests — no API calls
│   ├── integration/           Live SIM API tests
│   ├── test_connectivity.py   Full endpoint health check
│   ├── test_streaming.py      Streaming with auto-fallback
│   ├── test_historical.py     Historical bar data
│   └── check_cantrade.py      Trading permission check
├── docs/
│   ├── architecture.md        This file
│   ├── risk_register.md       10 risks with mitigations and current status
│   └── go_live_checklist.md   Pre-production checklist
├── conftest.py                pytest sys.path setup
├── requirements.txt
└── .env                       Secrets — gitignored
```

---

## Data flow

```
.env
  └── config.py
        └── SaxoClient (client.py)
              ├── token_manager.py ──→ tokens.json
              │     └── oauth.py ──→ pkce.py
              │                  └── callback_server.py
              ├── AccountAPI (account.py)
              ├── InstrumentsAPI (instruments.py)
              ├── PricesAPI (prices.py)
              ├── OrdersAPI (orders.py)
              └── HistoricalData (historical.py) ──→ yfinance

SaxoStreamer (streamer.py) ──→ WebSocket (LIVE only)
SaxoPoller  (poller.py)   ──→ REST polling (SIM + LIVE)

dashboard.py ──→ AccountAPI + PricesAPI + SaxoPoller + yfinance
```

---

## SaxoClient

Located at `src/api/client.py`. The single HTTP client that all modules use.

- Loads a valid OAuth token automatically on instantiation via `get_valid_token()`
- Sets `Authorization: Bearer {token}` and `Content-Type: application/json` via a
  persistent `requests.Session` — headers sent on every request
- Safety assert: `assert "sim" in base_url` — blocks accidental LIVE usage in development.
  Remove this only when switching to LIVE
- GET: 3-retry loop with exponential back-off on 429 (rate limited) and request timeouts.
  Raises clear exception on 401 (token expired)
- POST: logs full error response body before raising HTTPError
- DELETE: accepts optional `params` dict for query string parameters
- PUT: returns `{"status": "ok"}` on 204 No Content responses
- 10 second timeout on all requests

---

## OAuth 2.0 + PKCE flow

```
Your app                    Saxo auth server           User browser
─────────                   ────────────────           ────────────
generate PKCE pair
build /authorize URL   ───→ sim.logonvalidation.net
                            redirects browser     ───→ login page
                                                  ←─── credentials
                       ←─── auth code (redirect to localhost:8080/callback)
exchange code + verifier ─→ /token endpoint
                       ←─── access_token + refresh_token
save to tokens.json
use access_token on all API calls
auto-refresh via refresh_token before expiry
```

Grant type: Authorization Code with PKCE (S256)
Redirect URI: `http://localhost:8080/callback`
Access token lifetime: 20 minutes
Refresh token lifetime: 1 hour

---

## Saxo entity hierarchy

Understanding this is critical — most API calls require both ClientKey and AccountKey.

```
Partner (your registered app)
  └── Client (the account holder — you)
        └── Account (one client can have multiple accounts)
              ├── Position (open trades)
              └── Order (pending orders)
```

Your SIM account:

| Field | Value |
|---|---|
| UserId | 22367165 |
| ClientId | 22367165 |
| ClientKey | Jif2DtysdsFgm3me1FQqwQ== |
| AccountKey | Jif2DtysdsFgm3me1FQqwQ== |
| Currency | EUR |
| Starting balance | 1,000,000 EUR |
| Account type | Normal / Trial |

---

## Key instrument UICs

UIC (Unique Instrument Code) is Saxo's internal identifier used in all price,
order, streaming, and chart API calls.

| Instrument | UIC | Asset type | Notes |
|---|---|---|---|
| EURUSD | 21 | FxSpot | Default test instrument |
| Apple Inc (NASDAQ) | 211 | Stock | Prices need data subscription on SIM |
| SPY ETF (ARCX) | 36590 | Etf | Prices need data subscription on SIM |
| E-mini NASDAQ-100 Jun 2026 | 52477965 | ContractFutures | Traded in session |

---

## Streaming architecture

Saxo uses a subscription model for real-time data:

1. Connect WebSocket to `wss://gateway.saxobank.com/sim/openapi/streamingws/connect`
2. POST a subscription to a REST endpoint (e.g. `/trade/v1/prices/subscriptions`)
   with the WebSocket `contextid` and a `referenceId`
3. Saxo pushes updates over the WebSocket whenever data changes
4. Each message is binary-encoded: `[8B msg ID][2B ref ID len][ref ID][1B format][4B payload len][JSON]`
5. Messages are matched to callbacks by `referenceId`

WebSocket is not available on SIM (returns 404). `SaxoPoller` provides an identical
callback interface using REST polling as a fallback. The test suite automatically
detects which transport is available and uses the appropriate one.

---

## Order payload requirements

Discovered through testing — these fields are required by Saxo and not in all
documentation examples:

```python
{
    "Uic":           21,
    "AssetType":     "FxSpot",
    "BuySell":       "Buy",
    "Amount":        100000,
    "OrderType":     "Limit",
    "OrderPrice":    1.10,          # required for Limit orders
    "OrderRelation": "StandAlone",  # required — not obvious from docs
    "ManualOrder":   True,
    "AccountKey":    "...",
    "OrderDuration": {              # required — not optional
        "DurationType": "GoodTillCancel"
    }
}
```

---

## Rate limits

- Default: 120 requests per minute per endpoint
- SaxoClient handles 429 with exponential back-off: `sleep(2^attempt)` seconds
- For scripts that loop over multiple instruments, add `time.sleep(0.5)` between calls

---

## Known SIM limitations

| Feature | Status | Workaround |
|---|---|---|
| WebSocket streaming | 404 on SIM | SaxoPoller REST fallback |
| `/chart/v1/charts` | 404 on SIM | yfinance for OHLCV data |
| US stock prices | NoAccess | Requires market data subscription |
| CME futures prices | NoAccess | Requires market data subscription |
| FX prices | Available | Works by default |

---

## Go-live changes required

Two URL changes and remove the safety assert:

`src/utils/config.py`:
```python
SIM_BASE = "https://gateway.saxobank.com/openapi"
```

`src/auth/oauth.py`:
```python
SIM_AUTH_URL  = "https://live.logonvalidation.net/authorize"
SIM_TOKEN_URL = "https://live.logonvalidation.net/token"
```

`src/api/client.py` — remove:
```python
assert "sim" in base_url, "Safety check: switch to LIVE only in Phase 6"
```

See `docs/go_live_checklist.md` for the full pre-production checklist.
