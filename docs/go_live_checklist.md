# Go-Live Checklist — Saxo Bank API Integration

**Last updated:** 2026-06-12
**Current environment:** SIM
**Target:** Switch to LIVE when account and compliance requirements are met

---

## Code changes required (3 changes total)

### 1. `src/utils/config.py` — update base URL

```python
# From:
SIM_BASE = "https://gateway.saxobank.com/sim/openapi"

# To:
SIM_BASE = "https://gateway.saxobank.com/openapi"
```

### 2. `src/auth/oauth.py` — update auth URLs

```python
# From:
SIM_AUTH_URL  = "https://sim.logonvalidation.net/authorize"
SIM_TOKEN_URL = "https://sim.logonvalidation.net/token"

# To:
SIM_AUTH_URL  = "https://live.logonvalidation.net/authorize"
SIM_TOKEN_URL = "https://live.logonvalidation.net/token"
```

### 3. `src/api/client.py` — remove safety assert

```python
# Remove this line:
assert "sim" in base_url, "Safety check: switch to LIVE only in Phase 6"
```

### 4. `src/api/orders.py` — confirm mock is off

```python
# Confirm all production order calls use:
orders = OrdersAPI(client, mock=False)
```

---

## Pre go-live checklist

### Credentials
- [ ] Obtain LIVE App Key from developer.saxo → Apps → Create App (LIVE)
- [ ] Obtain LIVE App Secret — copy immediately, shown only once
- [ ] Update `.env` with LIVE credentials under new keys (keep SIM keys for rollback)
- [ ] Register LIVE redirect URI in the new LIVE app
- [ ] Re-run `python -m src.auth.oauth` to get LIVE tokens
- [ ] Confirm `tokens.json` contains a LIVE access token (decode JWT, check `iss` field)

### Account verification
- [ ] `CanTrade: True` confirmed on LIVE account
- [ ] `TradeLevel: FullTradingAndChat` confirmed via `python -m tests.check_cantrade`
- [ ] Sufficient balance/margin confirmed for intended trading
- [ ] Risk limits configured on Saxo LIVE platform
- [ ] All required legal and compliance documents signed with Saxo
- [ ] OpenAPI Access enabled in SaxoTraderGO → Settings → Platform & Trading

### Code verification
- [ ] All 3 URL/assert changes applied
- [ ] `OrdersAPI(mock=False)` confirmed for production paths
- [ ] `SaxoClient` instantiates without errors against LIVE endpoint
- [ ] Run full test suite: `python -m pytest tests/unit/ -v` (unit tests only — no LIVE API calls)
- [ ] Run connectivity test against LIVE: `python -m tests.test_connectivity`
- [ ] Verify EURUSD price returns real bid/ask (not SIM mock data)
- [ ] Verify WebSocket connects: `python -m tests.test_streaming`

### Order testing (small size first)
- [ ] Place one limit order well below market — verify it appears in dashboard
- [ ] Verify order shows in Saxo LIVE platform (cross-check API vs UI)
- [ ] Cancel the test order via API — verify cancellation
- [ ] Place and fill one small market order (minimum size)
- [ ] Verify fill appears in trade history
- [ ] Verify balance updated correctly after fill

### Monitoring setup
- [ ] Dashboard running and showing live LIVE data
- [ ] Token refresh working — monitor for 1 hour, confirm no auth errors
- [ ] Confirm 429 rate limiting handled gracefully under normal usage
- [ ] Set up alert if equity drops below threshold
- [ ] Confirm `tokens.json` is gitignored on LIVE machine

---

## Rollback plan

If anything goes wrong after switching to LIVE:

1. In `src/utils/config.py` — revert to `gateway.saxobank.com/sim/openapi`
2. In `src/auth/oauth.py` — revert to `sim.logonvalidation.net`
3. Re-add the safety assert to `SaxoClient.__init__`
4. Run `python -m src.auth.oauth` to get fresh SIM tokens
5. Confirm dashboard shows SIM balance (1,000,000 EUR)
6. Cancel any open LIVE orders manually via Saxo LIVE platform
7. Review what went wrong before attempting LIVE again

---

## Post go-live monitoring — first 24 hours

- [ ] Token refresh fires automatically at ~19 minute mark — confirm in logs
- [ ] No 429 rate limit errors during normal operation
- [ ] Price feed ticking continuously — confirm in dashboard
- [ ] Open orders match between API and Saxo platform
- [ ] Account balance matches between API and Saxo platform
- [ ] WebSocket streaming delivering ticks (check vs poller)
- [ ] `/chart/v1/charts` endpoint accessible (no longer 404 on LIVE)

---

## Features unlocked on LIVE vs SIM

| Feature | SIM | LIVE |
|---|---|---|
| WebSocket streaming | ❌ 404 | ✅ Available |
| Chart / OHLCV data | ❌ 404 | ✅ Available |
| US stock prices | ❌ NoAccess | ✅ With subscription |
| CME futures prices | ❌ NoAccess | ✅ With subscription |
| FX prices | ✅ | ✅ |
| Order placement | ✅ | ✅ |
| Real P&L | ❌ Simulated | ✅ Real money |

---

## Environment variable template for LIVE `.env`

```
# LIVE credentials
SAXO_LIVE_TOKEN=
SAXO_CLIENT_ID=your-live-client-id
SAXO_ACCOUNT_ID=your-live-account-id
SAXO_ACCOUNT_KEY=your-live-account-key
SAXO_CLIENT_KEY=your-live-client-key
SAXO_APP_KEY=your-live-app-key
SAXO_APP_SECRET=your-live-app-secret
SAXO_REDIRECT_URI=http://localhost:8080/callback

# Keep SIM credentials for rollback
SAXO_SIM_APP_KEY=93a239df382e4091bd27f295c3846d75
SAXO_SIM_ACCOUNT_KEY=Jif2DtysdsFgm3me1FQqwQ==
SAXO_SIM_CLIENT_KEY=Jif2DtysdsFgm3me1FQqwQ==
```
