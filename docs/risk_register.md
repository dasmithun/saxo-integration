# Risk Register — Saxo Bank API Integration

**Project:** Saxo Bank API Integration  
**Owner:** Solo developer  
**Last updated:** 2026-06-11  

Risk score = Probability (1–5) × Impact (1–5)  
🟢 Low (1–5) · 🟡 Medium (6–10) · 🔴 High (11–25)

---

## R01 — 24-hour token expiry during testing

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 4 |
| Impact | 3 |
| Score | 🟡 12 |
| Description | The 24h SIM token from developer.saxo expires and breaks all test calls mid-session |
| Mitigation | Set a calendar reminder 23h after getting each token. Keep the token page bookmarked: developer.saxo/openapi/token. Phase 2 (OAuth) eliminates this risk permanently |
| Status | Active until Phase 2 complete |

---

## R02 — Credentials committed to Git

| Field | Detail |
|---|---|
| Category | Security |
| Probability | 2 |
| Impact | 5 |
| Score | 🔴 10 |
| Description | `.env` file accidentally staged and pushed, exposing API keys and secrets on GitHub |
| Mitigation | `.env` is in `.gitignore`. Run `git status` before every commit — `.env` must never appear. If it ever does appear, rotate keys immediately in the Saxo app management portal |
| Status | Mitigated — verify before every commit |

---

## R03 — Saxo SIM environment downtime

| Field | Detail |
|---|---|
| Category | Availability |
| Probability | 2 |
| Impact | 3 |
| Score | 🟢 6 |
| Description | Saxo SIM is down during a planned dev session, blocking all API testing |
| Mitigation | Check status at developer.saxo before long sessions. Saxo typically does maintenance Sunday nights UTC. Use this time for documentation, architecture, or offline code writing |
| Status | Low risk — monitor |

---

## R04 — Rate limit hits (429 errors) during rapid testing

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 3 |
| Impact | 2 |
| Score | 🟢 6 |
| Description | Rapid sequential API calls during testing trigger Saxo's 120 req/min rate limit |
| Mitigation | SaxoClient already has exponential back-off on 429. Add `time.sleep(0.5)` between calls in test scripts that loop over multiple instruments |
| Status | Mitigated in SaxoClient |

---

## R05 — OAuth implementation complexity (Phase 2 blocker)

| Field | Detail |
|---|---|
| Category | Technical |
| Probability | 3 |
| Impact | 4 |
| Score | 🟡 12 |
| Description | OAuth 2.0 + PKCE is non-trivial to implement solo. Mistakes here block all of Phase 3 onwards |
| Mitigation | Use Saxo's tutorial and the interactive portal to test each step before coding. Build the local callback server first, test the redirect manually, then automate. Don't rush this phase |
| Status | Pending — Phase 2 |

---

## R06 — Wrong ClientKey / AccountKey in API calls

| Field | Detail |
|---|---|
| Category | Data |
| Probability | 3 |
| Impact | 3 |
| Score | 🟡 9 |
| Description | Passing wrong or hardcoded keys causes 400/401 errors that are hard to debug |
| Mitigation | Keys are stored in `.env` and loaded via `config.py`. Never hardcode keys in any Python file. If you see `400 Bad Request`, always check ClientKey and AccountKey first |
| Status | Mitigated via config module |

---

## R07 — Chart / historical data unavailable in SIM

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 4 |
| Impact | 2 |
| Score | 🟡 8 |
| Description | `/chart/v1/charts` returns 404 with 24h token in SIM — confirmed in Phase 1 testing |
| Mitigation | Deferred to Phase 3. Will retry with full OAuth token. If still unavailable, use alternative data source (e.g. Yahoo Finance via `yfinance`) for backtesting only |
| Status | Known issue — deferred to Phase 3 |

---

## R08 — Scope creep (adding features mid-project)

| Field | Detail |
|---|---|
| Category | Scope |
| Probability | 3 |
| Impact | 3 |
| Score | 🟡 9 |
| Description | Temptation to add features (options, algo orders, UI) before core integration is stable |
| Mitigation | Strictly follow the phase plan. Log new ideas in a `backlog.md` file — don't implement until Phase 3 core is complete and tested |
| Status | Active — discipline required |

---

## R09 — Saxo API breaking changes

| Field | Detail |
|---|---|
| Category | API / Technical |
| Probability | 2 |
| Impact | 4 |
| Score | 🟡 8 |
| Description | Saxo deprecates or changes an endpoint version, breaking existing integration code |
| Mitigation | Monitor the Saxo release notes page: developer.saxo/openapi/releasenotes. All API calls in `src/api/` use versioned paths (e.g. `/v1/`, `/v2/`) — changes are localised to one file |
| Status | Low risk — monitor monthly |

---

## R10 — LIVE trading with SIM code (Phase 6)

| Field | Detail |
|---|---|
| Category | Financial |
| Probability | 2 |
| Impact | 5 |
| Score | 🔴 10 |
| Description | Accidentally pointing the client at LIVE environment while testing could trigger real orders |
| Mitigation | `SaxoClient` defaults to `SIM_BASE` from config. LIVE URL is never set until Phase 6. Add an `ENVIRONMENT=SIM` variable to `.env` and assert it in the client constructor during development |
| Status | Pending — enforce in Phase 6 switch |

---

## Summary

| ID | Risk | Score | Status |
|---|---|---|---|
| R01 | 24h token expiry | 🟡 12 | Active |
| R02 | Credentials in Git | 🔴 10 | Mitigated |
| R03 | SIM downtime | 🟢 6 | Monitor |
| R04 | Rate limit hits | 🟢 6 | Mitigated |
| R05 | OAuth complexity | 🟡 12 | Pending Phase 2 |
| R06 | Wrong API keys | 🟡 9 | Mitigated |
| R07 | Chart data 404 | 🟡 8 | Deferred Phase 3 |
| R08 | Scope creep | 🟡 9 | Active |
| R09 | API breaking changes | 🟡 8 | Monitor |
| R10 | LIVE env accident | 🔴 10 | Pending Phase 6 |
