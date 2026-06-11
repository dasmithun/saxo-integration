# Go-Live Checklist — Saxo Bank API Integration

## Pre go-live (complete before switching to LIVE)

### Credentials
- [ ] Obtain LIVE App Key and Secret from developer.saxo
- [ ] Obtain LIVE API token
- [ ] Store LIVE credentials in .env under separate keys
- [ ] Confirm LIVE redirect URI registered in app management

### Code
- [ ] Remove `assert "sim" in base_url` from SaxoClient (or update for LIVE)
- [ ] Update LIVE_BASE and LIVE_AUTH_URL constants in config.py
- [ ] Set ENVIRONMENT=LIVE in .env
- [ ] Confirm mock=False in OrdersAPI for live trading
- [ ] Test token refresh works against LIVE auth endpoint

### Account
- [ ] CanTrade = True confirmed on LIVE account
- [ ] Sufficient margin/balance confirmed
- [ ] Risk limits set on Saxo platform
- [ ] All legal/compliance docs signed

### Testing
- [ ] Run full test suite: python -m pytest tests/ -v
- [ ] Run connectivity test against LIVE endpoint
- [ ] Place one small test order manually, confirm fills
- [ ] Confirm order cancel works
- [ ] Monitor for 30 mins before full deployment

### Monitoring
- [ ] Dashboard running and showing live data
- [ ] Alert set for token expiry
- [ ] Alert set for API errors > 5 in 60s
- [ ] Runbook accessible offline

---

## Environment switch — one-line change

Open src/utils/config.py and change:

    SIM_BASE = "https://gateway.saxobank.com/sim/openapi"

To:

    LIVE_BASE = "https://gateway.saxobank.com/openapi"

And update SaxoClient to use LIVE_BASE.

Also update auth URLs in src/auth/oauth.py:

    SIM_AUTH_URL  → https://live.logonvalidation.net/authorize
    SIM_TOKEN_URL → https://live.logonvalidation.net/token

---

## Rollback plan

If anything goes wrong after switching to LIVE:

1. Revert SIM_BASE in config.py
2. Revert auth URLs in oauth.py
3. Re-run python -m src.auth.oauth to get fresh SIM token
4. Confirm dashboard shows SIM data
5. Cancel any open LIVE orders manually via Saxo platform

---

## Post go-live monitoring (first 24 hours)

- [ ] Check token refresh fires correctly before expiry
- [ ] Confirm no 429 rate limit errors in logs
- [ ] Verify price feed is ticking continuously
- [ ] Check open orders match Saxo platform
- [ ] Review balance matches Saxo platform