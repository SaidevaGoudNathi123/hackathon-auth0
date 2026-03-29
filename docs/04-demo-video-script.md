# Demo Video Script (Max 3 Minutes)

## Structure: Problem -> Solution -> Demo -> Architecture

---

### [0:00 - 0:20] Hook + Problem Statement

"AI agents are everywhere — but here's the problem. When your AI agent needs to access your Google Calendar, your GitHub repos, or your Slack messages, how do you do that securely? Most projects hardcode API keys or skip auth entirely. That's not how production works."

### [0:20 - 0:40] Our Solution

"We built [PROJECT NAME] — an AI agent that securely acts on behalf of users using Auth0 Token Vault. The agent only accesses what you explicitly authorize, with real OAuth consent flows."

### [0:40 - 1:30] Live Demo — The Happy Path

**Screen recording of the app:**

1. "Here's the app. I'm going to log in with Google through Auth0."
   - Show Auth0 Universal Login screen
   - Log in with Google

2. "Now I'll ask the agent: 'What's on my calendar today?'"
   - Type the message in the chat
   - **Show the consent popup** (key moment for judges)
   - "Notice the agent is asking for permission to access Google Calendar. I can see exactly what scopes it's requesting."
   - Click Authorize

3. "And just like that, the agent reads my actual calendar events."
   - Show the response with real calendar data

4. "Now watch — if I ask again, no consent popup. Token Vault stored the token securely."
   - Ask another calendar question
   - Instant response, no popup

### [1:30 - 2:00] Second Connection (GitHub)

5. "Let me try: 'Show me my latest GitHub issues.'"
   - New consent popup for GitHub
   - "Different provider, same secure pattern. The user is always in control."
   - Authorize and show results

### [2:00 - 2:30] Architecture Walkthrough

Show the architecture diagram:

"Under the hood:
- **Auth0** handles login and session management
- **Token Vault** securely stores and refreshes OAuth tokens
- **Vercel AI SDK** powers the chat with streaming and tool calling
- **Interrupts pattern** — when the agent needs a new permission, it pauses, asks, and resumes
- All deployed on **Vercel**"

### [2:30 - 2:50] What Makes This Different

"Three things:
1. **User control** — you see every permission before it's granted
2. **Security by default** — tokens are server-side, refresh rotation is on, scopes are minimal
3. **Real OAuth** — not simulated, not hardcoded"

### [2:50 - 3:00] Closing

"This is [PROJECT NAME] — secure agentic AI powered by Auth0. Thanks for watching."

---

## Recording Tips
- Use a clean browser profile (no bookmarks bar, no extensions)
- Pre-populate Google Calendar with 3-4 events
- Have a few GitHub issues ready
- Record at 1080p minimum
- Use a good mic
- Practice the full flow once before recording
- Keep it under 3 minutes
