# AI Shelby — Automated Community Manager

> **Built for:** The Class Economy System — [skool.com/class-economy](https://skool.com/class-economy)
> **Community Owner:** Shelby Lattimore
> **Last Updated:** May 2026

---

## What This System Does

AI Shelby is a fully automated community management system that keeps the Class Economy Skool community active and engaged — without Shelby needing to do anything day-to-day.

| Workflow | Schedule | What it does |
|----------|----------|-------------|
| **Daily Post** | Every day at 7:00 AM ET | Posts engaging day-specific content in Shelby's voice |
| **Comment Reply** | Every hour | Scans for unanswered comments and replies as Shelby |
| **Weekly Events** | Monday at 8:00 AM ET | Generates 4 community events/challenges for the week |

All three workflows can be paused/resumed with a **single toggle** — no code changes required.

---

## Project File Structure

```
ai-shelby/
│
├── config.json              ← On/off toggle (edit SYSTEM_ACTIVE here)
├── .env                     ← API keys (never commit this to GitHub)
├── requirements.txt         ← Python dependencies
│
├── shelby_prompt.py         ← Shelby's AI personality (shared by all scripts)
├── daily_post.py            ← Workflow 1: Daily morning post
├── comment_reply.py         ← Workflow 2: Hourly comment reply
├── weekly_events.py         ← Workflow 3: Weekly event generator
│
├── utils/
│   ├── apify_client.py      ← All Skool read/write via Apify
│   ├── claude_client.py     ← All AI content generation via Claude
│   └── toggle.py            ← On/off toggle reader/writer
│
├── dashboard/
│   ├── app.py               ← Flask toggle dashboard server
│   └── templates/
│       └── index.html       ← Beautiful one-page toggle UI
│
└── README.md                ← This file
```

---

## Setup Instructions

### Step 1: Prerequisites

Make sure you have **Python 3.10+** installed:
```bash
python --version
```

### Step 2: Install Dependencies

```bash
cd ai-shelby
pip install -r requirements.txt
```

### Step 3: Set Up API Keys

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your real API keys (see **Credentials** section below).

### Step 4: Verify the Toggle

Open `config.json` and make sure it reads:
```json
{
  "SYSTEM_ACTIVE": true
}
```

---

## Credentials & API Keys

### 1. Anthropic Claude API Key

| Field | Value |
|-------|-------|
| **Used for** | Generating all AI content in Shelby's voice |
| **Where to get** | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| **Where to put** | `.env` → `ANTHROPIC_API_KEY=...` |
| **Model used** | `claude-sonnet-4-20250514` |
| **Est. monthly cost** | $5–15/month depending on usage |

### 2. Apify API Token

| Field | Value |
|-------|-------|
| **Used for** | Reading posts from and writing posts to Skool |
| **Where to get** | [console.apify.com](https://console.apify.com) → Settings → Integrations → Personal API Token |
| **Where to put** | `.env` → `APIFY_API_TOKEN=...` |
| **Actor used** | `cristiantala/skool-all-in-one-api` |
| **Est. monthly cost** | $10–30/month |

> **Apify Setup:** Log into Apify, search the store for "Skool All-in-One API" by cristiantala, and click "Try for free". The actor uses Shelby's Skool cookies for authentication — set up once during first run.

### 3. Shelby's Skool User ID

| Field | Value |
|-------|-------|
| **Used for** | Filtering out comments Shelby already replied to |
| **Where to get** | Run `apify_test.py` (below) and look for `createdBy.id` on any post by Shelby |
| **Where to put** | `.env` → `SHELBY_USER_ID=...` |

**How to find Shelby's User ID:**
1. Run a test Apify call with action `posts:list` for `class-economy`
2. In the JSON response, find a post made by Shelby's account
3. Copy the value from `createdBy.id` — that's her user ID

---

## Running the Scripts Manually

Always `cd` into the `ai-shelby` directory first.

### Test: Daily Post
```bash
python daily_post.py
```
Expected output: Logs showing Claude generating a post, then Apify posting it.

### Test: Comment Reply
```bash
python comment_reply.py
```
Expected output: Fetches posts, finds unanswered comments, generates and posts replies.

### Test: Weekly Events
```bash
python weekly_events.py
```
Expected output: Claude generates 4 events as JSON, each posted to Skool.

---

## Toggle: Pause & Resume

### Option 1 — Web Dashboard (easiest for Shelby)
Run the dashboard:
```bash
python dashboard/app.py
```
Open a browser to `http://localhost:5000` (or your deployed URL).

Flip the toggle — done. No code needed.

### Option 2 — Edit config.json directly
Open `config.json` and change:
```json
{ "SYSTEM_ACTIVE": false }   ← PAUSED (no posts will be made)
{ "SYSTEM_ACTIVE": true }    ← ACTIVE (all workflows run normally)
```

---

## Deploying to Railway or Render

### Railway Deployment

1. Push this project to a GitHub repository
2. Go to [railway.app](https://railway.app) and create a new project from your GitHub repo
3. Add all environment variables from `.env` in the Railway dashboard (Settings → Variables)
4. Set up scheduled jobs (Railway Cron) with these schedules:

| Service | Command | Cron Schedule |
|---------|---------|---------------|
| Daily Post | `python daily_post.py` | `0 12 * * *` (7AM ET = 12:00 UTC) |
| Comment Reply | `python comment_reply.py` | `0 * * * *` |
| Weekly Events | `python weekly_events.py` | `0 13 * * 1` (8AM ET Mon = 13:00 UTC) |
| Dashboard | `python dashboard/app.py` | (always running) |

> **Timezone Note:** Railway runs in UTC. Eastern Time is UTC-5 (standard) or UTC-4 (daylight saving). Adjust cron accordingly. During daylight saving (March–November): 7AM ET = 11:00 UTC. During standard time (November–March): 7AM ET = 12:00 UTC.

### Render Deployment

1. Push to GitHub
2. Create a **Web Service** on [render.com](https://render.com) for the dashboard (`python dashboard/app.py`)
3. Create **Cron Jobs** for each workflow script using the schedules above
4. Add environment variables in Render dashboard → Environment

---

## Cron Schedule Reference

```bash
# Daily post — 7:00 AM Eastern (UTC-4 during DST, UTC-5 during standard)
0 11 * * *   python /path/to/ai-shelby/daily_post.py     # DST
0 12 * * *   python /path/to/ai-shelby/daily_post.py     # Standard time

# Comment reply — every hour
0 * * * *    python /path/to/ai-shelby/comment_reply.py

# Weekly events — Monday 8:00 AM Eastern
0 12 * * 1   python /path/to/ai-shelby/weekly_events.py  # DST
0 13 * * 1   python /path/to/ai-shelby/weekly_events.py  # Standard time
```

---

## Testing Checklist

Before going live, complete every item below:

- [ ] Apify read test — fetch posts from `class-economy` group successfully
- [ ] Apify write test — test post appears in community (delete immediately after)
- [ ] Apify reply test — test reply appears under a post (delete immediately after)
- [ ] Claude generates a post that sounds like Shelby (not robotic)
- [ ] Claude generates a comment reply that sounds like Shelby
- [ ] `daily_post.py` runs manually and posts successfully
- [ ] `comment_reply.py` runs manually and replies successfully
- [ ] `weekly_events.py` runs manually and posts 4 event announcements
- [ ] `SYSTEM_ACTIVE: false` — all scripts exit immediately without posting
- [ ] `SYSTEM_ACTIVE: true` — all scripts resume normally
- [ ] Toggle dashboard loads and toggle button works
- [ ] Cron schedules confirmed active on server
- [ ] All API keys documented and stored securely

---

## Troubleshooting

### "ANTHROPIC_API_KEY is not set"
→ Make sure your `.env` file exists and contains the real key (not the placeholder).

### "APIFY_API_TOKEN is not set"
→ Same — check your `.env` file.

### "SHELBY_USER_ID is not set"
→ Run an Apify test call, find Shelby's `createdBy.id` and add it to `.env`.

### Apify returns empty results
→ The actor may need authentication. Verify Shelby's Skool login credentials are saved in the Apify actor's input settings.

### Claude generates content that sounds robotic
→ Check `shelby_prompt.py` — the system prompt must be passed exactly as-is to every Claude call.

### Comment reply posts duplicate replies
→ Verify `SHELBY_USER_ID` is correct. This ID is how the script detects Shelby's existing replies.

---

## Security Notes

- **Never commit `.env` to GitHub.** It is listed in `.gitignore`.
- API keys should be added to the deployment platform (Railway/Render) as environment variables, not hardcoded.
- The toggle dashboard has no login — the URL itself is the password. Deploy it on a non-guessable URL or add basic auth for extra security.

---

## Monthly Cost Estimate

| Service | Est. Cost |
|---------|-----------|
| Anthropic Claude API | $5–15/month |
| Apify | $10–30/month |
| Railway / Render hosting | $5–20/month |
| **Total** | **$20–65/month** |

---

*AI Shelby — Built for The Class Economy System by Shelby Lattimore.*
*Questions? Contact the project owner listed in your handover document.*
