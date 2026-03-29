# Tech Stack Options & Comparison

## Recommended Stack (Fastest Path to Submission)

| Layer | Choice | Reason |
|-------|--------|--------|
| Framework | Next.js 14+ (App Router) | Auth0 has official SDK + sample app |
| Auth | @auth0/nextjs-auth0 v4 | First-class Token Vault support |
| AI SDK | Vercel AI SDK (ai@6) | streamText, tool calling, streaming UI |
| Token Mgmt | @auth0/ai-vercel@5 | withTokenVault wrapper, interrupts |
| LLM | OpenAI GPT-4o-mini | Cheap, fast, great at tool calling |
| UI | Tailwind + @ai-sdk/react | useChat hook, built-in streaming |
| Deploy | Vercel | One-click deploy, free tier |

---

## Framework Options Compared

### 1. Next.js + Vercel AI SDK (RECOMMENDED)
- **Auth0 support:** Official SDK, sample app, full docs
- **Effort:** Low — clone sample and extend
- **Deploy:** Vercel (free, fast)
- **Language:** TypeScript
- **Best for:** Hackathon speed

### 2. Python + FastAPI
- **Auth0 support:** Community SDK, no official AI wrapper
- **Effort:** Medium — need to build Token Vault integration manually
- **Deploy:** Railway, Render, or Fly.io
- **Language:** Python
- **Best for:** Teams more comfortable with Python
- **Caveat:** No `@auth0/ai-vercel` equivalent — you'd need to handle OAuth token exchange manually

### 3. Python + Flask
- **Auth0 support:** authlib library
- **Effort:** High — no Token Vault wrapper, manual everything
- **Deploy:** Heroku, Railway
- **Language:** Python
- **Best for:** Simple apps, not recommended for this hackathon

### 4. Express.js (Node)
- **Auth0 support:** express-openid-connect
- **Effort:** Medium — no Vercel AI SDK integration
- **Deploy:** Any Node host
- **Best for:** Teams who prefer vanilla Node
- **Caveat:** No streaming UI helpers — build chat UI from scratch

### 5. Remix
- **Auth0 support:** Limited — community adapters
- **Effort:** High
- **Best for:** Not this hackathon

### 6. SvelteKit
- **Auth0 support:** Very limited
- **Effort:** High
- **Best for:** Not this hackathon

### 7. Django
- **Auth0 support:** python-jose + authlib
- **Effort:** Very high for Token Vault
- **Best for:** Not this hackathon

---

## LLM Provider Options

| Provider | Model | Cost | Tool Calling | Notes |
|----------|-------|------|-------------|-------|
| **OpenAI** | gpt-4o-mini | $0.15/$0.60 per 1M tokens | Excellent | Best tool calling, fastest |
| OpenAI | gpt-4o | $2.50/$10 per 1M tokens | Excellent | Better quality, more expensive |
| Anthropic | claude-sonnet-4-20250514 | $3/$15 per 1M tokens | Good | Great reasoning, higher cost |
| Google | gemini-2.0-flash | Free tier available | Good | Free option, slightly less reliable tool calling |

**Recommendation:** Start with `gpt-4o-mini` — it's cheap, fast, and handles tool calling better than any other model at its price point. Upgrade to `gpt-4o` only if quality isn't good enough.

---

## Deployment Options

### Vercel (RECOMMENDED)
- **Cost:** Free tier (100GB bandwidth, serverless functions)
- **Setup:** Connect GitHub repo, auto-deploy on push
- **Auth0 compatibility:** Perfect — env vars in dashboard, edge middleware works
- **Command:** `vercel deploy` or auto-deploy from GitHub

### Netlify
- **Cost:** Free tier available
- **Setup:** Similar to Vercel
- **Auth0 compatibility:** Good but middleware requires adapters
- **Caveat:** Server functions work differently

### Railway
- **Cost:** $5 credit free
- **Setup:** Connect GitHub, auto-deploy
- **Auth0 compatibility:** Good for Python backends
- **Best for:** If you go Python + FastAPI route

### Fly.io
- **Cost:** Free tier (3 shared VMs)
- **Auth0 compatibility:** Good
- **Best for:** Docker-based deployments

---

## Final Recommendation

```
Next.js + Vercel AI SDK + Auth0 + GPT-4o-mini + Vercel hosting
```

This is the path of least resistance. The official sample app gives you 70% of the work done. You just need to:
1. Clone the sample
2. Add your Auth0 credentials
3. Add your tools (Google Calendar, GitHub)
4. Customize the UI
5. Deploy to Vercel

Everything else is over-engineering for a hackathon.
