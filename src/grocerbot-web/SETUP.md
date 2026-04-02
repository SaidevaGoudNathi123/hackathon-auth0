# PlanBot Setup Guide — For Teammates

This guide walks you through setting up the PlanBot app locally with Auth0 Token Vault + Spotify integration.

## Prerequisites
- Node.js 18+
- A Spotify Premium account
- Access to the Auth0 Dashboard (ask Saideva for credentials)

## 1. Clone & Install

```bash
git clone https://github.com/SaidevaGoudNathi123/hackathon-auth0.git
cd hackathon-auth0/src/grocerbot-web
npm install
```

## 2. Environment Variables

Copy the example and fill in your values:

```bash
cp .env.local.example .env.local
```

Required variables in `.env.local`:
```
APP_BASE_URL=http://localhost:3000
AUTH0_DOMAIN=dev-zkp5ir8w8baqr65u.us.auth0.com
AUTH0_CLIENT_ID=7KolcPclgklw1goyMg8TpoQ5I2QY2Ogq
AUTH0_CLIENT_SECRET=<ask Saideva — never commit this>
AUTH0_SECRET=<any random 32+ char hex string — run: openssl rand -hex 32>
OPENAI_API_KEY=<your OpenAI key from platform.openai.com>
```

## 3. Auth0 Dashboard Setup (already done — reference only)

These steps were already completed for the shared Auth0 tenant. Listed here so you understand the architecture.

### a) Spotify Social Connection
1. Auth0 Dashboard > Authentication > Social > Spotify
2. Purpose: **"Authentication and Connected Accounts for Token Vault"**
3. Additional scopes: `user-modify-playback-state, user-read-playback-state, playlist-read-private`
4. Client ID + Secret from Spotify Developer Dashboard

### b) Spotify Developer App
1. Go to https://developer.spotify.com/dashboard
2. App redirect URI: `https://dev-zkp5ir8w8baqr65u.us.auth0.com/login/callback`

### c) Auth0 Application (PlanBot)
1. Auth0 Dashboard > Applications > PlanBot
2. Allowed Callback URLs: `http://localhost:3000/auth/callback`
3. Allowed Logout URLs: `http://localhost:3000`
4. Grant Types enabled: Authorization Code, Refresh Token, Client Credentials, **Token Vault**

### d) Management API Access
1. Auth0 Dashboard > Applications > APIs > Auth0 Management API > Application Access
2. PlanBot: Client Access = AUTHORIZED
3. Permissions granted: `read:users`, `read:user_idp_tokens`

## 4. Run the App

```bash
npm run dev
```

Open http://localhost:3000

## 5. First-Time Login

**IMPORTANT:** Log in using **"Continue with Spotify"** (NOT email/password).

This creates your Auth0 user with a Spotify identity attached, which includes the access_token that PlanBot uses to control your Spotify.

## 6. Test It

1. Open Spotify on your phone or computer and play any song for 1 second (this registers the device)
2. In PlanBot, ask: "What's currently playing on Spotify?"
3. Try: "Play some lofi music"
4. Try: "Pause the music"

## Architecture Overview

```
User -> PlanBot (Next.js) -> OpenAI GPT-4o-mini (with tools)
                                    |
                          Tool: playPlaylist / getNowPlaying / togglePlayback
                                    |
                          Auth0 Management API (get Spotify access_token)
                                    |
                          Spotify Web API (play, pause, search)
```

### How Token Flow Works
1. User logs in via "Continue with Spotify" on Auth0
2. Auth0 stores Spotify access_token + refresh_token on the user's identity
3. When a Spotify tool is called, PlanBot:
   - Gets a Management API token (client_credentials grant)
   - Fetches the user's identities from Management API
   - Extracts the Spotify access_token from the spotify connection identity
   - Calls Spotify Web API with that token

### Key Files
| File | What it does |
|------|-------------|
| `src/app/api/chat/route.ts` | Main chat API — OpenAI + Spotify tools |
| `src/lib/auth0.ts` | Auth0 client config |
| `src/components/ChatBox.tsx` | Chat UI component |
| `src/app/page.tsx` | Main page with login + chat |
| `src/app/api/connect-spotify/route.ts` | Redirect to Spotify login |

### For Adding Google Calendar / Notion
Follow the same pattern:
1. Create social connection in Auth0 (Google / Notion)
2. Set purpose to "Authentication and Connected Accounts for Token Vault"
3. Add required scopes
4. Add tools to `route.ts` following the same pattern as Spotify
5. Use Management API to get the connection's access_token

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No Spotify identity linked" | Sign out, log back in via "Continue with Spotify" |
| "No active Spotify device" | Open Spotify app, play any song for 1 second |
| 401 from Spotify API | Token expired — Auth0 should auto-refresh, but if not, sign out and back in |
| "Grant type not allowed" | Enable Token Vault in Auth0 > App > Advanced > Grant Types |
| Two users with same email | Delete the email/password user in Auth0 > User Management |
