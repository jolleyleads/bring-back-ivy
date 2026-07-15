# DOE James Jolley Command Center Flask app
# Replace your repo's app.py with this file, commit, and Render will redeploy.

import os
from pathlib import Path
import json
import requests
from openai import OpenAI
import json
from datetime import datetime
from uuid import uuid4
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "dashboard_data.json"

CASE_CATEGORIES = [
    "Evidence", "Witness Statement", "Law Enforcement Contact", "Prosecutor Contact",
    "Court Event", "Grand Jury Information", "Media Coverage", "Timeline Event",
    "Legal Question", "Civil Case Information", "Follow Up Needed",
]

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def new_id(prefix): return f"{prefix}_{uuid4().hex[:10]}"

def empty_db():
    return {
        "case_name":"James Michael Jolley Case Files",
        "victim":"James Michael Jolley",
        "date_of_death":"2025-10-11",
        "reported_cause":"Reported fentanyl overdose",
        "contacts":[], "media_contacts":[], "emails":[], "followups":[], "case_updates":[],
        "evidence":[], "witnesses":[], "timeline":[], "law_enforcement_contacts":[],
        "prosecutor_contacts":[], "court_events":[], "grand_jury":[],
        "civil_case_information":[], "legal_questions":[], "contradictions":[], "activity":[]
    }

def normalize_db(db):
    base = empty_db()
    if not isinstance(db, dict): return base
    for k,v in base.items(): db.setdefault(k,v)
    if db.get("contacts") and not db.get("media_contacts"):
        db["media_contacts"] = db["contacts"]
    return db

def load_db():
    if not os.path.exists(DB): return empty_db()
    try:
        with open(DB,"r",encoding="utf-8") as f: return normalize_db(json.load(f))
    except Exception:
        return empty_db()

def save_db(db):
    with open(DB,"w",encoding="utf-8") as f: json.dump(normalize_db(db), f, indent=2, ensure_ascii=False)

def add_activity(db,msg):
    db["activity"].insert(0,{"id":new_id("act"),"time":now(),"message":msg})

def clean(data, category=None, prefix="rec"):
    r = dict(data or {})
    r.setdefault("id", new_id(prefix)); r.setdefault("created_at", now())
    if category: r.setdefault("category", category)
    r.setdefault("source", "Command Center"); r.setdefault("importance", "Medium")
    return r

def infer_category(text):
    t=(text or "").lower()
    if "grand jury" in t or "indict" in t: return "Grand Jury Information"
    if "court" in t or "hearing" in t or "judge" in t: return "Court Event"
    if "detective" in t or "police" in t: return "Law Enforcement Contact"
    if "prosecutor" in t or "commonwealth" in t or "attorney" in t: return "Prosecutor Contact"
    if "witness" in t or "statement" in t: return "Witness Statement"
    if "media" in t or "reporter" in t or "news" in t: return "Media Coverage"
    if "follow" in t or "next action" in t: return "Follow Up Needed"
    if "evidence" in t or "phone" in t or "text" in t or "ring" in t or "toxicology" in t: return "Evidence"
    return "Timeline Event"

def route_case_update(db, record):
    category = record.get("category") or infer_category(record.get("summary") or record.get("description") or record.get("text"))
    record["category"] = category
    db["case_updates"].insert(0, record)
    mapping = {
        "Evidence":"evidence", "Witness Statement":"witnesses", "Law Enforcement Contact":"law_enforcement_contacts",
        "Prosecutor Contact":"prosecutor_contacts", "Court Event":"court_events", "Grand Jury Information":"grand_jury",
        "Legal Question":"legal_questions", "Civil Case Information":"civil_case_information", "Follow Up Needed":"followups"
    }
    if category in mapping: db[mapping[category]].insert(0, record)
    if record.get("date") or record.get("event_date"):
        db["timeline"].insert(0,{
            "id":new_id("time"), "date":record.get("date") or record.get("event_date"), "time":record.get("time",""),
            "location":record.get("location",""), "people_involved":record.get("people_involved", record.get("people", [])),
            "description":record.get("summary") or record.get("description") or record.get("text", ""),
            "supporting_evidence":record.get("supporting_evidence", record.get("evidence", "")),
            "source_record_id":record["id"], "created_at":now()
        })
    return record

@app.route("/")
def home():
    db=load_db()
    stats = {
        "Media Contacts":len(db["media_contacts"]),
        "Case Updates":len(db["case_updates"]),
        "Evidence":len(db["evidence"]),
        "Witnesses":len(db["witnesses"]),
        "Timeline":len(db["timeline"]),
        "Grand Jury":len(db["grand_jury"]),
        "Court Events":len(db["court_events"]),
        "Follow-Ups":len(db["followups"])
    }

    def card(title, count, icon):
        return f"""
        <div class='stat-card'>
            <div class='icon'>{icon}</div>
            <div>
                <div class='count'>{count}</div>
                <div class='label'>{title}</div>
            </div>
        </div>
        """

    recent = ""
    for a in db["activity"][:12]:
        recent += f"<li><b>{a.get('time','')}</b><br>{a.get('message','')}</li>"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<title>James Jolley Command Center</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
    margin:0;
    font-family:Arial, sans-serif;
    background:#0b1020;
    color:white;
}}
.header {{
    padding:24px;
    background:linear-gradient(135deg,#111827,#1e3a8a);
}}
.header h1 {{margin:0;font-size:28px;}}
.header p {{margin:8px 0 0;color:#cbd5e1;}}
.nav {{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    padding:16px 24px;
    background:#111827;
}}
.nav a {{
    color:white;
    text-decoration:none;
    background:#2563eb;
    padding:10px 14px;
    border-radius:8px;
    font-weight:bold;
}}
.container {{padding:24px;}}
.grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:16px;
}}
.stat-card {{
    background:#111827;
    border:1px solid #334155;
    border-radius:14px;
    padding:18px;
    display:flex;
    gap:14px;
    align-items:center;
}}
.icon {{font-size:28px;}}
.count {{font-size:28px;font-weight:bold;}}
.label {{color:#cbd5e1;}}
.section {{
    margin-top:24px;
    background:#111827;
    border:1px solid #334155;
    border-radius:14px;
    padding:18px;
}}
.buttons {{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:12px;
}}
.button {{
    background:#1f2937;
    border:1px solid #475569;
    padding:14px;
    border-radius:10px;
    color:white;
    text-decoration:none;
    font-weight:bold;
}}
.green {{background:#166534;}}
.gold {{background:#92400e;}}
.red {{background:#7f1d1d;}}
ul {{padding-left:20px;}}
li {{margin-bottom:12px;color:#e5e7eb;}}
.small {{color:#94a3b8;font-size:13px;}}
</style>
</head>
<body>

<div class="header">
    <h1>James Jolley Command Center</h1>
    <p>DOE Case Files + Media Outreach + Business CRM</p>
</div>

<div class="nav">
    <a href="/">Dashboard</a>
    <a href="/api/db">Database</a>
    <a href="/api/report">Case Report</a>
    <a href="/api/health">Health</a>
</div>

<div class="container">

    <div class="grid">
        {card("Media Contacts",stats["Media Contacts"],"??")}
        {card("Case Updates",stats["Case Updates"],"??")}
        {card("Evidence",stats["Evidence"],"??")}
        {card("Witnesses",stats["Witnesses"],"??")}
        {card("Timeline",stats["Timeline"],"??")}
        {card("Grand Jury",stats["Grand Jury"],"??")}
        {card("Court Events",stats["Court Events"],"???")}
        {card("Follow-Ups",stats["Follow-Ups"],"?")}
    </div>

    <div class="section">
        <h2>Quick Actions</h2>
        <div class="buttons">
            <a class="button green" href="/api/media-contact">View Media Contacts</a>
            <a class="button" href="/api/timeline">View Timeline</a>
            <a class="button" href="/api/evidence">View Evidence</a>
            <a class="button" href="/api/witness">View Witnesses</a>
            <a class="button gold" href="/api/grand-jury">View Grand Jury</a>
            <a class="button red" href="/api/followup">View Follow-Ups</a>
        </div>
        <p class="small">Add records through Make.com HTTP modules or direct API POST requests.</p>
    </div>

    <div class="section">
        <h2>System Status</h2>
        <p>? Command Center API live</p>
        <p>? Make.com connected</p>
        <p>? Gmail draft automation working</p>
        <p>? Iterator creates one draft per contact</p>
    </div>

    <div class="section">
        <h2>Recent Activity</h2>
        <ul>{recent}</ul>
    </div>

</div>
</body>
</html>
"""
    return html
@app.route("/api/health")
def health(): return jsonify({"success":True,"time":now()})
@app.route("/api/db")
def get_db(): return jsonify(load_db())
@app.route("/api/report")
def report():
    db=load_db()
    return jsonify({"success":True,"executive_summary":{"victim":db["victim"],"date_of_death":db["date_of_death"],"reported_cause":db["reported_cause"]},"timeline":db["timeline"],"evidence_inventory":db["evidence"],"witness_information":db["witnesses"],"law_enforcement_actions":db["law_enforcement_contacts"],"prosecutor_actions":db["prosecutor_contacts"],"court_events":db["court_events"],"grand_jury_information":db["grand_jury"],"media_contacts":db["media_contacts"],"outstanding_questions":db["legal_questions"],"recommended_follow_up":db["followups"],"contradictions":db["contradictions"]})

@app.route("/api/case-update", methods=["POST"])
def case_update():
    db=load_db(); rec=clean(request.get_json(silent=True) or {}, prefix="case"); route_case_update(db,rec); add_activity(db,f"New case update saved: {rec.get('category')}"); save_db(db); return jsonify({"success":True,"record":rec})
@app.route("/add-case-update", methods=["POST"])
def add_case_update_alias(): return case_update()

def simple_collection(route, key, category, prefix):
    def handler():
        db=load_db()
        if request.method=="GET": return jsonify({"success":True,key:db[key]})
        rec=clean(request.get_json(silent=True) or {}, category, prefix); db[key].insert(0,rec); db["case_updates"].insert(0,rec); add_activity(db,f"{category} added"); save_db(db); return jsonify({"success":True,"record":rec})
    handler.__name__ = f"handler_{key}"
    app.route(route, methods=["GET","POST"])(handler)

simple_collection("/api/evidence","evidence","Evidence","ev")
simple_collection("/api/timeline","timeline","Timeline Event","time")
simple_collection("/api/witness","witnesses","Witness Statement","wit")
simple_collection("/api/court-event","court_events","Court Event","court")
simple_collection("/api/grand-jury","grand_jury","Grand Jury Information","gj")
simple_collection("/api/followup","followups","Follow Up Needed","fu")
simple_collection("/api/contradiction","contradictions","Follow Up Needed","con")

@app.route("/api/media-contact", methods=["GET","POST"])
def media_contact():
    db=load_db()
    if request.method=="GET": return jsonify({"success":True,"media_contacts":db["media_contacts"]})
    data=request.get_json(silent=True) or {}; contacts=data.get("contacts") if isinstance(data,dict) else None
    if not isinstance(contacts,list): contacts=[data]
    saved=[]
    for item in contacts:
        rec=clean(item,"Media Coverage","media"); rec.setdefault("case", data.get("case","James Michael Jolley") if isinstance(data,dict) else "James Michael Jolley")
        db["media_contacts"].insert(0,rec); db["contacts"].insert(0,rec); saved.append(rec)
    add_activity(db,f"Media contacts added: {len(saved)}"); save_db(db); return jsonify({"success":True,"count":len(saved),"records":saved})


@app.route("/api/update-media-contact", methods=["POST"])
def update_media_contact():
    db = load_db()
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    status = data.get("status", "Draft Created")
    draft_id = data.get("draft_id", "")
    notes = data.get("notes", "")

    if not email:
        return jsonify({"success": False, "error": "email required"}), 400

    updated = 0

    for contact in db.get("media_contacts", []):
        if contact.get("email", "").strip().lower() == email:
            contact["status"] = status
            contact["draft_created_at"] = now()
            if draft_id:
                contact["draft_id"] = draft_id
            if notes:
                contact["notes"] = notes
            updated += 1

    for contact in db.get("contacts", []):
        if contact.get("email", "").strip().lower() == email:
            contact["status"] = status
            contact["draft_created_at"] = now()
            if draft_id:
                contact["draft_id"] = draft_id
            if notes:
                contact["notes"] = notes

    add_activity(db, f"Media contact marked {status}: {email}")
    save_db(db)

    return jsonify({"success": True, "updated": updated, "email": email, "status": status}), 200
@app.route("/api/email-sent", methods=["POST"])
def email_sent():
    db=load_db(); rec=clean(request.get_json(silent=True) or {},"Media Coverage","email"); db["emails"].insert(0,rec); add_activity(db,"Email activity logged"); save_db(db); return jsonify({"success":True,"record":rec})


@app.route("/ai-intake", methods=["GET", "POST"])
def ai_intake():
    try:
        if request.method == "GET":
            return jsonify({
                "ok": True,
                "route": "/ai-intake",
                "message": "AI intake endpoint is live. Send POST JSON with a request field."
            })

        data = request.get_json(silent=True) or {}
        user_request = (data.get("request") or data.get("message") or "").strip()
        memory_context = summarize_ai_memory()

        if not user_request:
            return jsonify({"ok": False, "error": "Missing request text"}), 400

        make_webhook_url = os.getenv("MAKE_WEBHOOK_URL") or os.getenv("MAKE_OUTREACH_WEBHOOK_URL")
        if not make_webhook_url:
            return jsonify({"ok": False, "error": "Missing MAKE_WEBHOOK_URL environment variable"}), 500

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({"ok": False, "error": "Missing OPENAI_API_KEY environment variable"}), 500

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are the AI command console for the James Law Command Center.

Use recent memory to understand references like:
- "the last one"
- "same email as yesterday"
- "more reporters like that"
- "follow up with everyone who has not replied"
- "use the same angle but target legislators"

Recent command memory:
{memory_context}

Extract an outreach contact/action from the current request.

Return ONLY valid JSON with these keys:
Name, Organization, Type, Email, Phone, Notes, Priority, Status, DesiredAction

Rules:
- Type must be one of: Media, Legislator, Attorney, Prosecutor, Detective, Advocate, Other.
- Status should be Ready.
- Priority should be High, Medium, or Low.
- If something is unknown, use an empty string.
- Do not invent email addresses or phone numbers.
- DesiredAction should be a short instruction for the outreach draft.

Current Current user request:
{user_request}
"""

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt,
            text={
                "format": {
                    "type": "json_object"
                }
            }
        )

        raw = response.output_text.strip()
        payload = json.loads(raw)

        payload.setdefault("Status", "Ready")
        payload.setdefault("Source", "Command Center AI Intake")

        make_response = requests.post(make_webhook_url, json=payload, timeout=20)
        remember_ai_interaction(user_request, payload, make_response.ok, make_response.status_code)

        return jsonify({
            "ok": make_response.ok,
            "status_code": make_response.status_code,
            "payload_sent": payload,
            "make_response": make_response.text[:500]
        }), 200 if make_response.ok else make_response.status_code

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500






@app.route("/ai-memory", methods=["GET", "DELETE"])
def ai_memory():
    if request.method == "DELETE":
        save_ai_memory({"items": []})
        return jsonify({"ok": True, "message": "AI memory cleared"})
    return jsonify({"ok": True, "memory": load_ai_memory()})


# AI CONVERSATION MEMORY START
MEMORY_FILE = Path("data") / "ai_conversation_memory.json"

def load_ai_memory():
    try:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if MEMORY_FILE.exists():
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"items": []}

def save_ai_memory(memory):
    try:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")
    except Exception:
        pass

def summarize_ai_memory(limit=10):
    memory = load_ai_memory()
    items = memory.get("items", [])[-limit:]
    if not items:
        return "No prior outreach memory yet."

    lines = []
    for item in items:
        payload = item.get("payload", {})
        lines.append(
            f"- {item.get('timestamp','')} | Request: {item.get('request','')} | "
            f"Name: {payload.get('Name','')} | Org: {payload.get('Organization','')} | "
            f"Type: {payload.get('Type','')} | Email: {payload.get('Email','')} | "
            f"Priority: {payload.get('Priority','')} | DesiredAction: {payload.get('DesiredAction','')}"
        )
    return "\n".join(lines)

def remember_ai_interaction(user_request, payload, make_ok=True, status_code=200):
    memory = load_ai_memory()
    items = memory.get("items", [])
    items.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request": user_request,
        "payload": payload,
        "make_ok": bool(make_ok),
        "status_code": status_code
    })
    memory["items"] = items[-50:]
    save_ai_memory(memory)
# AI CONVERSATION MEMORY END



# CLEAN HOMEPAGE CHAT AND SEARCH START
@app.route("/site-search", methods=["GET", "POST"])
def site_search():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            q = (data.get("q") or data.get("query") or data.get("request") or "").strip()
        else:
            q = (request.args.get("q") or "").strip()

        if not q:
            return jsonify({"ok": False, "error": "Missing search query"}), 400

        roots = ["data", "contacts", "docs", "directives", "execution", "orchestration"]
        allowed = {".txt", ".md", ".json", ".csv", ".py", ".log"}
        results = []

        q_lower = q.lower()

        for root in roots:
            folder = Path(root)
            if not folder.exists():
                continue

            for file in folder.rglob("*"):
                if not file.is_file() or file.suffix.lower() not in allowed:
                    continue

                try:
                    text = file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                if q_lower in text.lower() or q_lower in file.name.lower():
                    lower = text.lower()
                    idx = lower.find(q_lower)
                    if idx < 0:
                        idx = 0

                    start = max(idx - 180, 0)
                    end = min(idx + 420, len(text))
                    snippet = text[start:end].replace("\n", " ").strip()

                    results.append({
                        "file": str(file),
                        "snippet": snippet[:700]
                    })

                if len(results) >= 10:
                    break

            if len(results) >= 10:
                break

        return jsonify({
            "ok": True,
            "query": q,
            "count": len(results),
            "results": results
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.after_request
def inject_clean_homepage_chat_and_search(response):
    try:
        if request.path == "/" and response.status_code == 200 and "text/html" in response.content_type:
            html = response.get_data(as_text=True)

            if "AI Outreach Command Box" not in html and "</body>" in html:
                widget = """
<div class="section" style="border:2px solid #16a34a;">
    <h2>AI Outreach Command Box</h2>
    <p>Type an outreach command. If Make accepts it, this will show a simple saved message instead of raw JSON.</p>

    <textarea id="aiRequest" style="width:100%;min-height:120px;border-radius:10px;padding:12px;font-size:15px;" placeholder="Example: Create outreach for John Smith at john@example.com. Use the James Jolley Foundation Medicaid gap angle. Priority High."></textarea>

    <br><br>
    <button class="button green" onclick="sendAiIntakeClean()">Send Outreach Request</button>

    <div id="aiFriendlyResult" style="margin-top:15px;background:#052e16;color:#dcfce7;padding:14px;border-radius:10px;display:none;font-weight:bold;"></div>
    <pre id="aiRawResult" style="margin-top:10px;white-space:pre-wrap;background:#020617;color:#9ca3af;padding:12px;border-radius:10px;display:none;"></pre>
</div>

<div class="section" style="border:2px solid #2563eb;">
    <h2>Case File Search</h2>
    <p>Search your Command Center folders like data, contacts, docs, directives, execution, and orchestration.</p>

    <textarea id="siteSearchQuery" style="width:100%;min-height:80px;border-radius:10px;padding:12px;font-size:15px;" placeholder="Example: Detective Jackson, CNN, Medicaid gap, grand jury, Savannah, timeline"></textarea>

    <br><br>
    <button class="button" onclick="searchSiteFiles()">Search Case Files</button>

    <div id="siteSearchResult" style="margin-top:15px;background:#111827;color:#e5e7eb;padding:14px;border-radius:10px;display:none;"></div>
</div>

<script>
async function sendAiIntakeClean() {
    const request = document.getElementById("aiRequest").value.trim();
    const friendly = document.getElementById("aiFriendlyResult");
    const raw = document.getElementById("aiRawResult");

    friendly.style.display = "block";
    raw.style.display = "none";

    if (!request) {
        friendly.textContent = "Type an outreach request first.";
        return;
    }

    friendly.textContent = "Sending request...";
    try {
        const response = await fetch("/ai-intake", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({request: request})
        });

        const data = await response.json();

        if (data.ok === true) {
            friendly.textContent = "✅ Request saved. Your automation accepted it and the draft workflow is running.";
        } else {
            friendly.textContent = "⚠️ Request received, but something needs attention.";
            raw.style.display = "block";
            raw.textContent = JSON.stringify(data, null, 2);
        }
    } catch (err) {
        friendly.textContent = "❌ Error sending request: " + err.message;
    }
}

async function searchSiteFiles() {
    const q = document.getElementById("siteSearchQuery").value.trim();
    const box = document.getElementById("siteSearchResult");
    box.style.display = "block";

    if (!q) {
        box.textContent = "Type something to search first.";
        return;
    }

    box.textContent = "Searching case files...";

    try {
        const response = await fetch("/site-search", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({q: q})
        });

        const data = await response.json();

        if (!data.ok) {
            box.textContent = "Search error: " + (data.error || "Unknown error");
            return;
        }

        if (!data.results || data.results.length === 0) {
            box.textContent = "No matching case files found for: " + q;
            return;
        }

        let html = "<b>Found " + data.count + " result(s):</b><br><br>";
        data.results.forEach((r, i) => {
            html += "<div style='margin-bottom:14px;padding:10px;background:#020617;border-radius:8px;'>";
            html += "<b>" + (i + 1) + ". " + r.file + "</b><br>";
            html += "<span style='color:#d1d5db;'>" + r.snippet + "</span>";
            html += "</div>";
        });

        box.innerHTML = html;
    } catch (err) {
        box.textContent = "Search failed: " + err.message;
    }
}
</script>
"""
                html = html.replace("</body>", widget + "\n</body>")
                response.set_data(html)

        return response
    except Exception:
        return response
# CLEAN HOMEPAGE CHAT AND SEARCH END




# COMMAND CENTER AI CHAT START
COMMAND_CENTER_SYSTEM_PROMPT = """
You are CommandCenter.AI, the integrated assistant for the user's private AI command center.

Your job:
- Understand natural language commands like ChatGPT.
- Retrieve, summarize, and analyze internal data stored in this system.
- Prioritize internal data first.
- Never hallucinate.
- Never use external internet unless explicitly instructed.
- If information does not exist, say so clearly.
- If multiple items match, ask which one the user wants.
- Treat all user data as confidential.

You can output plain text, bullets, tables, JSON, timelines, summaries, action plans, reports, and case-file formatting.

Primary mission:
Be the user's personal AI command center — retrieve, analyze, organize, and respond using ONLY internal data unless told otherwise.
"""

def command_center_internal_search(query, max_results=12):
    roots = ["data", "contacts", "docs", "directives", "execution", "orchestration"]
    allowed = {".txt", ".md", ".json", ".csv", ".py", ".log"}
    results = []
    q = (query or "").lower().strip()

    if not q:
        return results

    for root in roots:
        folder = Path(root)
        if not folder.exists():
            continue

        for file in folder.rglob("*"):
            if not file.is_file() or file.suffix.lower() not in allowed:
                continue

            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            haystack = (file.name + "\n" + text).lower()

            if q in haystack:
                idx = haystack.find(q)
                idx = max(idx, 0)
                start = max(idx - 250, 0)
                end = min(idx + 750, len(text))
                snippet = text[start:end].replace("\n", " ").strip()

                results.append({
                    "file": str(file),
                    "snippet": snippet[:900]
                })

            if len(results) >= max_results:
                return results

    return results


@app.route("/command-chat", methods=["GET", "POST"])
def command_chat():
    try:
        if request.method == "GET":
            return jsonify({
                "ok": True,
                "route": "/command-chat",
                "message": "CommandCenter.AI chat is live."
            })

        data = request.get_json(silent=True) or {}
        user_request = (data.get("request") or data.get("message") or data.get("q") or "").strip()

        if not user_request:
            return jsonify({"ok": False, "error": "Missing command text"}), 400

        case_direct_answer = command_center_case_answer(user_request)
        if case_direct_answer:
            return jsonify({"ok": True, "answer": case_direct_answer, "results": []})

        results = command_center_internal_search(user_request)

        internal_context = ""
        if results:
            for i, r in enumerate(results, 1):
                internal_context += f"\nRESULT {i}\nFILE: {r['file']}\nSNIPPET: {r['snippet']}\n"
        else:
            internal_context = "No exact internal file matches found."

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return jsonify({
                "ok": True,
                "answer": "I searched the internal command center files. OpenAI is not available, so here are the raw internal search results.",
                "results": results
            })

        client = OpenAI(api_key=api_key)

        prompt = f"""
{COMMAND_CENTER_SYSTEM_PROMPT}

User command:
{user_request}

Internal search results:
{internal_context}

Answer clearly. If the internal data does not contain the answer, say that clearly. Do not invent facts.
"""

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt
        )

        answer = response.output_text.strip()

        return jsonify({
            "ok": True,
            "answer": answer,
            "results": results
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.after_request
def inject_command_center_ai_chat(response):
    try:
        if request.path == "/" and response.status_code == 200 and "text/html" in response.content_type:
            html = response.get_data(as_text=True)

            if "CommandCenter.AI Chat" not in html and "</body>" in html:
                widget = """
<div class="section" style="border:2px solid #fbbf24;">
    <h2>CommandCenter.AI Chat</h2>
    <p>Ask about your internal case files, notes, logs, contacts, directives, timelines, and records.</p>

    <textarea id="commandChatInput" style="width:100%;min-height:110px;border-radius:10px;padding:12px;font-size:15px;" placeholder="Example: Open my James Jolley case files and summarize what is inside."></textarea>

    <br><br>
    <button class="button gold" onclick="sendCommandChat()">Ask CommandCenter.AI</button>

    <div id="commandChatAnswer" style="margin-top:15px;background:#111827;color:#e5e7eb;padding:14px;border-radius:10px;display:none;white-space:pre-wrap;"></div>
</div>

<script>
async function sendCommandChat() {
    const request = document.getElementById("commandChatInput").value.trim();
    const box = document.getElementById("commandChatAnswer");

    box.style.display = "block";

    if (!request) {
        box.textContent = "Type a command first.";
        return;
    }

    box.textContent = "Searching internal command center data...";

    try {
        const response = await fetch("/command-chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({request: request})
        });

        const data = await response.json();

        if (data.ok) {
            box.textContent = data.answer || "Done.";
        } else {
            box.textContent = "Error: " + (data.error || "Unknown error");
        }
    } catch (err) {
        box.textContent = "Error: " + err.message;
    }
}
</script>
"""
                html = html.replace("</body>", widget + "\n</body>")
                response.set_data(html)

        return response
    except Exception:
        return response
# COMMAND CENTER AI CHAT END




# STRUCTURED CASE DATABASE START
CASE_DB_FILE = Path("data") / "case_database.json"

def default_case_database():
    return {
        "timeline": [
            {
                "date": "2026-06-04",
                "type": "detective_contact",
                "title": "Detective Jackson outreach logged",
                "people": ["Detective Jackson"],
                "summary": "Call/text/voicemail outreach to Detective Jackson logged as pending response.",
                "source": "James Law automation log",
                "confidence": "known"
            },
            {
                "date": "2026-06-15",
                "type": "prosecutor_outreach",
                "title": "Requested meeting with Portsmouth Commonwealth's Attorney Office",
                "people": ["Stephanie Morales", "Portsmouth Commonwealth's Attorney Office"],
                "summary": "Called to request meeting with Commonwealth's Attorney Stephanie Morales. Staff took contact information.",
                "source": "user case notes",
                "confidence": "known"
            },
            {
                "date": "2026-06-17",
                "type": "prosecutor_contact",
                "title": "Kenobia Davis returned call about case meeting",
                "people": ["Kenobia Davis", "Joyce Meadows", "Detective Jackson", "Stephanie Morales"],
                "summary": "Kenobia Davis called back. Plan discussed to set meeting the following week with Joyce Meadows, Detective Jackson, and possibly Stephanie Morales to review the case.",
                "source": "user case notes",
                "confidence": "known"
            }
        ],
        "evidence": [
            {
                "id": "EV-001",
                "type": "Phone Records",
                "summary": "Call logs and extracted phone data related to James Michael Jolley case.",
                "status": "tracked"
            },
            {
                "id": "EV-002",
                "type": "Facebook Messages",
                "summary": "Messages referencing coded terms and later fentanyl-related language.",
                "status": "tracked"
            },
            {
                "id": "EV-003",
                "type": "Ring Camera",
                "summary": "Vehicle arrival/departure footage and related plate/car evidence.",
                "status": "tracked"
            },
            {
                "id": "EV-004",
                "type": "Toxicology",
                "summary": "Toxicology indicating fentanyl as cause of death.",
                "status": "tracked"
            }
        ],
        "witnesses": [
            {
                "name": "Savannah Berry",
                "role": "Witness",
                "relationship": "James's girlfriend",
                "summary": "Reportedly on phone with James in real time when drugs were obtained.",
                "status": "Needs follow-up"
            },
            {
                "name": "Sam",
                "role": "Witness",
                "relationship": "Friend / minor witness",
                "summary": "Reportedly had information related to planned sale/contact.",
                "status": "Needs follow-up"
            }
        ],
        "contacts": [
            {
                "name": "Detective Jackson",
                "type": "Detective",
                "organization": "Portsmouth Police / case detective",
                "status": "Case contact"
            },
            {
                "name": "Kenobia Davis",
                "type": "Commonwealth Attorney Office",
                "organization": "Portsmouth Commonwealth's Attorney Office",
                "status": "Office administrator / scheduling contact"
            },
            {
                "name": "Joyce Meadows",
                "type": "Prosecutor",
                "organization": "Portsmouth Commonwealth's Attorney Office",
                "status": "Meeting participant / case review contact"
            }
        ],
        "notes": [
            {
                "title": "James Jolley Foundation Mission",
                "summary": "Foundation mission is to fund teens into rehab during Medicaid or insurance delay gaps, based on James Michael Jolley's case.",
                "tags": ["foundation", "medicaid gap", "rehab", "teen overdose"]
            },
            {
                "title": "Command Center Capability",
                "summary": "Current site can accept outreach commands, route them through OpenAI, send structured data to Make, update Google Sheets, and trigger Gmail draft workflow.",
                "tags": ["command center", "automation", "make", "gmail"]
            }
        ]
    }

def load_case_database():
    CASE_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CASE_DB_FILE.exists():
        db = default_case_database()
        CASE_DB_FILE.write_text(json.dumps(db, indent=2), encoding="utf-8")
        return db
    try:
        return json.loads(CASE_DB_FILE.read_text(encoding="utf-8"))
    except Exception:
        return default_case_database()

def save_case_database(db):
    CASE_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    CASE_DB_FILE.write_text(json.dumps(db, indent=2), encoding="utf-8")

def search_case_database(query, max_results=15):
    db = load_case_database()
    q = (query or "").lower().strip()
    results = []

    if not q:
        return results

    for section, items in db.items():
        if not isinstance(items, list):
            continue

        for item in items:
            text = json.dumps(item, ensure_ascii=False).lower()
            if q in text:
                results.append({
                    "section": section,
                    "item": item
                })

            if len(results) >= max_results:
                return results

    return results

@app.route("/case-data", methods=["GET"])
def case_data():
    return jsonify({"ok": True, "case_database": load_case_database()})

@app.route("/case-add", methods=["POST"])
def case_add():
    try:
        data = request.get_json(silent=True) or {}
        section = (data.get("section") or "notes").strip()

        if section not in ["timeline", "evidence", "witnesses", "contacts", "notes"]:
            return jsonify({"ok": False, "error": "Invalid section"}), 400

        item = data.get("item")
        if not isinstance(item, dict):
            item = {
                "title": data.get("title", "Untitled note"),
                "summary": data.get("summary", data.get("text", "")),
                "tags": data.get("tags", [])
            }

        db = load_case_database()
        db.setdefault(section, [])
        db[section].append(item)
        save_case_database(db)

        return jsonify({"ok": True, "section": section, "item": item})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# Upgrade command center search function if it exists
def command_center_case_answer(user_request):
    case_results = search_case_database(user_request)
    if case_results:
        lines = ["I found internal case database records matching your request:\n"]
        for i, result in enumerate(case_results, 1):
            lines.append(f"{i}. Section: {result['section']}")
            item = result["item"]
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or item.get("type") or item.get("id") or "Record"
                summary = item.get("summary") or item.get("status") or json.dumps(item, ensure_ascii=False)
                lines.append(f"   Title/Name: {title}")
                lines.append(f"   Summary: {summary}")
                if item.get("date"):
                    lines.append(f"   Date: {item.get('date')}")
                if item.get("people"):
                    lines.append(f"   People: {', '.join(item.get('people'))}")
            lines.append("")
        return "\n".join(lines)
    return None

# STRUCTURED CASE DATABASE END

# ===== UNIVERSAL CASE INTELLIGENCE UPGRADE - SAFE JSON VERSION =====

SEARCH_TABLES = [
    "media_contacts",
    "contacts",
    "case_updates",
    "evidence",
    "witnesses",
    "timeline",
    "grand_jury",
    "court_events",
    "followups",
    "law_enforcement_contacts",
    "prosecutor_contacts",
    "legal_questions",
    "civil_case_information",
    "contradictions",
    "notes"
]

def _combined_sections():
    main_db = load_db()
    case_db = load_case_database()
    combined = {}

    for key in SEARCH_TABLES:
        combined[key] = []

        main_items = main_db.get(key, [])
        if isinstance(main_items, list):
            combined[key].extend(main_items)

        case_items = case_db.get(key, [])
        if isinstance(case_items, list):
            combined[key].extend(case_items)

    return combined

def universal_case_search(query):
    q = (query or "").lower().strip()
    if not q:
        return []

    results = []
    sections = _combined_sections()

    for section, rows in sections.items():
        for row in rows:
            text = json.dumps(row, ensure_ascii=False).lower()
            if q in text:
                results.append({
                    "section": section,
                    "record": row
                })

            if len(results) >= 50:
                return results

    return results

@app.route("/api/ai/universal-search", methods=["POST"])
def ai_universal_search():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("q") or data.get("request") or ""

    results = universal_case_search(query)

    if not results:
        return jsonify({
            "ok": True,
            "answer": f"No matching internal case files found for: {query}",
            "results": []
        })

    return jsonify({
        "ok": True,
        "answer": f"Found {len(results)} matching records across your Command Center.",
        "results": results
    })

@app.route("/api/dashboard/intelligence", methods=["GET"])
def dashboard_intelligence():
    sections = _combined_sections()
    counts = {key: len(value) for key, value in sections.items()}

    return jsonify({
        "ok": True,
        "status": "Case Intelligence Online",
        "tables_scanned": list(sections.keys()),
        "counts": counts
    })

@app.route("/api/case/report", methods=["GET"])
def generate_case_report():
    sections = _combined_sections()

    return jsonify({
        "ok": True,
        "title": "James Jolley Master Case Report",
        "victim": "James Michael Jolley",
        "date_of_death": "October 11, 2025",
        "sections": sections
    })

# ===== END UNIVERSAL CASE INTELLIGENCE UPGRADE =====



# ===== HARD FIX LIVE MAKE INTAKE ROUTES =====

@app.route("/api/ai-os/status", methods=["GET"])
def hard_fix_ai_os_status():
    return jsonify({
        "status": "online",
        "message": "AI OS intake API is live"
    })

@app.route("/api/ai-os/intake", methods=["GET", "POST"])
def hard_fix_ai_os_intake():
    from datetime import datetime

    if request.method == "GET":
        return jsonify({
            "status": "ready",
            "message": "Use POST to save case records."
        })

    data = request.get_json(force=True, silent=True) or {}

    db.execute("""
        CREATE TABLE IF NOT EXISTS case_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            source TEXT,
            category TEXT,
            people_involved TEXT,
            summary TEXT,
            supporting_evidence TEXT,
            open_questions TEXT,
            importance_level TEXT,
            next_action TEXT,
            created_at TEXT
        )
    """)

    db.execute("""
        INSERT INTO case_intake
        (date, source, category, people_involved, summary, supporting_evidence,
         open_questions, importance_level, next_action, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("date") or datetime.now().strftime("%Y-%m-%d"),
        data.get("source") or "Make.com Intake",
        data.get("category") or "Timeline Event",
        data.get("people_involved") or "",
        data.get("summary") or "",
        data.get("supporting_evidence") or "",
        data.get("open_questions") or "",
        data.get("importance") or "Medium",
        data.get("next_action") or "",
        datetime.now().isoformat()
    ))

    db.commit()

    return jsonify({
        "status": "saved",
        "table": "case_intake"
    })

# ===== END HARD FIX LIVE MAKE INTAKE ROUTES =====


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# ===== AI OS SAFE UPGRADE =====

from datetime import datetime
import re

AI_OS_TABLES = [
    "media_contacts",
    "case_updates",
    "evidence",
    "witnesses",
    "timeline",
    "grand_jury",
    "court_events",
    "follow_ups",
    "law_enforcement_contacts",
    "prosecutor_contacts",
    "media_coverage",
    "notes",
    "documents"
]

def ai_os_rows(table):
    try:
        rows = db.execute(f"SELECT * FROM {table}").fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []

def ai_os_all_data():
    return {table: ai_os_rows(table) for table in AI_OS_TABLES}

def ai_os_text(row):
    return " ".join(str(v) for v in row.values() if v is not None).lower()

def ai_os_search_records(query, limit=50):
    q = query.lower()
    words = [w for w in re.findall(r"[a-zA-Z0-9]+", q) if len(w) > 2]
    results = []

    for table, rows in ai_os_all_data().items():
        for row in rows:
            text = ai_os_text(row)
            score = 0

            if q in text:
                score += 25

            for word in words:
                if word in text:
                    score += 4

            if "detective jackson" in q and ("jackson" in text or "detective" in text):
                score += 20

            if "grand jury" in q and ("grand jury" in text or "indict" in text):
                score += 20

            if "jessica" in q and "jessica" in text:
                score += 20

            if "savannah" in q and "savannah" in text:
                score += 20

            if score > 0:
                results.append({"table": table, "score": score, "record": row})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

def ai_os_counts():
    return {table: len(rows) for table, rows in ai_os_all_data().items()}

@app.route("/api/ai-os/status", methods=["GET"])
def ai_os_status():
    return jsonify({
        "status": "James Jolley AI OS Online",
        "counts": ai_os_counts(),
        "tables_scanned": AI_OS_TABLES
    })

@app.route("/api/ai-os/chat", methods=["POST"])
def ai_os_chat():
    data = request.get_json(force=True)
    query = data.get("query", "")
    results = ai_os_search_records(query)

    if not results:
        return jsonify({
            "answer": "I searched all case tables, but no matching internal record was found.",
            "query": query,
            "results": []
        })

    return jsonify({
        "answer": f"Found {len(results)} matching records across the Command Center.",
        "query": query,
        "results": results
    })

@app.route("/api/ai-os/dashboard", methods=["GET"])
def ai_os_dashboard():
    return jsonify({
        "status": "Live AI Dashboard",
        "counts": ai_os_counts()
    })

@app.route("/api/ai-os/person/<name>", methods=["GET"])
def ai_os_person(name):
    results = ai_os_search_records(name, limit=100)
    return jsonify({
        "person": name,
        "total_matches": len(results),
        "records": results
    })

@app.route("/api/ai-os/report", methods=["GET"])
def ai_os_report():
    data = ai_os_all_data()
    return jsonify({
        "title": "James Jolley Master AI Case Report",
        "victim": "James Michael Jolley",
        "date_of_death": "October 11, 2025",
        "generated_at": datetime.now().isoformat(),
        "sections": data,
        "counts": ai_os_counts()
    })

# ===== END AI OS SAFE UPGRADE =====


# ===== DOCUMENT INDEX + FULL CASE SEARCH UPGRADE =====

from services.document_indexer import build_document_index, load_document_index, search_documents, score_text

FULL_SEARCH_TABLES = [
    "media_contacts",
    "case_updates",
    "evidence",
    "witnesses",
    "timeline",
    "grand_jury",
    "court_events",
    "follow_ups",
    "law_enforcement_contacts",
    "prosecutor_contacts",
    "media_coverage",
    "notes",
    "documents"
]

def db_rows_safe(table):
    try:
        rows = db.execute(f"SELECT * FROM {table}").fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []

def search_database_records(query, limit=25):
    results = []

    for table in FULL_SEARCH_TABLES:
        for row in db_rows_safe(table):
            text = " ".join(str(v) for v in row.values() if v is not None)
            score = score_text(query, text)

            if score > 0:
                results.append({
                    "source_type": "database",
                    "table": table,
                    "score": score,
                    "record": row
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

def best_date_from_result(result):
    if result.get("source_type") == "database":
        r = result.get("record", {})
        return r.get("date") or r.get("created_at") or r.get("event_date") or r.get("timestamp")

    metadata = result.get("metadata", {})
    dates = metadata.get("dates", [])
    return dates[0] if dates else None

def confidence_from_score(score):
    if score >= 70:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"

@app.route("/api/documents/index", methods=["GET"])
def api_documents_index():
    docs = load_document_index()
    return jsonify({
        "status": "loaded",
        "count": len(docs),
        "index_path": "data/document_index.json",
        "documents": docs[:50]
    })

@app.route("/api/documents/reindex", methods=["POST"])
def api_documents_reindex():
    docs = build_document_index()
    return jsonify({
        "status": "reindexed",
        "count": len(docs),
        "index_path": "data/document_index.json"
    })

@app.route("/api/ai-os/document-status", methods=["GET"])
def api_document_status():
    docs = load_document_index()
    files = sorted(list(set(d.get("file") for d in docs if d.get("file"))))

    return jsonify({
        "status": "document index online",
        "indexed_chunks": len(docs),
        "indexed_files": len(files),
        "files": files[:200]
    })

@app.route("/api/ai-os/full-search", methods=["POST"])
def api_full_search():
    payload = request.get_json(force=True)
    query = payload.get("query", "")

    db_results = search_database_records(query, limit=25)
    doc_results = search_documents(query, limit=25)

    combined = db_results + doc_results
    combined.sort(key=lambda x: x.get("score", 0), reverse=True)

    if not combined:
        return jsonify({
            "answer": "I searched both the database and local case files, but no matching internal record was found.",
            "query": query,
            "best_answer": None,
            "confidence_level": "Low",
            "database_results": [],
            "document_results": [],
            "supporting_records": []
        })

    best = combined[0]
    best_date = best_date_from_result(best)
    confidence = confidence_from_score(best.get("score", 0))

    if best.get("source_type") == "document":
        source = best.get("file")
        preview = best.get("text_preview", "")
    else:
        source = best.get("table")
        preview = str(best.get("record", ""))[:800]

    return jsonify({
        "answer": "I searched both your database and local case files. The strongest match is shown below.",
        "query": query,
        "best_answer": {
            "source_type": best.get("source_type"),
            "source": source,
            "date_found": best_date,
            "preview": preview,
            "score": best.get("score")
        },
        "confidence_level": confidence,
        "database_results": db_results,
        "document_results": doc_results,
        "supporting_records": combined[:15]
    })

# ===== END DOCUMENT INDEX + FULL CASE SEARCH UPGRADE =====


# ===== MAKE INTAKE API FIX =====

from datetime import datetime

@app.route("/api/ai-os/status", methods=["GET"])
def make_ai_os_status_fix():
    return jsonify({
        "status": "online",
        "message": "James Jolley Command Center AI OS intake API is live"
    })

@app.route("/api/ai-os/intake", methods=["POST", "GET"])
def make_ai_os_intake_fix():
    if request.method == "GET":
        return jsonify({
            "status": "ready",
            "message": "Use POST to send case records into the Command Center."
        })

    data = request.get_json(force=True, silent=True) or {}

    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    source = data.get("source") or "Make.com Intake"
    category = data.get("category") or "Timeline Event"
    people = data.get("people_involved") or ""
    summary = data.get("summary") or ""
    supporting_evidence = data.get("supporting_evidence") or ""
    open_questions = data.get("open_questions") or ""
    importance = data.get("importance") or data.get("importance_level") or "Medium"
    next_action = data.get("next_action") or ""

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS case_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                source TEXT,
                category TEXT,
                people_involved TEXT,
                summary TEXT,
                supporting_evidence TEXT,
                open_questions TEXT,
                importance_level TEXT,
                next_action TEXT,
                created_at TEXT
            )
        """)

        db.execute("""
            INSERT INTO case_intake
            (date, source, category, people_involved, summary, supporting_evidence,
             open_questions, importance_level, next_action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, source, category, people, summary, supporting_evidence,
            open_questions, importance, next_action, datetime.now().isoformat()
        ))

        db.commit()

        return jsonify({
            "status": "saved",
            "table": "case_intake",
            "record": {
                "date": date,
                "source": source,
                "category": category,
                "people_involved": people,
                "summary": summary,
                "supporting_evidence": supporting_evidence,
                "open_questions": open_questions,
                "importance_level": importance,
                "next_action": next_action
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ===== END MAKE INTAKE API FIX =====
