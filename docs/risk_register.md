# Risk Register — Saxo Bank API Integration

**Project:** Saxo Bank API Integration
**Owner:** Solo developer
**Last updated:** 2026-06-12
**Project status:** All 6 phases complete

Risk score = Probability (1–5) × Impact (1–5)
🟢 Low (1–5) · 🟡 Medium (6–10) · 🔴 High (11–25)

---

## R01 — 24-hour token expiry during testing

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 1 |
| Impact | 2 |
| Score | 🟢 2 |
| Description | The 24h SIM token from developer.saxo expires and breaks API calls |
| Mitigation | Resolved — OAuth 2.0 with auto-refresh is fully implemented. Tokens refresh automatically before expiry. Only re-login needed when refresh token expires (~1 hour of inactivity) |
| Status | ✅ Resolved — Phase 2 complete |

---

## R02 — Credentials committed to Git

| Field | Detail |
|---|---|
| Category | Security |
| Probability | 1 |
| Impact | 5 |
| Score | 🟡 5 |
| Description | `.env` or `tokens.json` accidentally staged and pushed, exposing API keys |
| Mitigation | Both files are in `.gitignore` and confirmed never committed (verified via `git log -- .env` and `git log -- tokens.json`). Run `git status` before every commit. If credentials are ever exposed, rotate immediately at developer.saxo/openapi/appmanagement |
| Status | ✅ Mitigated — verified clean |

---

## R03 — Saxo SIM environment downtime

| Field | Detail |
|---|---|
| Category | Availability |
| Probability | 2 |
| Impact | 2 |
| Score | 🟢 4 |
| Description | Saxo SIM is unavailable during a dev session |
| Mitigation | Project is complete — SIM downtime no longer blocks development. For future maintenance, Saxo typically schedules downtime Sunday nights UTC. Use yfinance for data work during downtime |
| Status | 🟢 Low risk — project complete |

---

## R04 — Rate limit hits (429 errors)

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 2 |
| Impact | 1 |
| Score | 🟢 2 |
| Description | Rapid API calls trigger Saxo's 120 req/min rate limit |
| Mitigation | SaxoClient has exponential back-off on 429 (sleep 2^attempt seconds). Add `time.sleep(0.5)` in scripts that loop over many instruments |
| Status | ✅ Mitigated in SaxoClient |

---

## R05 — OAuth token scope insufficient (oal: 1F vs 3F)

| Field | Detail |
|---|---|
| Category | Security / Permissions |
| Probability | 2 |
| Impact | 3 |
| Score | 🟢 6 |
| Description | JWT tokens issued with `oal: 1F` (read-only) instead of `oal: 3F` (trading). Caused 403 on order placement during development |
| Mitigation | Resolved by ensuring `OAPI.OP.Trading` is in the account Operations list and the app has Allow Trading enabled. Verified working — full order lifecycle (place, verify, cancel) tested and passing |
| Status | ✅ Resolved — trading confirmed working |

---

## R06 — Wrong ClientKey / AccountKey in API calls

| Field | Detail |
|---|---|
| Category | Data |
| Probability | 1 |
| Impact | 2 |
| Score | 🟢 2 |
| Description | Incorrect keys cause 400/401 errors |
| Mitigation | Keys loaded from `.env` via `config.py`. Never hardcoded. All integration tests verify correct keys are returned from the API |
| Status | ✅ Mitigated — config module in place |

---

## R07 — Chart / historical data unavailable in SIM

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 5 |
| Impact | 1 |
| Score | 🟡 5 |
| Description | `/chart/v1/charts` returns 404 on SIM for all OAuth token types |
| Mitigation | Resolved — `src/api/historical.py` uses yfinance as fallback. Supports EURUSD, Apple, SPY, NQ futures. Map is extensible. Saxo chart endpoint available on LIVE |
| Status | ✅ Resolved — yfinance fallback working |

---

## R08 — WebSocket streaming unavailable on SIM

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 5 |
| Impact | 2 |
| Score | 🟡 10 |
| Description | Saxo's WebSocket endpoint (`/streamingws/connect`) returns 404 on SIM regardless of auth token or URL variant |
| Mitigation | Resolved — `SaxoPoller` provides identical callback interface via REST polling. `test_streaming.py` auto-detects transport and falls back gracefully. WebSocket code is complete and will work on LIVE |
| Status | ✅ Resolved — REST poller fallback working |

---

## R09 — Saxo API breaking changes

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 2 |
| Impact | 3 |
| Score | 🟢 6 |
| Description | Saxo deprecates or changes an endpoint version |
| Mitigation | All API calls use versioned paths (`/v1/`, `/v2/`). Monitor developer.saxo/openapi/releasenotes monthly. Changes are localised to individual modules in `src/api/` |
| Status | 🟡 Ongoing — monitor |

---

## R10 — Accidental LIVE order placement

| Field | Detail |
|---|---|
| Category | Financial |
| Probability | 1 |
| Impact | 5 |
| Score | 🟡 5 |
| Description | Code accidentally points at LIVE and places real orders with real money |
| Mitigation | `SaxoClient.__init__` has `assert "sim" in base_url` that throws immediately if LIVE URL is passed. `OrdersAPI` defaults to `mock=True`. Both must be explicitly changed before any real order can be placed. Remove assert only when intentionally going LIVE after completing `go_live_checklist.md` |
| Status | ✅ Mitigated — double safety locks in place |

---

## Summary

| ID | Risk | Score | Status |
|---|---|---|---|
| R01 | 24h token expiry | 🟢 2 | ✅ Resolved |
| R02 | Credentials in Git | 🟡 5 | ✅ Mitigated |
| R03 | SIM downtime | 🟢 4 | 🟢 Low risk |
| R04 | Rate limit hits | 🟢 2 | ✅ Mitigated |
| R05 | OAuth token scope | 🟢 6 | ✅ Resolved |
| R06 | Wrong API keys | 🟢 2 | ✅ Mitigated |
| R07 | Chart data 404 | 🟡 5 | ✅ Resolved |
| R08 | WebSocket on SIM | 🟡 10 | ✅ Resolved |
| R09 | API breaking changes | 🟢 6 | 🟡 Monitor |
| R10 | Accidental LIVE orders | 🟡 5 | ✅ Mitigated |
