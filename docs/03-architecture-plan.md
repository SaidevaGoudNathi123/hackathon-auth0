# Architecture Plan

## System Overview

```
User (Browser)
  |
  v
Next.js App (Vercel) ---- Auth0 (Login + Token Vault)
  |                              |
  v                              v
Vercel AI SDK -----> LLM (GPT-4o-mini)
  |                              |
  v                              v
Agent Tools ---------> External APIs
  |                    (Google Calendar, GitHub, etc.)
  |
  v
Token Vault (secure token storage + refresh)
```

## Core Flow

1. **User logs in** via Auth0 Universal Login
2. **User sends a message** in the chat UI
3. **Next.js API route** receives the message, passes it to the LLM via Vercel AI SDK
4. **LLM decides** to call a tool (e.g., `getCalendarEvents`)
5. **Tool is wrapped** with `withTokenVault` — checks if user has authorized this connection
6. **If not authorized**: Auth0 sends an "interrupt" -> UI shows consent popup -> user approves
7. **If authorized**: Token Vault provides a fresh access token -> tool calls the API
8. **Results flow back** through the LLM -> streamed to the user's chat

## Key Architecture Decisions

### Why Next.js + Vercel AI SDK
- Official Auth0 AI SDK has first-class Vercel AI SDK support
- `@auth0/ai-vercel` provides `withTokenVault` wrapper
- Streaming responses out of the box with `streamText`
- Deploy to Vercel in one click

### Why Token Vault (Not Raw OAuth)
- Handles token refresh automatically
- Secure server-side storage — tokens never touch the browser
- Supports multiple providers with the same pattern
- Step-up authorization built in (interrupts pattern)

### Auth Pattern: Interrupts
When the agent needs a permission the user hasn't granted yet:
1. Tool execution pauses
2. Auth0 returns an "interrupt" with the required connection + scopes
3. Frontend shows the `TokenVaultInterruptHandler` component
4. User clicks "Authorize" -> OAuth consent flow
5. Token stored in Token Vault
6. Tool execution resumes automatically

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14+ (App Router) | Auth0 SDK support, server components |
| UI | Tailwind CSS + @ai-sdk/react | Fast styling, built-in chat hooks |
| Auth | @auth0/nextjs-auth0 v4 | Session management, middleware |
| AI Agent | Vercel AI SDK (ai@6) | streamText, tool calling |
| Token Mgmt | @auth0/ai-vercel | Token Vault integration |
| LLM | OpenAI GPT-4o-mini | Fast, cheap, good at tool calling |
| External APIs | googleapis, @octokit/rest | Google Calendar, GitHub |
| Deploy | Vercel | Free, fast, auto-deploy from GitHub |

## External Connections Plan

### Connection 1: Google Calendar (Primary)
- **Scopes:** `openid`, `calendar.events`
- **Tools:** `getCalendarEvents`, `createCalendarEvent`
- **Demo value:** Shows agent reading and writing to user's real calendar

### Connection 2: GitHub (Secondary)
- **Scopes:** `public_repo`, `read:user`
- **Tools:** `listRepos`, `getRepoIssues`, `createIssue`
- **Demo value:** Shows multi-provider capability

## Security Considerations
- All tokens stored server-side in Token Vault (never in browser)
- Middleware protects all routes except `/auth/*`
- Refresh token rotation enabled
- Scopes are minimal — request only what's needed
- Step-up auth ensures user explicitly consents to each provider
