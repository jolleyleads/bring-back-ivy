# DOE James Jolley Command Center Flask app
# Replace your repo's app.py with this file, commit, and Render will redeploy.

import os
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
        "Media Contacts":len(db["media_contacts"]), "Case Updates":len(db["case_updates"]), "Evidence":len(db["evidence"]),
        "Witnesses":len(db["witnesses"]), "Timeline":len(db["timeline"]), "Grand Jury":len(db["grand_jury"]),
        "Court Events":len(db["court_events"]), "Follow-Ups":len(db["followups"])
    }
    html="<html><body style='font-family:Arial;background:#111;color:white;padding:25px'><h1>James Jolley Command Center</h1><h2>DOE Case Files Dashboard</h2>"
    html += "".join(f"<p><b>{k}:</b> {v}</p>" for k,v in stats.items())
    html += "<h3>Endpoints</h3><p>POST /api/case-update | /api/media-contact | /api/evidence | /api/timeline | /api/witness | /api/court-event | /api/grand-jury | /api/followup</p>"
    html += "<h3>Recent Activity</h3>" + "".join(f"<p><b>{a.get('time','')}</b> - {a.get('message','')}</p>" for a in db["activity"][:30])
    html += "</body></html>"
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

@app.route("/api/email-sent", methods=["POST"])
def email_sent():
    db=load_db(); rec=clean(request.get_json(silent=True) or {},"Media Coverage","email"); db["emails"].insert(0,rec); add_activity(db,"Email activity logged"); save_db(db); return jsonify({"success":True,"record":rec})

if __name__ == "__main__":
    port=int(os.environ.get("PORT",5000)); app.run(host="0.0.0.0", port=port)
