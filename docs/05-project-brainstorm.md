# Project Ideas - Brainstorm

## Decision Framework
Pick the idea that maximizes: **Auth0 integration depth x Demo-ability x Buildability in hackathon time**

---

## Idea 1: AI Personal Assistant (Calendar + Email + GitHub)
**Concept:** Chat-based assistant that manages your day — reads calendar, summarizes emails, creates GitHub issues from meeting notes.

**Auth0 Usage:** Token Vault for Google (Calendar + Gmail) + GitHub. Step-up auth for each provider.

**Pros:**
- Shows multi-provider Token Vault (judges love this)
- Very demo-friendly — everyone understands calendar + email
- Clear "user control" story — different scopes for different actions

**Cons:**
- Gmail API can be tricky with Google's verification
- Slightly generic — many teams might build this

**Verdict:** Safe bet, high scores on judging criteria.

---

## Idea 2: Developer Productivity Agent
**Concept:** AI agent for developers — reviews PRs, creates issues from natural language, summarizes repo activity, manages project boards.

**Auth0 Usage:** Token Vault for GitHub (repos, issues, PRs) + Slack (notifications).

**Pros:**
- Unique angle — developer-focused
- GitHub integration is clean and well-documented
- Can show read + write operations (create issues, comment on PRs)

**Cons:**
- Narrower audience — judges may not all be developers
- Slack integration adds complexity

**Verdict:** Good if your team is strong on GitHub APIs.

---

## Idea 3: Smart Meeting Scheduler
**Concept:** AI agent that finds optimal meeting times across calendars, creates events, sends invites, and follows up on Slack.

**Auth0 Usage:** Token Vault for Google Calendar + Slack. Step-up auth when booking on behalf of user.

**Pros:**
- Very practical — solves a real problem
- Clean demo story: "Find me a time to meet with the team this week"
- Shows both read (check availability) and write (create event) operations

**Cons:**
- Need multiple Google accounts to demo properly
- Calendar availability logic can get complex

**Verdict:** Great for showing the "agent acting on behalf of user" story.

---

## Idea 4: Content Publishing Agent
**Concept:** AI writes blog posts / social content, then publishes to GitHub Pages, schedules on social media.

**Auth0 Usage:** Token Vault for GitHub (push to repo) + LinkedIn/Twitter API.

**Pros:**
- Creative and unique
- Shows the agent taking real actions (publishing)
- Good "user control" story — approve before publishing

**Cons:**
- Social media APIs are rate-limited and annoying
- LinkedIn API access is restricted

**Verdict:** High risk, high reward. Skip unless you have API access already.

---

## Idea 5: Finance Tracker Agent
**Concept:** AI agent connects to Google Sheets (budget tracker), reads transactions, categorizes spending, creates reports.

**Auth0 Usage:** Token Vault for Google Sheets + Google Drive.

**Pros:**
- Practical and relatable
- Google Sheets API is straightforward
- Single provider but deep integration

**Cons:**
- Only one provider connection — less impressive for Token Vault demo
- Judges might want to see multi-provider

**Verdict:** Simple but might not score high on "innovation."

---

## Idea 6: AI Research Assistant
**Concept:** Agent that searches your Google Drive docs, GitHub repos, and bookmarks to answer research questions with citations.

**Auth0 Usage:** Token Vault for Google Drive + GitHub. Step-up auth for each data source.

**Pros:**
- Shows RAG-like pattern with real user data
- Multi-provider Token Vault
- Impressive technically

**Cons:**
- More complex to build — need document parsing, search logic
- Demo might be slow if indexing is needed

**Verdict:** Technically impressive but risky for hackathon timeline.

---

## Recommendation

**Go with Idea 1 (AI Personal Assistant) or Idea 3 (Smart Meeting Scheduler).**

Both:
- Use multi-provider Token Vault (high scores)
- Are easy to demo (judges understand immediately)
- Have clear "user control" moments (consent popups)
- Can be built on the sample app in hackathon time
- Deploy cleanly to Vercel

**Start with the Auth0 sample app, add Google Calendar first, then layer on a second provider.**
