# Team Reference - Authorized to Act Hackathon

## Hackathon Overview
- **Name:** Authorized to Act: Build an Agentic AI App with Auth0
- **Platform:** Devpost
- **Theme:** Build an agentic AI application that uses Auth0 for authentication and Token Vault for secure third-party API access
- **Key Technology:** Auth0 Token Vault — lets AI agents securely access user's external services (Google, GitHub, Slack) with proper OAuth consent

## Team

### Saideva Goud Nathi — AI Engineer
- **Role:** Backend architecture, AI agent logic, API integrations
- **Skills:** Python, OpenAI API, LLM orchestration, prompt engineering, API development
- **GitHub:** SaidevaGoudNathi123

### Teammate 2 — [Name TBD]
- **Role:** [TBD]

### Teammate 3 — [Name TBD]
- **Role:** [TBD]

## Judging Criteria
1. **Technology Implementation** — How well you use Auth0 + Token Vault
2. **User Control** — Users must clearly see what scopes/permissions the agent has
3. **Innovation** — Creative use of agentic AI with secure auth
4. **User Experience** — Clean UI, smooth consent flows
5. **Completeness** — Working demo, deployed app, clear documentation

## Key Requirements
- Must use **Auth0** for authentication
- Must use **Token Vault** for at least one external API connection
- Must implement **step-up authorization** (consent popups when agent needs new permissions)
- Submission needs: working demo URL, video (max 3 min), GitHub repo, Devpost writeup

## Winning Strategy
- Start with the official Auth0 AI sample app — don't build from scratch
- Use 2-3 connections max (Google + one more is enough to impress)
- Implement step-up auth — judges specifically look for proper consent flows
- Show scopes clearly in your UI — scores well on "User Control" criteria
- Deploy to Vercel — free, fast, and submission needs a live URL
- Write the bonus blog post — extra $250 opportunity

## Resources
- Auth0 AI Samples: `auth0-ai-samples/auth0-ai-samples.git`
- Vercel AI SDK + Next.js sample: `call-apis-on-users-behalf/others-api/vercel-ai-next-js`
- Auth0 Signup: https://auth0.com/signup (free tier includes Token Vault with 2 connected apps)

## Timeline
- [ ] Set up Auth0 tenant + Token Vault
- [ ] Clone sample app and get it running locally
- [ ] Add external connections (Google Calendar + one more)
- [ ] Build the AI agent with tool calling
- [ ] Implement step-up authorization UI
- [ ] Deploy to Vercel
- [ ] Record demo video (max 3 min)
- [ ] Write Devpost submission
- [ ] Optional: Write blog post for bonus prize
