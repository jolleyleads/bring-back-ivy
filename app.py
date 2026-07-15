import json, os, uuid
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA = Path("data")
UPLOADS = Path("uploads")
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)

SECTIONS = ["emails", "evidence", "timeline", "contacts", "tasks"]

def path_for(name):
    return DATA / f"{name}.json"

def load(name):
    p = path_for(name)
    if not p.exists():
        p.write_text("[]", encoding="utf-8")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

def save(name, rows):
    path_for(name).write_text(json.dumps(rows, indent=2), encoding="utf-8")

def add(name, row):
    rows = load(name)
    row["id"] = str(uuid.uuid4())
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    rows.append(row)
    save(name, rows)

def esc(v):
    return str(v or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def layout(title, body):
    nav = "".join(f'<a href="/{x}">{x.title()}</a>' for x in SECTIONS)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} • Bring Back Ivy</title>
<style>
:root{{--bg:#07110d;--panel:#112019;--panel2:#162a20;--green:#3ad17c;--text:#f5f7f4;--muted:#a8b9ae;--border:#2a4336}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top right,#173a29,#07110d 45%);color:var(--text);font-family:Arial,sans-serif}}
nav{{position:sticky;top:0;background:#07110df2;border-bottom:1px solid var(--border);padding:16px 4vw;display:flex;gap:18px;flex-wrap:wrap;z-index:5}}
nav a{{color:var(--muted);text-decoration:none;font-weight:700}}nav a:first-child{{color:var(--green)}}
main{{width:min(1180px,92vw);margin:30px auto 70px}}h1{{font-size:clamp(2rem,5vw,4rem);margin:0 0 10px}}h2{{margin-top:0}}
.hero{{margin-bottom:26px}}.eyebrow{{color:var(--green);font-weight:900;letter-spacing:.14em;font-size:.75rem}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:13px;margin:22px 0}}.grid article,.panel{{background:linear-gradient(145deg,var(--panel2),var(--panel));border:1px solid var(--border);border-radius:17px;padding:20px}}
.grid strong{{font-size:2rem;color:var(--green);display:block}}.grid span,.muted{{color:var(--muted)}}
.columns{{display:grid;grid-template-columns:1fr 1.15fr;gap:18px;align-items:start}}form{{display:grid;gap:12px}}
label{{display:grid;gap:6px;font-weight:700}}input,textarea,select{{width:100%;background:#08120e;color:var(--text);border:1px solid var(--border);border-radius:10px;padding:11px;font:inherit}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}button,.btn{{background:var(--green);color:#051009;border:0;border-radius:10px;padding:11px 15px;font-weight:900;cursor:pointer;text-decoration:none;display:inline-block}}
.card{{background:#0b1711;border:1px solid var(--border);border-radius:13px;padding:14px;margin:10px 0}}.card p,.card small{{color:var(--muted)}}.badge{{float:right;background:#244333;color:#9cf2bc;padding:5px 8px;border-radius:999px;font-size:.72rem;font-weight:900}}
pre{{white-space:pre-wrap;font-family:inherit;line-height:1.6;background:#08120e;border:1px solid var(--border);padding:16px;border-radius:12px}}
@media(max-width:850px){{.grid{{grid-template-columns:repeat(2,1fr)}}.columns{{grid-template-columns:1fr}}.two{{grid-template-columns:1fr}}}}
</style></head><body>
<nav><a href="/">BRING BACK IVY</a>{nav}<a href="/media-kit">Media Kit</a></nav>
<main>{body}</main></body></html>"""

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.get("/")
def home():
    stats = {x: len(load(x)) for x in SECTIONS}
    body = f"""
<section class="hero"><p class="eyebrow">JUSTICE • ACCOUNTABILITY • BRING IVY HOME</p>
<h1>Bring Back Ivy Command Center</h1>
<p class="muted">Emails, evidence, timeline, contacts, tasks and media materials in one place.</p></section>
<section class="grid">
<article><strong>{stats['emails']}</strong><span>Emails</span></article>
<article><strong>{stats['evidence']}</strong><span>Evidence Items</span></article>
<article><strong>{stats['timeline']}</strong><span>Timeline Events</span></article>
<article><strong>{stats['contacts']}</strong><span>Contacts</span></article>
<article><strong>{stats['tasks']}</strong><span>Tasks</span></article>
</section>
<section class="panel"><h2>How to use it</h2>
<p>Add every ChatGPT email to the Email Center, upload evidence, build the timeline, save contacts and track follow-ups.</p></section>"""
    return layout("Dashboard", body)

@app.route("/emails", methods=["GET","POST"])
def emails():
    if request.method == "POST":
        add("emails", {k: request.form.get(k,"") for k in [
            "subject","recipient","recipient_email","organization","category","priority",
            "status","case_topic","summary","body","follow_up_date","next_action","confidence","notes"
        ]})
        return redirect(url_for("emails"))
    cards = ""
    for x in reversed(load("emails")):
        cards += f"""<div class="card"><span class="badge">{esc(x.get('status'))}</span>
        <h3>{esc(x.get('subject'))}</h3><p>{esc(x.get('recipient'))} • {esc(x.get('organization'))}</p>
        <small>{esc(x.get('category'))} • {esc(x.get('priority'))} • {esc(x.get('confidence'))}</small>
        <pre>{esc(x.get('body'))}</pre></div>"""
    body = f"""<p class="eyebrow">COMMUNICATIONS CRM</p><h1>Email Center</h1>
    <section class="columns"><div class="panel"><h2>Add Enriched Email</h2>
    <form method="post">
    <div class="two"><label>Recipient<input name="recipient" required></label><label>Email<input name="recipient_email" type="email"></label></div>
    <div class="two"><label>Organization<input name="organization"></label><label>Subject<input name="subject" required></label></div>
    <div class="two"><label>Category<select name="category"><option>Media Outreach</option><option>Animal Control</option><option>Attorney</option><option>Elected Official</option><option>Public Records</option><option>Supporter</option></select></label>
    <label>Status<select name="status"><option>Draft</option><option>Ready</option><option>Sent</option><option>Follow-Up Due</option><option>Response Received</option><option>Closed</option></select></label></div>
    <div class="two"><label>Priority<select name="priority"><option>Critical</option><option selected>High</option><option>Medium</option><option>Low</option></select></label>
    <label>Confidence<select name="confidence"><option>Confirmed</option><option selected>Supported</option><option>Unverified</option></select></label></div>
    <label>Case Topic<input name="case_topic"></label><label>Summary<textarea name="summary"></textarea></label>
    <label>Email Body<textarea name="body" rows="12" required></textarea></label>
    <div class="two"><label>Follow-Up Date<input name="follow_up_date" type="date"></label><label>Next Action<input name="next_action"></label></div>
    <label>Notes<textarea name="notes"></textarea></label><button>Save Email</button></form></div>
    <div class="panel"><h2>Saved Emails</h2>{cards or '<p class="muted">No emails yet.</p>'}</div></section>"""
    return layout("Emails", body)

@app.route("/evidence", methods=["GET","POST"])
def evidence():
    if request.method == "POST":
        filename = ""
        f = request.files.get("file")
        if f and f.filename:
            filename = f"{uuid.uuid4()}_{secure_filename(f.filename)}"
            f.save(UPLOADS / filename)
        add("evidence", {
            "title":request.form.get("title",""),"date":request.form.get("date",""),
            "source":request.form.get("source",""),"category":request.form.get("category",""),
            "description":request.form.get("description",""),"confidence":request.form.get("confidence",""),
            "next_action":request.form.get("next_action",""),"filename":filename
        })
        return redirect(url_for("evidence"))
    cards=""
    for x in reversed(load("evidence")):
        link=f'<a class="btn" href="/uploads/{esc(x.get("filename"))}" target="_blank">Open File</a>' if x.get("filename") else ""
        cards+=f'<div class="card"><span class="badge">{esc(x.get("confidence"))}</span><h3>{esc(x.get("title"))}</h3><p>{esc(x.get("description"))}</p><small>{esc(x.get("category"))} • {esc(x.get("date"))} • {esc(x.get("source"))}</small><br><br>{link}</div>'
    body=f"""<p class="eyebrow">EVIDENCE MANAGEMENT</p><h1>Evidence</h1><section class="columns">
    <div class="panel"><h2>Add Evidence</h2><form method="post" enctype="multipart/form-data">
    <label>Title<input name="title" required></label><div class="two"><label>Date<input name="date" type="date"></label>
    <label>Category<select name="category"><option>Document</option><option>Photo</option><option>Video</option><option>Audio</option><option>Witness Statement</option><option>Agency Record</option></select></label></div>
    <label>Source<input name="source"></label><label>Description<textarea name="description" rows="6"></textarea></label>
    <label>Confidence<select name="confidence"><option>Confirmed</option><option>Supported</option><option selected>Unverified</option></select></label>
    <label>Next Action<input name="next_action"></label><label>File<input type="file" name="file"></label><button>Save Evidence</button></form></div>
    <div class="panel"><h2>Evidence Index</h2>{cards or '<p class="muted">No evidence yet.</p>'}</div></section>"""
    return layout("Evidence", body)

@app.get("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOADS, filename)

def simple_section(name, title, fields):
    if request.method == "POST":
        add(name, {f[0]: request.form.get(f[0],"") for f in fields})
        return redirect(f"/{name}")
    inputs=""
    for key,label,kind in fields:
        if kind=="textarea":
            inputs+=f'<label>{label}<textarea name="{key}" rows="5"></textarea></label>'
        elif kind=="date":
            inputs+=f'<label>{label}<input type="date" name="{key}"></label>'
        else:
            inputs+=f'<label>{label}<input name="{key}"></label>'
    cards=""
    for x in reversed(load(name)):
        heading=esc(x.get(fields[0][0]))
        details=" • ".join(esc(x.get(f[0])) for f in fields[1:] if x.get(f[0]))
        cards+=f'<div class="card"><h3>{heading}</h3><p>{details}</p></div>'
    body=f'<p class="eyebrow">BRING BACK IVY</p><h1>{title}</h1><section class="columns"><div class="panel"><h2>Add Record</h2><form method="post">{inputs}<button>Save</button></form></div><div class="panel"><h2>Saved Records</h2>{cards or "<p class=muted>No records yet.</p>"}</div></section>'
    return layout(title, body)

@app.route("/timeline", methods=["GET","POST"])
def timeline():
    return simple_section("timeline","Case Timeline",[("title","Event Title","text"),("event_date","Event Date","date"),("category","Category","text"),("source","Source","text"),("description","Description","textarea"),("confidence","Confidence","text"),("open_questions","Open Questions","textarea"),("next_action","Next Action","text")])

@app.route("/contacts", methods=["GET","POST"])
def contacts():
    return simple_section("contacts","Contacts",[("name","Name","text"),("organization","Organization","text"),("title","Title","text"),("email","Email","text"),("phone","Phone","text"),("category","Category","text"),("status","Status","text"),("notes","Notes","textarea")])

@app.route("/tasks", methods=["GET","POST"])
def tasks():
    return simple_section("tasks","Tasks",[("title","Task","text"),("category","Category","text"),("priority","Priority","text"),("status","Status","text"),("due_date","Due Date","date"),("assigned_to","Assigned To","text"),("description","Description","textarea")])

@app.get("/media-kit")
def media_kit():
    body="""<p class="eyebrow">PUBLIC AWARENESS</p><h1>Media Kit</h1>
    <section class="columns"><div class="panel"><h2>Core Message</h2>
    <p>Bring Back Ivy is an evidence-based advocacy project focused on documenting Ivy's removal, preserving records, seeking transparency and pursuing lawful public awareness.</p>
    <h3>Project Email</h3><p>bringIVhome@gmail.com</p></div>
    <div class="panel"><h2>Credibility Standard</h2>
    <p>Every public statement should identify whether information is confirmed, supported by documentation, alleged by a named source or still unverified.</p>
    <h3>Media File Checklist</h3><p>Case chronology, evidence index, agency correspondence, veterinary records, animal-control records, photos, videos and witness summaries.</p></div></section>"""
    return layout("Media Kit", body)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","10000")))
