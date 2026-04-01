# Notion Integration

This document explains how the Notion integration works end-to-end: how the user
connects their Notion account once, and how the OpenClaw agent accesses it on every
subsequent request — without ever seeing or storing a raw Notion token itself.

---

## The Two-Phase Model

The integration is split into two completely separate phases with different lifetimes.

```
Phase 1 — One-time setup      Phase 2 — Every agent request
─────────────────────────     ──────────────────────────────
User visits /auth/notion/start
        ↓
Auth0 → Notion consent screen
        ↓
User approves
        ↓
Auth0 stores Notion token      Agent sends user's Auth0 token
in Token Vault forever    →    Auth0 returns Notion token
                               Agent calls Notion API
                               Results returned to user
```

Phase 1 runs once. Phase 2 runs every time the agent needs Notion data.

---

## Phase 1: Connecting Notion (One-Time)

**File:** `src/callback_server.py`

The user visits:
```
https://<your-domain>/auth/notion/start
```

### What happens step by step

**1. `/auth/notion/start`**

`callback_server.py` generates a time-stamped HMAC `state` token for CSRF
protection, then builds an Auth0 authorization URL:

```
https://<AUTH0_DOMAIN>/authorize
  ?response_type=code
  &client_id=<AUTH0_CLIENT_ID>
  &redirect_uri=https://<your-domain>/auth/notion/callback
  &connection=notion
  &scope=openid profile email
  &state=<hmac-state>
```

The user is redirected there immediately (HTTP 302).

**2. Auth0 → Notion consent screen**

Auth0 forwards the user to Notion's OAuth consent screen. The user sees the
standard "Allow this app to access your Notion workspace?" prompt and approves.

**3. Notion → Auth0 (internal)**

Notion sends the authorization code back to Auth0's internal endpoint. Auth0
exchanges it with Notion for an access token + refresh token, and **stores both
inside Token Vault**. Your application code never sees these tokens.

**4. Auth0 → `/auth/notion/callback`**

Auth0 redirects to your callback with its own short-lived `code`:
```
https://<your-domain>/auth/notion/callback?code=<auth0-code>&state=<state>
```

**5. Callback completes the handshake**

`callback_server.py` verifies the `state` (CSRF check), then exchanges the Auth0
`code` for Auth0 tokens via `POST /oauth/token`. This final exchange confirms to
Auth0 that your server received the callback, locking in the Token Vault entry.

Response to the user:
```json
{ "status": "connected", "provider": "Notion" }
```

**Phase 1 is now complete.** The Notion token lives in Token Vault permanently
(auto-refreshed by Auth0 as needed). This flow never needs to run again unless
the user revokes access.

---

## Phase 2: Agent Accessing Notion (Every Request)

**Files:** `src/auth0_vault.py`, `src/notion_mcp_server.py`

When the OpenClaw agent decides it needs Notion data, it invokes one of the MCP
tools registered in `notion_mcp_server.py`. Every tool call follows the same
three-step sequence:

### Step 1 — Token exchange (`auth0_vault.py`)

The tool receives the user's current Auth0 access token from the OpenClaw session
context. It calls `get_notion_token()`, which POSTs an RFC 8693 token exchange
request to Auth0:

```
POST https://<AUTH0_DOMAIN>/oauth/token
{
  "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
  "client_id": "...",
  "client_secret": "...",
  "subject_token": "<user's Auth0 access token>",
  "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
  "requested_token_type": "urn:auth0:params:oauth:token-type:connection",
  "connection": "notion",
  "requested_subject": "<user's sub claim>"
}
```

Auth0 Token Vault looks up the stored Notion token for that user (`requested_subject`)
and returns a fresh Notion access token. If the stored token is expired, Auth0
silently refreshes it first using Notion's refresh token — your code never handles
token refresh logic.

### Step 2 — Notion API call (`notion_mcp_server.py`)

The returned Notion token is passed directly to `notion-client`:

```python
notion = NotionClient(auth=notion_token)
```

The tool then calls the appropriate Notion API method.

### Step 3 — Results returned to agent

The Notion API response is returned as MCP `TextContent` back to OpenClaw, which
passes it to the LLM as tool output.

---

## Available Tools

| Tool | What it does | Required args |
|------|-------------|---------------|
| `search_notion` | Full-text search across all pages and data sources | `user_token`, `query` |
| `query_notion_data_source` | Query a data source with optional filters | `user_token` |
| `read_notion_page` | Retrieve a page's properties and content | `user_token`, `page_id` |
| `create_notion_page` | Create a new page in a data source | `user_token`, `title` |

All tools accept an optional `data_source_id` argument. If omitted, they fall back to
the `NOTION_DATA_SOURCE_ID` environment variable.

> **API version note:** As of Notion API 2025-09-03, the `database` concept was split
> into **databases** (schema/structure) and **data sources** (records). All
> read/write operations now use `data_source_id` — `notion.data_sources.query()` for
> queries and `parent: {type: "data_source_id", ...}` for page creation.
> Requires `notion-client>=3.0.0`.

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1 (once)                                                  │
│                                                                  │
│  User                callback_server.py        Auth0    Notion   │
│   │                        │                     │        │      │
│   │  GET /auth/notion/start│                     │        │      │
│   │───────────────────────>│                     │        │      │
│   │  302 → Auth0 /authorize│                     │        │      │
│   │<───────────────────────│                     │        │      │
│   │                        │  GET /authorize     │        │      │
│   │────────────────────────────────────────────> │        │      │
│   │                        │    redirect to Notion consent       │
│   │<───────────────────────────────────────────────────────────  │
│   │  approve                                              │      │
│   │──────────────────────────────────────────────────────>       │
│   │                        │  code → Auth0 (internal)     │      │
│   │                        │<──────────────────────────────────  │
│   │                        │  Auth0 exchanges + stores in Vault  │
│   │                        │                     │        │      │
│   │  GET /auth/notion/callback?code=...          │        │      │
│   │───────────────────────>│                     │        │      │
│   │                        │  POST /oauth/token  │        │      │
│   │                        │────────────────────>│        │      │
│   │  {"status":"connected"}│                     │        │      │
│   │<───────────────────────│                     │        │      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2 (every agent request)                                   │
│                                                                  │
│  OpenClaw    notion_mcp_server.py  auth0_vault.py  Auth0  Notion │
│     │               │                   │            │      │    │
│     │  tool call    │                   │            │      │    │
│     │  {user_token} │                   │            │      │    │
│     │──────────────>│                   │            │      │    │
│     │               │ get_notion_token()│            │      │    │
│     │               │──────────────────>             │      │    │
│     │               │                   RFC 8693     │      │    │
│     │               │                   POST ──────> │      │    │
│     │               │                   Notion token │      │    │
│     │               │                   <─────────── │      │    │
│     │               │   notion_token    │            │      │    │
│     │               │<──────────────────             │      │    │
│     │               │                                Notion API  │
│     │               │────────────────────────────────────────>   │
│     │               │                               results │    │
│     │               │<────────────────────────────────────────   │
│     │  tool result  │                                       │    │
│     │<──────────────│                                       │    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why Token Vault

The agent never stores or manages Notion credentials directly. This matters because:

- **No token leakage** — Notion tokens never appear in agent memory, logs, or
  prompt context. The agent only ever holds its own Auth0 token.
- **Automatic refresh** — Auth0 handles Notion token expiry transparently. The
  agent always gets a valid token regardless of when it last ran.
- **Revocation** — If a user disconnects Notion from Auth0, Token Vault stops
  returning tokens immediately. No stale credentials linger anywhere.
- **Same pattern for every provider** — Adding Google Calendar or YouTube uses the
  identical Phase 1 flow (one entry in `PROVIDERS`) and the identical Phase 2
  exchange (one new function in `auth0_vault.py`).

---

## Auth0 Dashboard Requirements

Before Phase 1 can run, these must be configured in Auth0:

1. **Authentication → Social → Create Connection → Notion**
   Enable "Token Vault" in the connection's Advanced tab.
2. **Application → Advanced → Grant Types**
   Enable "Token Exchange" and "Authorization Code".
3. **Application → Allowed Callback URLs**
   Add `https://<your-domain>/auth/notion/callback`.
4. Enable **refresh token rotation** on the application.

The `connection` value in `auth0_vault.py` (`"notion"`) must match the Auth0
connection slug exactly — it is case-sensitive.

---

## Environment Variables

| Variable | Used by | Purpose |
|----------|---------|---------|
| `AUTH0_DOMAIN` | all | Your Auth0 tenant domain |
| `AUTH0_CLIENT_ID` | all | Auth0 application client ID |
| `AUTH0_CLIENT_SECRET` | all | Auth0 application client secret |
| `AUTH0_AUDIENCE` | `auth0_vault.py` | Auth0 API identifier for token exchange |
| `BASE_URL` | `callback_server.py` | Public HTTPS URL (e.g. sslip.io address) |
| `STATE_SECRET` | `callback_server.py` | Secret for signing CSRF state tokens |
| `PORT` | `callback_server.py` | Internal port uvicorn listens on (default 8000) |
| `NOTION_DATA_SOURCE_ID` | `notion_mcp_server.py` | Default Notion data source ID for tools |
