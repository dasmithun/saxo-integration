# Architecture — Saxo Bank API Integration

## Overview

This project integrates with the Saxo Bank OpenAPI to enable programmatic trading,
market data access, and portfolio management. All development happens against the
SIM (simulation) environment. LIVE is only switched on at Phase 6 go-live.

---

## Environment URLs

| Environment | Base URL | Auth URL | When used |
|---|---|---|---|
| SIM | `https://gateway.saxobank.com/sim/openapi` | `https://sim.logonvalidation.net` | Phases 1–5 |
| LIVE | `https://gateway.saxobank.com/openapi` | `https://live.logonvalidation.net` | Phase 6 only |

---

## Module Structure

```
saxo-integration/
├── src/
│   ├── auth/           # OAuth 2.0 + PKCE (Phase 2)
│   ├── api/
│   │   └── client.py   # SaxoClient — base HTTP wrapper (Phase 1)
│   ├── streaming/      # WebSocket subscriptions (Phase 4)
│   └── utils/
│       └── config.py   # Loads .env variables
├── tests/              # Connectivity and unit tests
├── docs/               # Architecture and reference docs
├── .env                # Secrets — never commit
├── .gitignore
└── requirements.txt
```

---

## SaxoClient

Located at `src/api/client.py`. Responsibilities:

- Sets `Authorization: Bearer {token}` on every request
- Handles HTTP errors: 401 (token expired), 429 (rate limited), 5xx (server errors)
- Retries up to 3 times with exponential back-off on 429 and timeouts
- 10 second timeout on every request

---

## Saxo Entity Hierarchy

Understanding this is critical — most API calls require both ClientKey and AccountKey.

```
Partner (your app)
  └── Client (the trader)
        └── Account (one client can have multiple accounts)
              ├── Position (open trades)
              └── Order (pending orders)
```

Your SIM account details:

| Field | Value |
|---|---|
| UserId | 22367165 |
| ClientId | 22367165 |
| ClientKey | Jif2DtysdsFgm3me1FQqwQ== |
| AccountKey | Jif2DtysdsFgm3me1FQqwQ== |
| Currency | EUR |
| Starting balance | 1,000,000 EUR (SIM) |

---

## Key Instrument Reference

| Instrument | UIC | Asset type |
|---|---|---|
| EURUSD | 21 | FxSpot |

UIC (Unique Instrument Code) is Saxo's internal identifier used in all price,
order, and chart calls.

---

## OAuth Flow (Phase 2)

```
User → Your App → Saxo /authorize → User logs in
     ← Auth code (redirect to localhost:8080/callback)
     → Exchange code for access token + refresh token
     → Use access token in all API calls
     → Auto-refresh before expiry using refresh token
```

Grant type: Authorization Code with PKCE
Redirect URI: `http://localhost:8080/callback`

---

## Known SIM Limitations

| Endpoint | Issue | Workaround |
|---|---|---|
| `/chart/v1/charts` | Returns 404 with 24h token | Revisit in Phase 3 with OAuth token |
| `CanTrade: false` | New SIM accounts start with trading disabled | Resolved once OAuth app is connected |

---

## Rate Limits

- Default: 120 requests/minute per endpoint
- SaxoClient handles 429 with exponential back-off (2^attempt seconds)
- Add `time.sleep(0.5)` between rapid sequential calls during testing

---

## Running the project

```bash
# 1. Activate environment
conda activate saxo

# 2. Run connectivity test
python -m tests.test_connectivity

# 3. Run all tests
python -m pytest tests/ -v
```

---

## Phase progress

| Phase | Focus | Status |
|---|---|---|
| 1 | Foundation & environment | In progress |
| 2 | OAuth 2.0 authentication | Pending |
| 3 | Core API integration | Pending |
| 4 | Streaming (WebSocket) | Pending |
| 5 | Testing & QA | Pending |
| 6 | Go-live | Pending |
