# Skylark BI — Complete Setup Guide (Local → Streamlit Cloud)

---

## STEP 1 — Prerequisites

Make sure you have these installed:

```bash
python --version      # needs Python 3.9+
pip --version         # comes with Python
git --version         # for GitHub deployment
```

If Python is not installed → download from https://python.org/downloads

---

## STEP 2 — Get the Code

Download and unzip `skylark-bi-agent-python.zip`, then open a terminal inside the folder:

```bash
cd skylark-bi
```

---

## STEP 3 — Create a Virtual Environment (recommended)

```bash
# Create venv
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You'll see `(venv)` appear in your terminal prompt.

---

## STEP 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `streamlit`, `requests`, `python-dotenv`

---

## STEP 5 — Configure API Keys

### Option A — Secrets file (recommended for local dev)

```bash
# Create the .streamlit folder and secrets file
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Now edit `.streamlit/secrets.toml`:

```toml
GROK_API_KEY   = "xai-your-actual-key"
MONDAY_API_KEY = "eyJhbGci...your-monday-token"
DEALS_BOARD_ID = "1234567890"
WO_BOARD_ID    = "9876543210"
```

**Where to find these keys:**

| Key | Where to get it |
|-----|----------------|
| `GROK_API_KEY` | Go to https://console.x.ai → API Keys → Create Key |
| `MONDAY_API_KEY` | Monday.com → click your Avatar → Admin → API → Generate Token |
| `DEALS_BOARD_ID` | Open your Deals board → look at the URL: `monday.com/boards/XXXXXXXXXX` |
| `WO_BOARD_ID` | Same for your Work Orders board |

### Option B — Leave blank (Demo Mode)

Skip the secrets file entirely. The app launches in Demo Mode with sample data.
You can still enter keys via the sidebar in the running app.

---

## STEP 6 — Run Locally

```bash
streamlit run streamlit_app.py
```

Your browser opens automatically at **http://localhost:8501**

To stop: press `Ctrl + C` in the terminal.

---

## STEP 7 — Deploy to Streamlit Cloud (FREE)

### 7a — Push code to GitHub

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit — Skylark BI Agent"

# Create a new repo on GitHub (github.com → New repository)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/skylark-bi.git
git branch -M main
git push -u origin main
```

### 7b — Deploy on Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Click **"New app"**
3. Select your GitHub repo: `YOUR_USERNAME/skylark-bi`
4. Set **Main file path**: `streamlit_app.py`
5. Click **"Deploy!"**

### 7c — Add your secrets on Streamlit Cloud

1. After deployment, click **"⋮" → Settings** on your app
2. Click **"Secrets"**
3. Paste this (fill in your real values):

```toml
GROK_API_KEY   = "xai-your-actual-key"
MONDAY_API_KEY = "eyJhbGci...your-monday-token"
DEALS_BOARD_ID = "1234567890"
WO_BOARD_ID    = "9876543210"
```

4. Click **"Save"** → app restarts automatically
5. Your live URL: `https://YOUR_USERNAME-skylark-bi-streamlit-app-XXXXX.streamlit.app`

---

## File Structure

```
skylark-bi/
├── streamlit_app.py          ← Main app (run this)
├── app.py                    ← Flask version (alternative)
├── requirements.txt          ← streamlit, requests, python-dotenv
├── .streamlit/
│   ├── config.toml           ← Dark theme config
│   └── secrets.toml.example  ← Copy → secrets.toml and fill in
├── templates/
│   └── index.html            ← Flask UI (not used by Streamlit)
├── .gitignore                ← Excludes .env and secrets.toml
├── README.md
└── DECISION_LOG.md
```

---

## Two API Modes — Summary

| | Mode 1 (Built-in Keys) | Mode 2 (User Keys) |
|---|---|---|
| Setup | Fill `secrets.toml` | Leave blank |
| Result | Auto-connects LIVE on startup | User enters keys in sidebar |
| Best for | Your own deployment | Sharing with others |

Both modes work in the same app — built-in keys auto-connect; sidebar keys override per session.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: streamlit` | Run `pip install -r requirements.txt` |
| `Port 8501 already in use` | Run `streamlit run streamlit_app.py --server.port 8502` |
| Monday.com returns 401 | Token expired — regenerate in Monday Admin → API |
| Grok returns 401 | Check key starts with `xai-` and has credits |
| Board ID not found | Check URL: `monday.com/boards/[THIS NUMBER]` |
| Streamlit Cloud shows blank | Check Secrets are saved and app was restarted |

---

## Quick Command Reference

```bash
# Install
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app.py

# Run on different port
streamlit run streamlit_app.py --server.port 8502

# Check streamlit version
streamlit --version

# Upgrade streamlit
pip install --upgrade streamlit
```
