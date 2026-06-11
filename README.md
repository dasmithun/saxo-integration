# Saxo Bank API Integration

Python integration with the Saxo Bank OpenAPI for programmatic trading,
market data, and portfolio management.

## Setup

### Requirements
- Python 3.11+
- Conda (recommended)
- Saxo Bank developer account: developer.saxo

### Installation

    conda create -n saxo python=3.11
    conda activate saxo
    pip install -r requirements.txt

### Configuration

Create a .env file in the project root:

    SAXO_SIM_TOKEN=your-24h-token
    SAXO_CLIENT_ID=your-client-id
    SAXO_ACCOUNT_ID=your-account-id
    SAXO_ACCOUNT_KEY=your-account-key
    SAXO_CLIENT_KEY=your-client-key
    SAXO_APP_KEY=your-app-key
    SAXO_APP_SECRET=your-app-secret
    SAXO_REDIRECT_URI=http://localhost:8080/callback

### Authentication

Run OAuth login (required before any API call):

    python -m src.auth.oauth

This opens a browser, logs you in, and saves tokens to tokens.json.
Tokens auto-refresh — you only need to re-run this if the refresh token expires (~1 hour).

## Usage

### Run dashboard

    python -m src.dashboard

### Run tests

    python -m pytest tests/unit/ tests/integration/ -v

### Run connectivity test

    python -m tests.test_connectivity

## Project structure

    src/
    ├── auth/           OAuth 2.0 + PKCE + token manager
    ├── api/            REST API modules (account, instruments, prices, orders)
    ├── streaming/      WebSocket streamer + REST poller fallback
    └── utils/          Config loader

    tests/
    ├── unit/           Pure unit tests (no API calls)
    └── integration/    Live SIM API tests

    docs/
    ├── architecture.md
    ├── risk_register.md
    └── go_live_checklist.md

## Environment

| Environment | Base URL | When |
|---|---|---|
| SIM | gateway.saxobank.com/sim/openapi | Development |
| LIVE | gateway.saxobank.com/openapi | Phase 6 only |

## Known limitations (SIM)

| Issue | Status |
|---|---|
| CanTrade = False | Pending Saxo account verification |
| Chart endpoint 404 | SIM limitation — works on LIVE |
| US stock prices NoAccess | SIM data subscription needed |
| WebSocket blocked | Corporate firewall — works on home network |