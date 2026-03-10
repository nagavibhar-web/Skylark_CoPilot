"""
Skylark BI Agent — Flask Backend
Run: python app.py
Visit: http://localhost:5000
"""

import os
import json
import re
import requests
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "skylark-bi-secret-2025")
CORS(app)

# ─────────────────────────────────────────────
# BUILT-IN API KEYS (Mode 1 — Pre-configured)
# Set these in .env for the "already set" mode
# ─────────────────────────────────────────────
BUILTIN_GROK_KEY    = os.environ.get("GROK_API_KEY", "")
BUILTIN_MONDAY_KEY  = os.environ.get("MONDAY_API_KEY", "")
BUILTIN_DEALS_BOARD = os.environ.get("DEALS_BOARD_ID", "")
BUILTIN_WO_BOARD    = os.environ.get("WO_BOARD_ID", "")

# ─────────────────────────────────────────────
# SAMPLE / DEMO DATA
# ─────────────────────────────────────────────
SAMPLE_DEALS = [
    {"id": 1,  "name": "TechCorp Phase 2",        "sector": "Technology",    "value": 320000, "stage": "Proposal",     "owner": "Ankit S.",  "date": "2025-03-15", "probability": 65},
    {"id": 2,  "name": "EnergyCo Solar Grid",      "sector": "Energy",        "value": 480000, "stage": "Negotiation",  "owner": "Priya R.",  "date": "2025-03-20", "probability": 80},
    {"id": 3,  "name": "ManufactX Inspection",     "sector": "Manufacturing", "value": 150000, "stage": "Won",          "owner": "Rahul K.",  "date": "2025-02-10", "probability": 100},
    {"id": 4,  "name": "SkyLogistics Drone Survey","sector": "Logistics",     "value": 210000, "stage": "Proposal",     "owner": "Meera T.",  "date": "2025-03-28", "probability": 55},
    {"id": 5,  "name": "GreenEnergy Windmill",     "sector": "Energy",        "value": 395000, "stage": "Prospecting",  "owner": "Ankit S.",  "date": "2025-04-01", "probability": 30},
    {"id": 6,  "name": "BioTech Lab Mapping",      "sector": "Healthcare",    "value": 175000, "stage": "Proposal",     "owner": "Priya R.",  "date": "2025-03-10", "probability": 60},
    {"id": 7,  "name": "UrbanPlan City Survey",    "sector": "Government",    "value": 520000, "stage": "Negotiation",  "owner": "Rahul K.",  "date": "2025-02-25", "probability": 75},
    {"id": 8,  "name": "OilRig Delta Inspection",  "sector": "Energy",        "value": 290000, "stage": "Won",          "owner": "Meera T.",  "date": "2025-01-15", "probability": 100},
    {"id": 9,  "name": "AgroFarm Mapping",         "sector": "Agriculture",   "value": 95000,  "stage": "Lost",         "owner": "Ankit S.",  "date": "2025-02-05", "probability": 0},
    {"id": 10, "name": "TelecomTower Audit",       "sector": "Telecom",       "value": 130000, "stage": "Proposal",     "owner": "Priya R.",  "date": "2025-04-05", "probability": 50},
    {"id": 11, "name": "RetailChain Inventory",    "sector": "Retail",        "value": None,   "stage": "Prospecting",  "owner": "Rahul K.",  "date": None,         "probability": 25},
    {"id": 12, "name": "PortAuth Dock Survey",     "sector": "Logistics",     "value": 240000, "stage": "Proposal",     "owner": "Meera T.",  "date": "2025-03-30", "probability": 70},
]

SAMPLE_WORK_ORDERS = [
    {"id": 101, "title": "Solar Panel Array Survey - Phase 1", "client": "EnergyCo",       "sector": "Energy",        "status": "In Progress", "assignee": "Drone Team A", "due": "2025-03-25", "value": 45000,  "completion": 60},
    {"id": 102, "title": "Windmill Blade Inspection",          "client": "GreenEnergy",    "sector": "Energy",        "status": "Completed",   "assignee": "Drone Team B", "due": "2025-03-10", "value": 32000,  "completion": 100},
    {"id": 103, "title": "Factory Roof Thermal Scan",          "client": "ManufactX",      "sector": "Manufacturing", "status": "Completed",   "assignee": "Drone Team A", "due": "2025-02-28", "value": 28000,  "completion": 100},
    {"id": 104, "title": "Logistics Hub Mapping",              "client": "SkyLogistics",   "sector": "Logistics",     "status": "In Progress", "assignee": "Drone Team C", "due": "2025-03-20", "value": 38000,  "completion": 40},
    {"id": 105, "title": "OilRig Safety Inspection",           "client": "OilRig Delta",   "sector": "Energy",        "status": "Overdue",     "assignee": "Drone Team B", "due": "2025-03-05", "value": 62000,  "completion": 20},
    {"id": 106, "title": "City Infrastructure Audit",          "client": "UrbanPlan",      "sector": "Government",    "status": "In Progress", "assignee": "Drone Team A", "due": "2025-04-10", "value": 85000,  "completion": 30},
    {"id": 107, "title": "Crop Health Assessment",             "client": "AgroFarm",       "sector": "Agriculture",   "status": "Completed",   "assignee": "Drone Team C", "due": "2025-02-20", "value": 18000,  "completion": 100},
    {"id": 108, "title": "Telecom Tower Scan",                 "client": "TelecomTower",   "sector": "Telecom",       "status": "Pending",     "assignee": "Unassigned",   "due": "2025-04-15", "value": 22000,  "completion": 0},
    {"id": 109, "title": "BioLab Clean Room Survey",           "client": "BioTech Lab",    "sector": "Healthcare",    "status": "In Progress", "assignee": "Drone Team B", "due": "2025-03-28", "value": 41000,  "completion": 55},
    {"id": 110, "title": "Port Dock Perimeter Scan",           "client": "PortAuth",       "sector": "Logistics",     "status": "Pending",     "assignee": "Drone Team A", "due": "2025-04-20", "value": 35000,  "completion": 0},
    {"id": 111, "title": "Retail Inventory Drone Count",       "client": "RetailChain",    "sector": "Retail",        "status": "Overdue",     "assignee": "Drone Team C", "due": "2025-03-01", "value": None,   "completion": 10},
    {"id": 112, "title": "Solar Phase 2 Prep",                 "client": "EnergyCo",       "sector": "Energy",        "status": "Pending",     "assignee": "Drone Team A", "due": "2025-04-25", "value": 53000,  "completion": 0},
]


# ─────────────────────────────────────────────
# MONDAY.COM API CLIENT
# ─────────────────────────────────────────────
MONDAY_GQL_URL = "https://api.monday.com/v2"

def fetch_monday_board(board_id: str, api_key: str) -> list[dict]:
    """Fetch all items from a Monday.com board via GraphQL."""
    query = """
    query($ids: [ID!]!) {
      boards(ids: $ids) {
        name
        items_page(limit: 200) {
          items {
            id
            name
            column_values {
              id
              text
              value
              column { title }
            }
          }
        }
      }
    }
    """
    resp = requests.post(
        MONDAY_GQL_URL,
        json={"query": query, "variables": {"ids": [str(board_id)]}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise ValueError(f"Monday API error: {data['errors'][0]['message']}")
    board = data["data"]["boards"][0]
    return _parse_board_items(board)


def _parse_board_items(board: dict) -> list[dict]:
    """Convert raw Monday.com items to flat dicts keyed by column title."""
    result = []
    for item in board["items_page"]["items"]:
        obj = {"id": item["id"], "name": item["name"]}
        for cv in item["column_values"]:
            key = cv["column"]["title"].lower().replace(" ", "_")
            obj[key] = cv["text"] or None
        result.append(obj)
    return result


def normalize_items(items: list[dict]) -> list[dict]:
    """
    Clean messy real-world data:
    - Strip currency symbols / commas from numeric fields
    - Normalize empty / NA strings to None
    - Add *_num variants for detected numbers
    """
    null_sentinels = {"", "n/a", "N/A", "na", "NA", "-", "—", "null", "none", "None"}
    cleaned = []
    for item in items:
        row = {}
        for k, v in item.items():
            if v in null_sentinels:
                row[k] = None
            elif isinstance(v, str):
                stripped = re.sub(r"[$,₹€£\s]", "", v)
                if re.fullmatch(r"-?\d+(\.\d+)?", stripped):
                    row[k] = float(stripped)
                else:
                    row[k] = v.strip()
            else:
                row[k] = v
        cleaned.append(row)
    return cleaned


# ─────────────────────────────────────────────
# DATA ANALYTICS ENGINE
# ─────────────────────────────────────────────
def compute_stats(deals: list, work_orders: list) -> dict:
    active_deals  = [d for d in deals if d.get("stage") not in ("Lost", "Won")]
    won_deals     = [d for d in deals if d.get("stage") == "Won"]
    lost_deals    = [d for d in deals if d.get("stage") == "Lost"]
    total_pipeline = sum(d.get("value") or 0 for d in active_deals)
    won_value      = sum(d.get("value") or 0 for d in won_deals)

    sector_map: dict[str, dict] = {}
    for d in deals:
        sec = d.get("sector") or "Unknown"
        sector_map.setdefault(sec, {"deals": [], "value": 0})
        sector_map[sec]["deals"].append(d)
        sector_map[sec]["value"] += d.get("value") or 0

    def _wo_filter(status_kw):
        return [w for w in work_orders if status_kw.lower() in (w.get("status") or "").lower()]

    wo_completed  = _wo_filter("complet")
    wo_in_progress= _wo_filter("progress")
    wo_overdue    = _wo_filter("overdue")
    wo_pending    = _wo_filter("pending")

    null_values = sum(1 for d in deals if d.get("value") is None)
    null_dates  = sum(1 for d in deals if not d.get("date"))
    denom = len(won_deals) + len(lost_deals)
    win_rate = round(len(won_deals) / denom * 100) if denom else 0

    return {
        "deals": deals, "work_orders": work_orders,
        "active_deals": active_deals, "won_deals": won_deals, "lost_deals": lost_deals,
        "total_pipeline": total_pipeline, "won_value": won_value,
        "sector_map": sector_map,
        "wo_completed": wo_completed, "wo_in_progress": wo_in_progress,
        "wo_overdue": wo_overdue, "wo_pending": wo_pending,
        "null_values": null_values, "null_dates": null_dates, "win_rate": win_rate,
    }


def fmt_val(v) -> str:
    if v is None:
        return "N/A"
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"


def rule_based_response(query: str, stats: dict) -> str:
    """Generate structured HTML response based on query intent."""
    q = query.lower()
    d = stats

    def metric_row(*chips):
        inner = "".join(
            f'<div class="metric-chip"><div class="mc-val {c[2]}">{c[0]}</div>'
            f'<div class="mc-label">{c[1]}</div></div>'
            for c in chips
        )
        return f'<div class="metric-row">{inner}</div>'

    def table(headers, rows):
        ths = "".join(f"<th>{h}</th>" for h in headers)
        trs = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        return f'<table class="data-table"><tr>{ths}</tr>{trs}</table>'

    def badge(text, color="sky"):
        return f'<span class="badge {color}">{text}</span>'

    def insight(title, body):
        return f'<div class="insight-card"><div class="ic-title">{title}</div>{body}</div>'

    def caveat(title, body):
        return f'<div class="caveat"><strong>{title}</strong>{body}</div>'

    # ── LEADERSHIP UPDATE ──────────────────────────────────────────────
    if any(k in q for k in ("leadership", "board update", "weekly update", "exec update")):
        top_deals = sorted(d["active_deals"], key=lambda x: x.get("value") or 0, reverse=True)[:4]
        at_risk   = [x for x in d["active_deals"] if (x.get("probability") or 50) < 45]

        deal_rows = [
            [x["name"], x.get("sector","—"), fmt_val(x.get("value")),
             badge(x.get("stage","—"), "sky"), f'{x.get("probability","?")}%']
            for x in top_deals
        ]
        html = f"""
        <h4>📊 Weekly Leadership Update — Skylark Drones</h4>
        {metric_row(
            (fmt_val(d["total_pipeline"]), "Total Pipeline",    "b"),
            (fmt_val(d["won_value"]),      "Won Revenue",       "g"),
            (f'{d["win_rate"]}%',          "Win Rate",          "a"),
            (str(len(d["wo_overdue"])),    "WOs Overdue",       "r"),
        )}
        {insight("📌 Executive Summary",
            f'Pipeline at <strong>{fmt_val(d["total_pipeline"])}</strong> across '
            f'<strong>{len(d["active_deals"])}</strong> active deals. '
            f'Win rate <strong>{d["win_rate"]}%</strong>. '
            + (f'<strong style="color:var(--red)">{len(d["wo_overdue"])} work order(s) overdue</strong> — requires immediate action.'
               if d["wo_overdue"] else "All work orders on track.")
        )}
        <h4>🏆 Top Active Deals</h4>
        {table(["Deal","Sector","Value","Stage","Prob."], deal_rows)}
        <h4>🔧 Operations Snapshot</h4>
        {metric_row(
            (str(len(d["wo_completed"])),   "Completed",   "g"),
            (str(len(d["wo_in_progress"])), "In Progress", "b"),
            (str(len(d["wo_pending"])),     "Pending",     "a"),
            (str(len(d["wo_overdue"])),     "Overdue",     "r"),
        )}
        {caveat("⚠ DEALS AT RISK", ", ".join(
            f'{x["name"]} ({x.get("probability","?")}% — {fmt_val(x.get("value"))})'
            for x in at_risk) or "None") if at_risk else ""}
        {caveat("⚠ DATA QUALITY", f'{d["null_values"]} deal(s) missing value data.') if d["null_values"] else ""}
        {insight("🎯 Recommended Actions",
            f'1. Follow up on <strong>{len(at_risk)}</strong> at-risk deals before quarter end<br>'
            f'2. Resolve <strong>{len(d["wo_overdue"])}</strong> overdue work orders<br>'
            f'3. {len([x for x in d["active_deals"] if x.get("stage")=="Negotiation"])} deals in Negotiation — prioritize close<br>'
            f'4. Energy sector has highest concentration — watch for dependency risk'
        )}
        """
        return html

    # ── ENERGY ────────────────────────────────────────────────────────
    if "energy" in q:
        e_deals = d["sector_map"].get("Energy", {}).get("deals", [])
        e_active = [x for x in e_deals if x.get("stage") not in ("Won","Lost")]
        e_val = sum(x.get("value") or 0 for x in e_active)
        e_wos = [w for w in d["work_orders"] if (w.get("sector") or "").lower() == "energy"]

        deal_rows = [[
            x["name"], fmt_val(x.get("value")),
            badge(x.get("stage","—"), "green" if x.get("stage")=="Won" else "red" if x.get("stage")=="Lost" else "sky"),
            x.get("owner","—"), f'{x.get("probability","?")}%'
        ] for x in e_deals]

        wo_rows = [[w["title"], w["client"],
                    badge(w.get("status","—"), "green" if "Complet" in (w.get("status") or "") else
                          "red" if "Overdue" in (w.get("status") or "") else "sky"),
                    fmt_val(w.get("value"))] for w in e_wos]

        return f"""
        {insight("⚡ Energy Sector Pipeline",
            f'<strong>{len(e_deals)}</strong> total · <strong>{len(e_active)}</strong> active · '
            f'Pipeline: <strong>{fmt_val(e_val)}</strong>')}
        {table(["Deal","Value","Stage","Owner","Prob."], deal_rows)}
        <h4>🔧 Energy Work Orders ({len(e_wos)})</h4>
        {table(["Work Order","Client","Status","Value"], wo_rows)}
        {insight("💡 Insight",
            "Energy is your highest-value sector. "
            f'{len([x for x in e_active if x.get("stage")=="Negotiation"])} deals in Negotiation — '
            "strong Q2 potential.")}
        """

    # ── PIPELINE / DEALS ──────────────────────────────────────────────
    if any(k in q for k in ("pipeline", "deal", "proposal")):
        by_stage: dict[str, list] = {}
        for dd in d["deals"]:
            by_stage.setdefault(dd.get("stage","Unknown"), []).append(dd)

        stage_rows = []
        for stage, items in by_stage.items():
            total = sum(x.get("value") or 0 for x in items)
            with_val = [x for x in items if x.get("value")]
            avg = total / len(with_val) if with_val else None
            stage_rows.append([badge(stage, "green" if stage=="Won" else "red" if stage=="Lost" else "sky"),
                                str(len(items)), fmt_val(total), fmt_val(avg)])

        top5 = sorted(d["active_deals"], key=lambda x: x.get("value") or 0, reverse=True)[:5]
        top_rows = [[x["name"], x.get("sector","—"), fmt_val(x.get("value")),
                     badge(x.get("stage","—"), "sky")] for x in top5]

        return f"""
        {metric_row(
            (fmt_val(d["total_pipeline"]), "Active Pipeline", "b"),
            (str(len(d["won_deals"])),     "Deals Won",       "g"),
            (f'{d["win_rate"]}%',          "Win Rate",        "a"),
            (str(len(d["lost_deals"])),    "Deals Lost",      "r"),
        )}
        <h4>Pipeline by Stage</h4>
        {table(["Stage","Count","Total Value","Avg. Value"], stage_rows)}
        <h4>Top 5 Active Deals</h4>
        {table(["Deal","Sector","Value","Stage"], top_rows)}
        {caveat("⚠ DATA QUALITY", f'{d["null_values"]} deal(s) missing value data — total understated.') if d["null_values"] else ""}
        """

    # ── WORK ORDERS ───────────────────────────────────────────────────
    if any(k in q for k in ("work order", "wo ", "operation", "overdue", "complet")):
        wo_rows = [[
            w["title"], w.get("client","—"),
            badge(w.get("status","—"),
                  "green" if "Complet" in (w.get("status") or "") else
                  "red"   if "Overdue" in (w.get("status") or "") else
                  "sky"   if "Progress" in (w.get("status") or "") else "a"),
            w.get("due","—"), fmt_val(w.get("value"))
        ] for w in d["work_orders"]]

        return f"""
        {metric_row(
            (str(len(d["wo_completed"])),   "Completed",   "g"),
            (str(len(d["wo_in_progress"])), "In Progress", "b"),
            (str(len(d["wo_pending"])),     "Pending",     "a"),
            (str(len(d["wo_overdue"])),     "Overdue",     "r"),
        )}
        {table(["Work Order","Client","Status","Due","Value"], wo_rows)}
        {caveat("⚠ OVERDUE", ", ".join(w["title"] for w in d["wo_overdue"])) if d["wo_overdue"]
         else insight("✅ Operations", f'No overdue WOs. {len(d["wo_completed"])} completed this cycle.')}
        """

    # ── AT-RISK ───────────────────────────────────────────────────────
    if any(k in q for k in ("risk", "stall", "danger")):
        at_risk = [x for x in d["active_deals"] if (x.get("probability") or 50) < 45]
        risk_val = sum(x.get("value") or 0 for x in at_risk)
        rows = [[x["name"], x.get("sector","—"), fmt_val(x.get("value")),
                 badge(f'{x.get("probability","?")}%', "red"), x.get("owner","—")] for x in at_risk]
        return f"""
        {insight("⚠ At-Risk Deals (prob &lt; 45%)",
            f'{len(at_risk)} deals totaling {fmt_val(risk_val)} at risk of stalling.')}
        {table(["Deal","Sector","Value","Probability","Owner"], rows)}
        {insight("💡 Recommendation",
            "Schedule deal review meetings. Identify blockers per owner. "
            "Consider re-qualifying or offering revised proposals.")}
        """

    # ── FORECAST ─────────────────────────────────────────────────────
    if any(k in q for k in ("forecast", "revenue", "quarter")):
        weighted = sum((x.get("value") or 0) * (x.get("probability") or 50) / 100
                       for x in d["active_deals"])
        return f"""
        {metric_row(
            (fmt_val(d["total_pipeline"]), "Total Pipeline",    "b"),
            (fmt_val(weighted),            "Weighted Forecast", "g"),
            (fmt_val(d["won_value"]),      "Booked Revenue",    "a"),
        )}
        {insight("📈 Revenue Forecast",
            f'Expected (probability-weighted): <strong>{fmt_val(weighted)}</strong><br>'
            f'Best case (all close): <strong>{fmt_val(d["total_pipeline"] + d["won_value"])}</strong><br>'
            f'Conservative (won only): <strong>{fmt_val(d["won_value"])}</strong>'
        )}
        {caveat("⚠ CAVEAT", f'{d["null_values"]} deals missing values — forecast understated.') if d["null_values"] else ""}
        """

    # ── SECTOR ───────────────────────────────────────────────────────
    if "sector" in q:
        rows = []
        for sec, sd in sorted(d["sector_map"].items(), key=lambda x: -x[1]["value"]):
            active = len([dd for dd in sd["deals"] if dd.get("stage") not in ("Won","Lost")])
            rows.append([sec, str(len(sd["deals"])), fmt_val(sd["value"]), str(active)])
        return f"""
        <h4>Pipeline by Sector</h4>
        {table(["Sector","Total Deals","Pipeline Value","Active"], rows)}
        {insight("💡 Insight",
            "Energy leads pipeline. Growing presence in Logistics and Government indicates "
            "healthy sector diversification.")}
        """

    # ── DEFAULT ──────────────────────────────────────────────────────
    return f"""
    I'm ready to analyze your Skylark Drones data. Here's a quick snapshot:
    {metric_row(
        (fmt_val(d["total_pipeline"]), "Pipeline",    "b"),
        (str(len(d["won_deals"])),     "Deals Won",   "g"),
        (f'{d["win_rate"]}%',          "Win Rate",    "a"),
        (str(len(d["work_orders"])),   "Work Orders", "b"),
    )}
    <ul>
      <li>Ask about <strong>pipeline by sector</strong></li>
      <li>Ask about <strong>at-risk or stalling deals</strong></li>
      <li>Ask about <strong>work order status</strong></li>
      <li>Ask for a <strong>leadership update</strong></li>
      <li>Ask about <strong>revenue forecast</strong></li>
    </ul>
    """


# ─────────────────────────────────────────────
# GROK AI CLIENT
# ─────────────────────────────────────────────
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

def call_grok(query: str, stats: dict, history: list[dict], api_key: str) -> str:
    system_prompt = f"""You are Skylark BI, an elite business intelligence agent for Skylark Drones.

DEALS DATA ({len(stats["deals"])} records):
{json.dumps(stats["deals"][:15], indent=2)}

WORK ORDERS DATA ({len(stats["work_orders"])} records):
{json.dumps(stats["work_orders"][:15], indent=2)}

KEY METRICS:
- Active pipeline: {fmt_val(stats["total_pipeline"])}
- Win rate: {stats["win_rate"]}%
- Deals with missing values: {stats["null_values"]}
- Overdue work orders: {len(stats["wo_overdue"])}

RESPONSE RULES:
1. Answer with founder-level insight — the "so what", not raw data.
2. Use these HTML elements in your response:
   - <div class="metric-row"><div class="metric-chip"><div class="mc-val b|g|a|r">VALUE</div><div class="mc-label">LABEL</div></div></div>
   - <div class="insight-card"><div class="ic-title">TITLE</div>BODY</div>
   - <div class="caveat"><strong>TITLE</strong>BODY</div>
   - <table class="data-table"><tr><th>...</th></tr><tr><td>...</td></tr></table>
   - <span class="badge sky|green|amber|red">TEXT</span>
3. Surface data quality issues as caveats.
4. Never hallucinate — only use data provided above.
5. For leadership updates: Executive Summary → Top Deals → Ops Snapshot → Risks → Actions."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": query})

    resp = requests.post(
        GROK_API_URL,
        json={"model": "grok-3-latest", "messages": messages, "max_tokens": 1800, "temperature": 0.3},
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    has_builtin = bool(BUILTIN_GROK_KEY or BUILTIN_MONDAY_KEY)
    return render_template("index.html", has_builtin=has_builtin)


@app.route("/api/config/builtin", methods=["GET"])
def get_builtin_config():
    """Return whether built-in keys are configured (without exposing them)."""
    return jsonify({
        "has_grok":   bool(BUILTIN_GROK_KEY),
        "has_monday": bool(BUILTIN_MONDAY_KEY and BUILTIN_DEALS_BOARD and BUILTIN_WO_BOARD),
        "mode": "live" if (BUILTIN_MONDAY_KEY and BUILTIN_DEALS_BOARD and BUILTIN_WO_BOARD) else "demo",
    })


@app.route("/api/monday/fetch", methods=["POST"])
def api_fetch_monday():
    """Fetch live Monday.com data. Accepts user-supplied or uses built-in keys."""
    body = request.get_json() or {}
    monday_key    = body.get("monday_key") or BUILTIN_MONDAY_KEY
    deals_board   = body.get("deals_board_id") or BUILTIN_DEALS_BOARD
    wo_board      = body.get("wo_board_id") or BUILTIN_WO_BOARD

    if not all([monday_key, deals_board, wo_board]):
        return jsonify({"error": "Missing Monday.com credentials"}), 400

    try:
        raw_deals = fetch_monday_board(deals_board, monday_key)
        raw_wos   = fetch_monday_board(wo_board, monday_key)
        deals     = normalize_items(raw_deals)
        wos       = normalize_items(raw_wos)
        return jsonify({"deals": deals, "work_orders": wos, "source": "live"})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/data/demo", methods=["GET"])
def api_demo_data():
    """Return built-in sample data."""
    return jsonify({"deals": SAMPLE_DEALS, "work_orders": SAMPLE_WORK_ORDERS, "source": "demo"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Main chat endpoint.
    Body:
      query       str   — the user's question
      history     list  — prior conversation turns [{role, content}]
      data_mode   str   — "demo" | "live"
      deals       list  — if live, pass the fetched deals
      work_orders list  — if live, pass the fetched work orders
      grok_key    str   — optional; falls back to built-in
    """
    body        = request.get_json() or {}
    query       = body.get("query", "").strip()
    history     = body.get("history", [])
    data_mode   = body.get("data_mode", "demo")
    grok_key    = body.get("grok_key") or BUILTIN_GROK_KEY

    if not query:
        return jsonify({"error": "Empty query"}), 400

    # Choose data source
    if data_mode == "live":
        deals = body.get("deals", SAMPLE_DEALS)
        wos   = body.get("work_orders", SAMPLE_WORK_ORDERS)
    else:
        deals = SAMPLE_DEALS
        wos   = SAMPLE_WORK_ORDERS

    stats = compute_stats(deals, wos)

    # Try Grok, fall back to rule-based
    ai_used = False
    if grok_key:
        try:
            html_response = call_grok(query, stats, history, grok_key)
            ai_used = True
        except Exception as e:
            html_response = rule_based_response(query, stats)
            html_response += f'<div class="caveat"><strong>ℹ GROK FALLBACK</strong>AI unavailable ({e}). Rule-based analysis shown.</div>'
    else:
        html_response = rule_based_response(query, stats)
        html_response += '<div style="margin-top:10px;font-size:11px;color:var(--muted)">💡 Add a Grok API key for AI-powered natural language analysis.</div>'

    return jsonify({
        "response": html_response,
        "ai_used": ai_used,
        "stats": {
            "pipeline": stats["total_pipeline"],
            "win_rate": stats["win_rate"],
            "active_deals": len(stats["active_deals"]),
            "overdue_wos": len(stats["wo_overdue"]),
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🛸 Skylark BI Agent running at http://localhost:{port}\n")
    app.run(debug=True, port=port)
