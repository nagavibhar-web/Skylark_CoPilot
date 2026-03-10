# Skylark BI Agent — Python/Flask

A founder-level business intelligence chat agent for Monday.com (Work Orders + Deals), powered by Grok AI.

---

## Quick Setup (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and fill in your API keys

# 3. Run
python app.py
# Open http://localhost:5000
```

---

## Two API Modes

### Mode 1 — Built-in Keys (runs live automatically)
Set these in `.env`:
```
GROK_API_KEY=xai-...
MONDAY_API_KEY=eyJhbGci...
DEALS_BOARD_ID=1234567890
WO_BOARD_ID=9876543210
```
The server will auto-connect to Monday.com on startup. Users see **LIVE MODE** immediately.

### Mode 2 — User-supplied Keys
Leave the `.env` keys blank. Users click **"Configure APIs"** in the UI and paste their own keys. Keys are used per-request and never stored server-side.

Both modes work simultaneously — built-in keys are the default, user keys override them.

---

## Project Structure

```
skylark-bi/
├── app.py                  ← Flask backend + analytics engine
├── templates/
│   └── index.html          ← Full-featured chat UI
├── requirements.txt
├── .env.example            ← Copy to .env and fill in
├── .gitignore
└── README.md
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main UI |
| GET | `/api/config/builtin` | Check if built-in keys are configured |
| GET | `/api/data/demo` | Return sample data |
| POST | `/api/monday/fetch` | Fetch live Monday.com data |
| POST | `/api/chat` | Main chat endpoint |

### POST `/api/chat` body:
```json
{
  "query": "How is our energy sector pipeline?",
  "history": [],
  "data_mode": "demo",
  "deals": [],
  "work_orders": [],
  "grok_key": "xai-optional-override"
}
```

---

## Monday.com Board Setup

**Deals Board columns:** Name, Sector (Dropdown), Value (Numbers), Stage (Status), Owner (People), Close Date (Date), Probability (Numbers)

**Work Orders Board columns:** Name, Client (Text), Sector (Dropdown), Status (Status), Assignee (People), Due Date (Date), Value (Numbers)

Board IDs are in the URL: `monday.com/boards/[BOARD_ID]`
API token: Monday → Avatar → Admin → API → Generate

---

## Production Deployment

```bash
# Using gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 2

# Or with Railway / Render / Heroku
# Set environment variables in dashboard, push to git, done.
```

---

## Supported Queries

- "How is our energy sector pipeline looking this quarter?"
- "Show me top deals by value"
- "Which deals are at risk of stalling?"
- "Work order completion status"
- "Revenue forecast for next quarter"
- "Generate a leadership update for this week"
- "Pipeline by sector"
- Any natural language question (with Grok key)
