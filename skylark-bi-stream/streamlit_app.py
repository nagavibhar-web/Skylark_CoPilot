"""
Skylark BI Agent — Streamlit Version
Run locally: streamlit run streamlit_app.py
Deploy:       Push to GitHub → connect to share.streamlit.io
"""

import streamlit as st
import requests
import json
import re
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Skylark BI",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'DM Mono', monospace !important; }
.stApp { background: #030712; }
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0c1220 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; font-family: 'DM Mono', monospace !important; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #0c1220 !important; color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(14,165,233,0.45) !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.08) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Mono', monospace !important;
    font-size: 13px !important; font-weight: 500 !important;
    padding: 8px 20px !important; transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* ── Chat messages ── */
.user-msg {
    background: linear-gradient(135deg,rgba(14,165,233,0.12),rgba(37,99,235,0.08));
    border: 1px solid rgba(14,165,233,0.2); border-radius: 12px 4px 12px 12px;
    padding: 14px 16px; margin: 8px 0; font-size: 13px;
    color: #f1f5f9; line-height: 1.75; max-width: 75%; margin-left: auto;
}
.bot-msg {
    background: #0c1220; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px 12px 12px 12px; padding: 14px 16px;
    margin: 8px 0; font-size: 13px; color: #f1f5f9; line-height: 1.75;
}
.msg-meta { font-size: 10px; color: #64748b; margin-bottom: 6px; letter-spacing: 0.3px; }

/* ── Cards & components ── */
.metric-card {
    background: #0c1220; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px 16px; text-align: center;
}
.metric-val { font-family: 'Syne', sans-serif !important; font-size: 24px; font-weight: 700; }
.metric-val.blue { color: #0ea5e9; } .metric-val.green { color: #22c55e; }
.metric-val.amber { color: #f59e0b; } .metric-val.red { color: #ef4444; }
.metric-label { font-size: 10px; color: #64748b; margin-top: 4px; letter-spacing: 0.5px; }

.insight-card {
    background: rgba(14,165,233,0.06); border: 1px solid rgba(14,165,233,0.2);
    border-left: 4px solid #0ea5e9; border-radius: 8px; padding: 12px 16px; margin: 10px 0;
}
.insight-title { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #0ea5e9; margin-bottom: 6px; font-weight: 600; }

.caveat-card {
    background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2);
    border-left: 4px solid #f59e0b; border-radius: 8px; padding: 10px 14px; margin: 8px 0;
    color: #f59e0b; font-size: 12px;
}

.data-table-wrapper { overflow-x: auto; margin: 10px 0; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th { background: rgba(14,165,233,0.08); color: #0ea5e9; padding: 8px 12px; text-align: left; font-size: 10px; letter-spacing: 0.8px; text-transform: uppercase; border-bottom: 1px solid rgba(14,165,233,0.2); }
.data-table td { padding: 7px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #94a3b8; }
.data-table tr:hover td { background: rgba(14,165,233,0.03); color: #f1f5f9; }

.badge { display:inline-block; padding:2px 8px; border-radius:5px; font-size:10px; font-weight:600; }
.badge-sky   { background:rgba(14,165,233,0.15); color:#0ea5e9; }
.badge-green { background:rgba(34,197,94,0.15);  color:#22c55e; }
.badge-amber { background:rgba(245,158,11,0.15); color:#f59e0b; }
.badge-red   { background:rgba(239,68,68,0.15);  color:#ef4444; }

.section-header {
    font-family: 'Syne', sans-serif !important; font-size: 14px; font-weight: 700;
    color: #f1f5f9; margin: 16px 0 8px; padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.chat-container { max-height: 60vh; overflow-y: auto; padding-right: 4px; }
.logo-text {
    font-family: 'Syne', sans-serif !important; font-size: 22px;
    font-weight: 800; color: #f1f5f9 !important; letter-spacing: -0.5px;
}
.logo-text span { color: #0ea5e9 !important; }
.pill {
    display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px;
    font-weight: 500; background: rgba(14,165,233,0.12);
    border: 1px solid rgba(14,165,233,0.2); color: #0ea5e9;
}
.pill-green { background: rgba(34,197,94,0.1); border-color: rgba(34,197,94,0.2); color: #22c55e; }
.divider { height:1px; background:rgba(255,255,255,0.07); margin:12px 0; }
.welcome-box {
    text-align: center; padding: 40px 20px;
    border: 1px solid rgba(255,255,255,0.07); border-radius: 16px;
    background: #0c1220; margin-bottom: 20px;
}
.welcome-icon { font-size: 48px; margin-bottom: 12px; }
.welcome-title { font-family:'Syne',sans-serif!important; font-size:26px; font-weight:800; color:#f1f5f9; margin-bottom:8px; }
.welcome-sub { color:#64748b; font-size:13px; line-height:1.7; max-width:480px; margin:0 auto; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SAMPLE DATA
# ─────────────────────────────────────────────────────────────────
SAMPLE_DEALS = [
    {"id":1,  "name":"TechCorp Phase 2",         "sector":"Technology",    "value":320000, "stage":"Proposal",    "owner":"Ankit S.",  "date":"2025-03-15","probability":65},
    {"id":2,  "name":"EnergyCo Solar Grid",       "sector":"Energy",        "value":480000, "stage":"Negotiation", "owner":"Priya R.",  "date":"2025-03-20","probability":80},
    {"id":3,  "name":"ManufactX Inspection",      "sector":"Manufacturing", "value":150000, "stage":"Won",         "owner":"Rahul K.",  "date":"2025-02-10","probability":100},
    {"id":4,  "name":"SkyLogistics Drone Survey", "sector":"Logistics",     "value":210000, "stage":"Proposal",    "owner":"Meera T.",  "date":"2025-03-28","probability":55},
    {"id":5,  "name":"GreenEnergy Windmill",      "sector":"Energy",        "value":395000, "stage":"Prospecting", "owner":"Ankit S.",  "date":"2025-04-01","probability":30},
    {"id":6,  "name":"BioTech Lab Mapping",       "sector":"Healthcare",    "value":175000, "stage":"Proposal",    "owner":"Priya R.",  "date":"2025-03-10","probability":60},
    {"id":7,  "name":"UrbanPlan City Survey",     "sector":"Government",    "value":520000, "stage":"Negotiation", "owner":"Rahul K.",  "date":"2025-02-25","probability":75},
    {"id":8,  "name":"OilRig Delta Inspection",   "sector":"Energy",        "value":290000, "stage":"Won",         "owner":"Meera T.",  "date":"2025-01-15","probability":100},
    {"id":9,  "name":"AgroFarm Mapping",          "sector":"Agriculture",   "value":95000,  "stage":"Lost",        "owner":"Ankit S.",  "date":"2025-02-05","probability":0},
    {"id":10, "name":"TelecomTower Audit",        "sector":"Telecom",       "value":130000, "stage":"Proposal",    "owner":"Priya R.",  "date":"2025-04-05","probability":50},
    {"id":11, "name":"RetailChain Inventory",     "sector":"Retail",        "value":None,   "stage":"Prospecting", "owner":"Rahul K.",  "date":None,        "probability":25},
    {"id":12, "name":"PortAuth Dock Survey",      "sector":"Logistics",     "value":240000, "stage":"Proposal",    "owner":"Meera T.",  "date":"2025-03-30","probability":70},
]

SAMPLE_WOS = [
    {"id":101,"title":"Solar Panel Array Survey","client":"EnergyCo",     "sector":"Energy",        "status":"In Progress","assignee":"Drone Team A","due":"2025-03-25","value":45000, "pct":60},
    {"id":102,"title":"Windmill Blade Inspection","client":"GreenEnergy", "sector":"Energy",        "status":"Completed",  "assignee":"Drone Team B","due":"2025-03-10","value":32000, "pct":100},
    {"id":103,"title":"Factory Roof Thermal Scan","client":"ManufactX",   "sector":"Manufacturing", "status":"Completed",  "assignee":"Drone Team A","due":"2025-02-28","value":28000, "pct":100},
    {"id":104,"title":"Logistics Hub Mapping",    "client":"SkyLogistics", "sector":"Logistics",     "status":"In Progress","assignee":"Drone Team C","due":"2025-03-20","value":38000, "pct":40},
    {"id":105,"title":"OilRig Safety Inspection", "client":"OilRig Delta", "sector":"Energy",        "status":"Overdue",    "assignee":"Drone Team B","due":"2025-03-05","value":62000, "pct":20},
    {"id":106,"title":"City Infrastructure Audit","client":"UrbanPlan",   "sector":"Government",    "status":"In Progress","assignee":"Drone Team A","due":"2025-04-10","value":85000, "pct":30},
    {"id":107,"title":"Crop Health Assessment",   "client":"AgroFarm",     "sector":"Agriculture",   "status":"Completed",  "assignee":"Drone Team C","due":"2025-02-20","value":18000, "pct":100},
    {"id":108,"title":"Telecom Tower Scan",       "client":"TelecomTower", "sector":"Telecom",       "status":"Pending",    "assignee":"Unassigned", "due":"2025-04-15","value":22000, "pct":0},
    {"id":109,"title":"BioLab Clean Room Survey", "client":"BioTech Lab",  "sector":"Healthcare",    "status":"In Progress","assignee":"Drone Team B","due":"2025-03-28","value":41000, "pct":55},
    {"id":110,"title":"Port Dock Perimeter Scan", "client":"PortAuth",     "sector":"Logistics",     "status":"Pending",    "assignee":"Drone Team A","due":"2025-04-20","value":35000, "pct":0},
    {"id":111,"title":"Retail Inventory Count",   "client":"RetailChain",  "sector":"Retail",        "status":"Overdue",    "assignee":"Drone Team C","due":"2025-03-01","value":None,  "pct":10},
    {"id":112,"title":"Solar Phase 2 Prep",       "client":"EnergyCo",     "sector":"Energy",        "status":"Pending",    "assignee":"Drone Team A","due":"2025-04-25","value":53000, "pct":0},
]


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def fmt(v):
    if v is None: return "N/A"
    if v >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if v >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"

def badge(text, color="sky"):
    cls = {"sky":"badge-sky","green":"badge-green","amber":"badge-amber","red":"badge-red"}.get(color,"badge-sky")
    return f'<span class="badge {cls}">{text}</span>'

def stage_color(s):
    s = (s or "").lower()
    if "won" in s:       return "green"
    if "lost" in s:      return "red"
    if "negotiation" in s: return "sky"
    if "overdue" in s:   return "red"
    if "complet" in s:   return "green"
    if "progress" in s:  return "sky"
    return "amber"

def mk_table(headers, rows):
    ths = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="data-table-wrapper"><table class="data-table"><tr>{ths}</tr>{trs}</table></div>'

def insight_card(title, body):
    return f'<div class="insight-card"><div class="insight-title">{title}</div>{body}</div>'

def caveat_card(title, body):
    return f'<div class="caveat-card"><strong>⚠ {title}</strong><br>{body}</div>'


# ─────────────────────────────────────────────────────────────────
# MONDAY.COM CLIENT
# ─────────────────────────────────────────────────────────────────
def fetch_monday_board(board_id, api_key):
    q = """
    query($ids:[ID!]!) {
      boards(ids:$ids) {
        items_page(limit:200) {
          items { id name column_values { id text column { title } } }
        }
      }
    }"""
    r = requests.post(
        "https://api.monday.com/v2",
        json={"query": q, "variables": {"ids": [str(board_id)]}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise ValueError(data["errors"][0]["message"])
    items = data["data"]["boards"][0]["items_page"]["items"]
    result = []
    for item in items:
        obj = {"name": item["name"]}
        for cv in item["column_values"]:
            k = cv["column"]["title"].lower().replace(" ", "_")
            v = cv["text"] or None
            if v in {"", "N/A", "n/a", "-", "—"}: v = None
            if v:
                cleaned = re.sub(r"[$,₹€£\s]", "", v)
                if re.fullmatch(r"-?\d+(\.\d+)?", cleaned):
                    v = float(cleaned)
            obj[k] = v
        result.append(obj)
    return result


# ─────────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────────
def compute_stats(deals, wos):
    active = [d for d in deals if d.get("stage") not in ("Won","Lost")]
    won    = [d for d in deals if d.get("stage") == "Won"]
    lost   = [d for d in deals if d.get("stage") == "Lost"]
    pipeline = sum(d.get("value") or 0 for d in active)
    won_val  = sum(d.get("value") or 0 for d in won)

    sectors = {}
    for d in deals:
        s = d.get("sector") or "Unknown"
        sectors.setdefault(s, {"deals":[], "value":0})
        sectors[s]["deals"].append(d)
        sectors[s]["value"] += d.get("value") or 0

    def wf(kw): return [w for w in wos if kw.lower() in (w.get("status") or "").lower()]
    denom = len(won) + len(lost)
    return {
        "deals": deals, "wos": wos,
        "active": active, "won": won, "lost": lost,
        "pipeline": pipeline, "won_val": won_val, "sectors": sectors,
        "wo_done": wf("complet"), "wo_prog": wf("progress"),
        "wo_over": wf("overdue"), "wo_pend": wf("pending"),
        "null_vals": sum(1 for d in deals if d.get("value") is None),
        "win_rate": round(len(won)/denom*100) if denom else 0,
    }


# ─────────────────────────────────────────────────────────────────
# RULE-BASED RESPONSE ENGINE
# ─────────────────────────────────────────────────────────────────
def rule_response(query: str, s: dict) -> str:
    q = query.lower()

    def metric_chips(*chips):
        cells = "".join(
            f'<div style="flex:1;min-width:90px;background:#111827;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:10px 12px;text-align:center">'
            f'<div class="metric-val {c[2]}" style="font-family:Syne,sans-serif;font-size:20px;font-weight:700">{c[0]}</div>'
            f'<div class="metric-label">{c[1]}</div></div>'
            for c in chips
        )
        return f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin:10px 0">{cells}</div>'

    # ── LEADERSHIP UPDATE ──────────────────────────────────────────
    if any(k in q for k in ("leadership","board update","weekly update","exec update","exec summary")):
        top = sorted(s["active"], key=lambda x: x.get("value") or 0, reverse=True)[:4]
        risk = [x for x in s["active"] if (x.get("probability") or 50) < 45]
        rows = [[x["name"], x.get("sector","—"), fmt(x.get("value")),
                 badge(x.get("stage","—"), stage_color(x.get("stage",""))),
                 f'{x.get("probability","?")}%'] for x in top]
        wo_rows = [[w["title"], w.get("client","—"),
                    badge(w.get("status","—"), stage_color(w.get("status",""))),
                    fmt(w.get("value"))] for w in s["wo_over"]]

        html = f"""
        <div class="section-header">📊 Weekly Leadership Update — Skylark Drones</div>
        {metric_chips(
            (fmt(s["pipeline"]), "Total Pipeline",   "blue"),
            (fmt(s["won_val"]),  "Won Revenue",      "green"),
            (f'{s["win_rate"]}%',"Win Rate",         "amber"),
            (str(len(s["wo_over"])), "WOs Overdue",  "red"),
        )}
        {insight_card("📌 Executive Summary",
            f'Pipeline at <strong>{fmt(s["pipeline"])}</strong> across <strong>{len(s["active"])}</strong> active deals. '
            f'Win rate <strong>{s["win_rate"]}%</strong>. '
            + (f'<strong style="color:#ef4444">{len(s["wo_over"])} work order(s) overdue</strong> — requires immediate action.'
               if s["wo_over"] else "All work orders on track.")
        )}
        <div class="section-header">🏆 Top Active Deals</div>
        {mk_table(["Deal","Sector","Value","Stage","Prob."], rows)}
        <div class="section-header">🔧 Operations Snapshot</div>
        {metric_chips(
            (str(len(s["wo_done"])), "Completed",   "green"),
            (str(len(s["wo_prog"])), "In Progress", "blue"),
            (str(len(s["wo_pend"])), "Pending",     "amber"),
            (str(len(s["wo_over"])), "Overdue",     "red"),
        )}
        {(mk_table(["Work Order","Client","Status","Value"], wo_rows)) if s["wo_over"] else ""}
        {caveat_card("DEALS AT RISK", ", ".join(f'{x["name"]} ({x.get("probability","?")}%)' for x in risk)) if risk else ""}
        {caveat_card("DATA QUALITY", f'{s["null_vals"]} deal(s) missing value data — totals may be understated.') if s["null_vals"] else ""}
        {insight_card("🎯 Recommended Actions",
            f'1. Follow up on <strong>{len(risk)}</strong> at-risk deals before quarter end<br>'
            f'2. Resolve <strong>{len(s["wo_over"])}</strong> overdue work orders<br>'
            f'3. {len([x for x in s["active"] if x.get("stage")=="Negotiation"])} deals in Negotiation — prioritize close<br>'
            f'4. Energy sector leads pipeline — monitor concentration risk'
        )}"""
        return html

    # ── ENERGY ────────────────────────────────────────────────────
    if "energy" in q:
        ed = s["sectors"].get("Energy", {}).get("deals", [])
        ea = [x for x in ed if x.get("stage") not in ("Won","Lost")]
        ev = sum(x.get("value") or 0 for x in ea)
        ew = [w for w in s["wos"] if (w.get("sector") or "").lower() == "energy"]
        rows = [[x["name"], fmt(x.get("value")), badge(x.get("stage","—"), stage_color(x.get("stage",""))),
                 x.get("owner","—"), f'{x.get("probability","?")}%'] for x in ed]
        wo_rows = [[w["title"], w.get("client","—"),
                    badge(w.get("status","—"), stage_color(w.get("status",""))),
                    fmt(w.get("value"))] for w in ew]
        return f"""
        {insight_card("⚡ Energy Sector Pipeline",
            f'<strong>{len(ed)}</strong> total · <strong>{len(ea)}</strong> active · Pipeline: <strong>{fmt(ev)}</strong>')}
        {mk_table(["Deal","Value","Stage","Owner","Prob."], rows)}
        <div class="section-header">🔧 Energy Work Orders ({len(ew)})</div>
        {mk_table(["Work Order","Client","Status","Value"], wo_rows)}
        {insight_card("💡 Key Insight",
            f'Energy leads your pipeline. {len([x for x in ea if x.get("stage")=="Negotiation"])} deal(s) in Negotiation — strong Q2 close potential.')}"""

    # ── PIPELINE / DEALS ──────────────────────────────────────────
    if any(k in q for k in ("pipeline","deal","proposal","top deal","stage")):
        by_stage = {}
        for d in s["deals"]: by_stage.setdefault(d.get("stage","Unknown"), []).append(d)
        stage_rows = []
        for stage, items in by_stage.items():
            tot = sum(x.get("value") or 0 for x in items)
            wv = [x for x in items if x.get("value")]
            avg = tot/len(wv) if wv else None
            stage_rows.append([badge(stage, stage_color(stage)), str(len(items)), fmt(tot), fmt(avg)])
        top5 = sorted(s["active"], key=lambda x: x.get("value") or 0, reverse=True)[:5]
        top_rows = [[x["name"], x.get("sector","—"), fmt(x.get("value")),
                     badge(x.get("stage","—"), stage_color(x.get("stage",""))),
                     f'{x.get("probability","?")}%'] for x in top5]
        return f"""
        {metric_chips(
            (fmt(s["pipeline"]),     "Active Pipeline","blue"),
            (str(len(s["won"])),     "Deals Won",      "green"),
            (f'{s["win_rate"]}%',    "Win Rate",       "amber"),
            (str(len(s["lost"])),    "Deals Lost",     "red"),
        )}
        <div class="section-header">Pipeline by Stage</div>
        {mk_table(["Stage","Count","Total Value","Avg. Value"], stage_rows)}
        <div class="section-header">Top 5 Active Deals</div>
        {mk_table(["Deal","Sector","Value","Stage","Prob."], top_rows)}
        {caveat_card("DATA QUALITY", f'{s["null_vals"]} deal(s) missing value data.') if s["null_vals"] else ""}"""

    # ── WORK ORDERS ───────────────────────────────────────────────
    if any(k in q for k in ("work order","wo ","operation","overdue","complet","assignee")):
        rows = [[w["title"], w.get("client","—"),
                 badge(w.get("status","—"), stage_color(w.get("status",""))),
                 w.get("due","—"), fmt(w.get("value"))] for w in s["wos"]]
        return f"""
        {metric_chips(
            (str(len(s["wo_done"])), "Completed",   "green"),
            (str(len(s["wo_prog"])), "In Progress", "blue"),
            (str(len(s["wo_pend"])), "Pending",     "amber"),
            (str(len(s["wo_over"])), "Overdue",     "red"),
        )}
        {mk_table(["Work Order","Client","Status","Due","Value"], rows)}
        {caveat_card("OVERDUE", ", ".join(w["title"] for w in s["wo_over"])) if s["wo_over"]
         else insight_card("✅ Operations Status", f'No overdue WOs. {len(s["wo_done"])} completed this cycle.')}"""

    # ── AT-RISK ───────────────────────────────────────────────────
    if any(k in q for k in ("risk","stall","danger","low prob")):
        risk = [x for x in s["active"] if (x.get("probability") or 50) < 45]
        rv = sum(x.get("value") or 0 for x in risk)
        rows = [[x["name"], x.get("sector","—"), fmt(x.get("value")),
                 badge(f'{x.get("probability","?")}%',"red"), x.get("owner","—")] for x in risk]
        return f"""
        {insight_card("⚠ At-Risk Deals (probability < 45%)",
            f'<strong>{len(risk)}</strong> deals totaling <strong>{fmt(rv)}</strong> at risk of stalling.')}
        {mk_table(["Deal","Sector","Value","Probability","Owner"], rows)}
        {insight_card("💡 Recommendation",
            "Schedule deal review sessions. Identify blockers per owner and consider revised proposals.")}"""

    # ── FORECAST ─────────────────────────────────────────────────
    if any(k in q for k in ("forecast","revenue","quarter","projection")):
        wt = sum((x.get("value") or 0)*(x.get("probability") or 50)/100 for x in s["active"])
        return f"""
        {metric_chips(
            (fmt(s["pipeline"]),         "Total Pipeline",    "blue"),
            (fmt(wt),                    "Weighted Forecast", "green"),
            (fmt(s["won_val"]),          "Booked Revenue",    "amber"),
        )}
        {insight_card("📈 Revenue Forecast",
            f'Probability-weighted forecast: <strong>{fmt(wt)}</strong><br>'
            f'Best case (all close): <strong>{fmt(s["pipeline"]+s["won_val"])}</strong><br>'
            f'Conservative (won only): <strong>{fmt(s["won_val"])}</strong>'
        )}
        {caveat_card("CAVEAT", f'{s["null_vals"]} deals missing values — forecast understated.') if s["null_vals"] else ""}"""

    # ── SECTOR ───────────────────────────────────────────────────
    if "sector" in q:
        rows = [[sec, str(len(sd["deals"])), fmt(sd["value"]),
                 str(len([d for d in sd["deals"] if d.get("stage") not in ("Won","Lost")]))]
                for sec, sd in sorted(s["sectors"].items(), key=lambda x:-x[1]["value"])]
        return f"""
        <div class="section-header">Pipeline by Sector</div>
        {mk_table(["Sector","Total Deals","Pipeline Value","Active"], rows)}
        {insight_card("💡 Insight","Energy leads pipeline. Logistics and Government growing — healthy diversification.")}"""

    # ── DEFAULT ──────────────────────────────────────────────────
    return f"""
    Welcome! Here's a quick snapshot of your Skylark Drones data:
    {metric_chips(
        (fmt(s["pipeline"]),     "Pipeline",    "blue"),
        (str(len(s["won"])),     "Deals Won",   "green"),
        (f'{s["win_rate"]}%',    "Win Rate",    "amber"),
        (str(len(s["wos"])),     "Work Orders", "blue"),
    )}
    <br>Try asking:<br>
    • <em>How is our energy sector pipeline this quarter?</em><br>
    • <em>Which deals are at risk?</em><br>
    • <em>Work order status summary</em><br>
    • <em>Generate a leadership update</em><br>
    • <em>Revenue forecast for next quarter</em>"""


# ─────────────────────────────────────────────────────────────────
# GROK AI
# ─────────────────────────────────────────────────────────────────
def call_grok(query, stats, history, api_key):
    sys_prompt = f"""You are Skylark BI, an elite business intelligence agent for Skylark Drones.

DEALS ({len(stats["deals"])} records): {json.dumps(stats["deals"][:14], indent=2)}
WORK ORDERS ({len(stats["wos"])} records): {json.dumps(stats["wos"][:12], indent=2)}

KEY METRICS:
- Active pipeline: {fmt(stats["pipeline"])}
- Win rate: {stats["win_rate"]}%
- Deals missing values: {stats["null_vals"]}
- Overdue work orders: {len(stats["wo_over"])}

RULES:
1. Founder-level insight — the "so what", not raw data.
2. Use these HTML tags in your response:
   - <div class="insight-card"><div class="insight-title">TITLE</div>BODY</div>
   - <div class="caveat-card"><strong>⚠ TITLE</strong><br>BODY</div>
   - <div class="data-table-wrapper"><table class="data-table">...</table></div>
   - <span class="badge badge-sky|badge-green|badge-amber|badge-red">TEXT</span>
3. Surface data quality issues as caveats.
4. NEVER hallucinate — only use data provided.
5. Leadership updates: Executive Summary → Top Deals → Ops Snapshot → Risks → Actions."""

    messages = [{"role":"system","content":sys_prompt}]
    messages.extend(history[-6:])
    messages.append({"role":"user","content":query})

    r = requests.post(
        "https://api.x.ai/v1/chat/completions",
        json={"model":"grok-3-latest","messages":messages,"max_tokens":1800,"temperature":0.3},
        headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:     st.session_state.messages = []
if "deals" not in st.session_state:        st.session_state.deals = SAMPLE_DEALS
if "wos" not in st.session_state:          st.session_state.wos = SAMPLE_WOS
if "data_mode" not in st.session_state:    st.session_state.data_mode = "demo"
if "grok_key" not in st.session_state:     st.session_state.grok_key = ""
if "monday_key" not in st.session_state:   st.session_state.monday_key = ""
if "deals_board" not in st.session_state:  st.session_state.deals_board = ""
if "wo_board" not in st.session_state:     st.session_state.wo_board = ""

# Load secrets if available (Streamlit Cloud)
try:
    if not st.session_state.grok_key:
        st.session_state.grok_key = st.secrets.get("GROK_API_KEY", "")
    if not st.session_state.monday_key:
        st.session_state.monday_key = st.secrets.get("MONDAY_API_KEY", "")
    if not st.session_state.deals_board:
        st.session_state.deals_board = st.secrets.get("DEALS_BOARD_ID", "")
    if not st.session_state.wo_board:
        st.session_state.wo_board = st.secrets.get("WO_BOARD_ID", "")
except Exception:
    pass

# Auto-connect if built-in keys present
if (st.session_state.monday_key and st.session_state.deals_board
        and st.session_state.wo_board and st.session_state.data_mode == "demo"):
    try:
        st.session_state.deals = fetch_monday_board(st.session_state.deals_board, st.session_state.monday_key)
        st.session_state.wos   = fetch_monday_board(st.session_state.wo_board,   st.session_state.monday_key)
        st.session_state.data_mode = "live"
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    stats = compute_stats(st.session_state.deals, st.session_state.wos)

    st.markdown('<div class="logo-text">🛸 Skylark <span>BI</span></div>', unsafe_allow_html=True)

    mode_label = "🟢 LIVE MODE" if st.session_state.data_mode == "live" else "🟡 DEMO MODE"
    st.markdown(f'<span class="pill {"pill-green" if st.session_state.data_mode=="live" else ""}">{mode_label}</span>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Stats ──
    st.markdown('<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;margin-bottom:8px">Pipeline Overview</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val blue">{fmt(stats["pipeline"])}</div><div class="metric-label">PIPELINE</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val amber">{stats["win_rate"]}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-val green">{len(stats["active"])}</div><div class="metric-label">ACTIVE DEALS</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-val red">{len(stats["wo_over"])}</div><div class="metric-label">WOs OVERDUE</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Quick queries ──
    st.markdown('<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;margin-bottom:8px">Quick Queries</div>', unsafe_allow_html=True)
    quick_queries = [
        ("⚡", "Energy pipeline"),
        ("💰", "Top deals by value"),
        ("📋", "Work order status"),
        ("⚠️", "At-risk deals"),
        ("📊", "Leadership update"),
        ("📈", "Revenue forecast"),
    ]
    for icon, label in quick_queries:
        if st.button(f"{icon} {label}", key=f"q_{label}", use_container_width=True):
            st.session_state["pending_query"] = label

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── API Config ──
    st.markdown('<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;margin-bottom:8px">API Configuration</div>', unsafe_allow_html=True)

    cfg_mode = st.radio("Mode", ["🎭 Demo", "🔗 Live (Monday.com)"], horizontal=True,
                        label_visibility="collapsed")

    if "Demo" in cfg_mode:
        gk = st.text_input("Grok API Key (optional)", type="password",
                            value=st.session_state.grok_key,
                            placeholder="xai-... enhances responses")
        if st.button("✓ Apply", key="apply_demo"):
            st.session_state.grok_key = gk
            st.session_state.data_mode = "demo"
            st.session_state.deals = SAMPLE_DEALS
            st.session_state.wos   = SAMPLE_WOS
            st.success("Demo mode set!")
    else:
        mk  = st.text_input("Monday.com Token", type="password",
                             value=st.session_state.monday_key, placeholder="eyJhbGci...")
        db  = st.text_input("Deals Board ID",   value=st.session_state.deals_board, placeholder="1234567890")
        wb  = st.text_input("Work Orders Board ID", value=st.session_state.wo_board, placeholder="9876543210")
        gk2 = st.text_input("Grok API Key",     type="password",
                             value=st.session_state.grok_key, placeholder="xai-...")
        if st.button("🔗 Connect Live", key="connect_live"):
            with st.spinner("Connecting to Monday.com…"):
                try:
                    deals = fetch_monday_board(db, mk)
                    wos_  = fetch_monday_board(wb, mk)
                    st.session_state.update({
                        "monday_key": mk, "deals_board": db, "wo_board": wb,
                        "grok_key": gk2, "deals": deals, "wos": wos_,
                        "data_mode": "live",
                    })
                    st.success(f"✓ Connected! {len(deals)} deals, {len(wos_)} work orders")
                    st.rerun()
                except Exception as e:
                    st.error(f"✗ {e}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("↺ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Connection status
    mon_ok = st.session_state.data_mode == "live"
    ai_ok  = bool(st.session_state.grok_key)
    st.markdown(f"""
    <div style="font-size:11px;color:#64748b;padding:4px 0">
      {'🟢' if mon_ok else '🟡'} Monday.com: {'Connected' if mon_ok else 'Demo data'}<br>
      {'🟢' if ai_ok  else '🟡'} Grok AI: {'Connected' if ai_ok  else 'Not configured'}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# MAIN CHAT AREA
# ─────────────────────────────────────────────────────────────────
stats = compute_stats(st.session_state.deals, st.session_state.wos)

# Header row
hcol1, hcol2 = st.columns([3, 1])
with hcol1:
    st.markdown('<div class="logo-text" style="font-size:18px">🛸 Skylark Business Intelligence</div>', unsafe_allow_html=True)
with hcol2:
    st.markdown(f'<div style="text-align:right;padding-top:4px"><span class="pill {"pill-green" if st.session_state.data_mode=="live" else ""}">{"🟢 LIVE" if st.session_state.data_mode=="live" else "🟡 DEMO"}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Welcome screen
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
      <div class="welcome-icon">🛸</div>
      <div class="welcome-title">Your Business Intelligence Co-pilot</div>
      <div class="welcome-sub">Ask me anything about your Monday.com pipeline, deals, and work orders.<br>I query live data and give you founder-level insights.</div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(2)
    suggestions = [
        ("⚡ SECTOR ANALYSIS", "Energy sector pipeline this quarter",     "How is our energy sector pipeline looking this quarter?"),
        ("💼 DEAL REVIEW",     "Deals in proposal stage with values",     "Show me all deals in proposal stage with their values"),
        ("🚨 OPERATIONS",      "Overdue or at-risk work orders",          "What work orders are overdue or at risk?"),
        ("📊 LEADERSHIP",      "Weekly leadership update report",         "Generate a leadership update for this week"),
    ]
    for i, (title, desc, full_q) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"**{title}**\n{desc}", key=f"sug_{i}", use_container_width=True):
                st.session_state["pending_query"] = full_q

# Render chat history
chat_area = st.container()
with chat_area:
    for msg in st.session_state.messages:
        ts = msg.get("time","")
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg"><div class="msg-meta">You · {ts}</div>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg"><div class="msg-meta">🛸 Skylark BI · {ts}</div>{msg["content"]}</div>', unsafe_allow_html=True)

# ── Input row ──────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
inp_col, btn_col = st.columns([5, 1])
with inp_col:
    user_input = st.text_input(
        "query",
        label_visibility="collapsed",
        placeholder="Ask about pipeline, deals, work orders, revenue, sectors…",
        key="chat_input",
    )
with btn_col:
    send = st.button("➤ Send", use_container_width=True)

# Hint chips
h1, h2, h3, h4, h5 = st.columns(5)
with h1:
    if st.button("Pipeline by sector", key="h1"):  st.session_state["pending_query"] = "Pipeline by sector"
with h2:
    if st.button("Top 5 deals",        key="h2"):  st.session_state["pending_query"] = "Top 5 deals by value"
with h3:
    if st.button("WO status",          key="h3"):  st.session_state["pending_query"] = "Work order status summary"
with h4:
    if st.button("Revenue at risk",    key="h4"):  st.session_state["pending_query"] = "Revenue at risk"
with h5:
    if st.button("Leadership update",  key="h5"):  st.session_state["pending_query"] = "Generate a leadership update for this week"


# ─────────────────────────────────────────────────────────────────
# PROCESS QUERY
# ─────────────────────────────────────────────────────────────────
query_to_run = None
if send and user_input.strip():
    query_to_run = user_input.strip()
elif "pending_query" in st.session_state:
    query_to_run = st.session_state.pop("pending_query")

if query_to_run:
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role":"user","content":query_to_run,"time":now})

    with st.spinner("🛸 Analyzing your data…"):
        history = [{"role": m["role"], "content": m["content"]}
                   for m in st.session_state.messages[:-1][-6:]]

        gk = st.session_state.grok_key
        if gk:
            try:
                response = call_grok(query_to_run, stats, history, gk)
            except Exception as e:
                response = rule_response(query_to_run, stats)
                response += caveat_card("GROK FALLBACK", f"AI unavailable ({e}). Rule-based analysis shown.")
        else:
            response = rule_response(query_to_run, stats)
            response += '<div style="margin-top:10px;font-size:11px;color:#64748b">💡 Add a Grok API key in the sidebar for AI-powered natural language analysis.</div>'

    st.session_state.messages.append({"role":"assistant","content":response,"time":now})
    st.rerun()
