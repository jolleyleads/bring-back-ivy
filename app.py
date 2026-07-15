import csv
import io
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, redirect, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA = Path("data")
UPLOADS = Path("uploads")
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)

SECTIONS = ["emails", "evidence", "timeline", "contacts", "tasks"]


def now():
    return datetime.now(timezone.utc).isoformat()


def path_for(name):
    return DATA / f"{name}.json"


def load(name):
    path = path_for(name)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, list) else []
    except Exception:
        return []


def save(name, rows):
    path_for(name).write_text(json.dumps(rows, indent=2), encoding="utf-8")


def add(name, row):
    row = dict(row)
    row["id"] = row.get("id") or str(uuid.uuid4())
    row["created_at"] = row.get("created_at") or now()
    rows = load(name)
    rows.append(row)
    save(name, rows)


def esc(value):
    return (
        str(value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def normalize_contact(row):
    fields = [
        "id","name","organization","title","email","routing_email","phone","website",
        "category","beat","priority","status","last_contact_date","follow_up_date",
        "personalized_pitch","notes","confidence","created_at"
    ]
    clean = {field: str(row.get(field, "") or "").strip() for field in fields}
    clean["id"] = clean["id"] or str(uuid.uuid4())
    clean["created_at"] = clean["created_at"] or now()
    clean["status"] = clean["status"] or "Not Contacted"
    clean["confidence"] = clean["confidence"] or "Supported"
    return clean


def contact_key(row):
    email = (row.get("email") or row.get("routing_email") or "").strip().lower()
    if email:
        return f"email:{email}"
    return f"name:{row.get('name','').strip().lower()}|org:{row.get('organization','').strip().lower()}"


def merge_contact(existing, incoming):
    merged = dict(existing)
    for key, value in incoming.items():
        if value not in ("", None):
            if key == "notes" and merged.get("notes") and value not in merged["notes"]:
                merged["notes"] += " | " + value
            elif not merged.get(key):
                merged[key] = value
    return merged


def layout(title, body):
    nav = "".join(f'<a href="/{section}">{section.title()}</a>' for section in SECTIONS)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} • Bring Back Ivy</title>
<style>
:root{{--bg:#07110d;--panel:#112019;--panel2:#162a20;--green:#3ad17c;--text:#f5f7f4;--muted:#a8b9ae;--border:#2a4336;--red:#ef6b6b}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top right,#173a29,#07110d 45%);color:var(--text);font-family:Arial,sans-serif}}
nav{{position:sticky;top:0;background:#07110df2;border-bottom:1px solid var(--border);padding:16px 4vw;display:flex;gap:18px;flex-wrap:wrap;z-index:5}}
nav a{{color:var(--muted);text-decoration:none;font-weight:700}}nav a:first-child{{color:var(--green)}}
main{{width:min(1180px,92vw);margin:30px auto 70px}}h1{{font-size:clamp(2rem,5vw,4rem);margin:0 0 10px}}
.panel,.stat{{background:linear-gradient(145deg,var(--panel2),var(--panel));border:1px solid var(--border);border-radius:17px;padding:20px}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:13px;margin:22px 0}}.grid strong{{font-size:2rem;color:var(--green);display:block}}
.columns{{display:grid;grid-template-columns:1fr 1.2fr;gap:18px;align-items:start}}form{{display:grid;gap:12px}}
label{{display:grid;gap:6px;font-weight:700}}input,textarea,select{{width:100%;background:#08120e;color:var(--text);border:1px solid var(--border);border-radius:10px;padding:11px;font:inherit}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}button,.btn{{background:var(--green);color:#051009;border:0;border-radius:10px;padding:11px 15px;font-weight:900;cursor:pointer;text-decoration:none;display:inline-block}}
.card{{background:#0b1711;border:1px solid var(--border);border-radius:13px;padding:14px;margin:10px 0}}.card p,.card small,.muted{{color:var(--muted)}}.badge{{float:right;background:#244333;color:#9cf2bc;padding:5px 8px;border-radius:999px;font-size:.72rem;font-weight:900}}
.toolbar{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}}.danger{{background:#5a2222;color:white}}
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
    stats = {section: len(load(section)) for section in SECTIONS}
    body = f"""
    <p style="color:#3ad17c;font-weight:900">JUSTICE • ACCOUNTABILITY • BRING IVY HOME</p>
    <h1>Bring Back Ivy Command Center</h1>
    <p class="muted">Emails, evidence, timeline, contacts, tasks and media outreach in one place.</p>
    <section class="grid">
      <article class="stat"><strong>{stats['emails']}</strong><span>Emails</span></article>
      <article class="stat"><strong>{stats['evidence']}</strong><span>Evidence</span></article>
      <article class="stat"><strong>{stats['timeline']}</strong><span>Timeline</span></article>
      <article class="stat"><strong>{stats['contacts']}</strong><span>Contacts</span></article>
      <article class="stat"><strong>{stats['tasks']}</strong><span>Tasks</span></article>
    </section>"""
    return layout("Dashboard", body)


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        add("contacts", normalize_contact(request.form.to_dict()))
        return redirect(url_for("contacts"))

    rows = load("contacts")
    query = request.args.get("q", "").strip().lower()
    if query:
        rows = [row for row in rows if query in " ".join(str(v) for v in row.values()).lower()]

    cards = ""
    for row in rows:
        email = row.get("email") or row.get("routing_email") or "No verified email"
        cards += f"""
        <div class="card">
          <input type="checkbox" name="selected" value="{esc(row.get('id'))}" form="bulkForm">
          <span class="badge">{esc(row.get('status'))}</span>
          <h3>{esc(row.get('name'))}</h3>
          <p>{esc(row.get('title'))} • {esc(row.get('organization'))}</p>
          <small>{esc(row.get('category'))} • {esc(row.get('beat'))}</small>
          <p><b>Email:</b> {esc(email)}</p>
          <p><b>Priority:</b> {esc(row.get('priority'))} • <b>Confidence:</b> {esc(row.get('confidence'))}</p>
        </div>"""

    body = f"""
    <h1>Contacts</h1>
    <section class="panel">
      <form method="get" style="display:flex;gap:10px;align-items:end;flex-wrap:wrap">
        <label style="flex:1">Search<input name="q" value="{esc(request.args.get('q',''))}" placeholder="Reporter, station, beat, email"></label>
        <button>Search</button><a class="btn" href="/contacts">Clear</a>
      </form>
      <div class="toolbar">
        <a class="btn" href="/contacts/export/json">Export JSON</a>
        <a class="btn" href="/contacts/export/csv">Export CSV</a>
        <form method="post" action="/contacts/merge-duplicates"><button>Merge Duplicates</button></form>
      </div>
    </section>

    <section class="columns" style="margin-top:18px">
      <div class="panel">
        <h2>Add Contact</h2>
        <form method="post">
          <label>Name<input name="name" required></label>
          <div class="two"><label>Organization<input name="organization"></label><label>Title<input name="title"></label></div>
          <div class="two"><label>Email<input name="email" type="email"></label><label>Routing Email<input name="routing_email" type="email"></label></div>
          <div class="two"><label>Phone<input name="phone"></label><label>Website<input name="website"></label></div>
          <div class="two"><label>Category<input name="category"></label><label>Beat<input name="beat"></label></div>
          <div class="two"><label>Priority<input name="priority"></label><label>Status<input name="status" value="Not Contacted"></label></div>
          <div class="two"><label>Last Contacted<input name="last_contact_date" type="date"></label><label>Follow-Up Date<input name="follow_up_date" type="date"></label></div>
          <label>Personalized Pitch<textarea name="personalized_pitch" rows="4"></textarea></label>
          <label>Notes<textarea name="notes" rows="4"></textarea></label>
          <label>Confidence<input name="confidence" value="Supported"></label>
          <button>Save Contact</button>
        </form>
      </div>

      <div class="panel">
        <h2>Import Contacts</h2>
        <p class="muted">Upload JSON or CSV. Existing contacts are merged by email or by name and organization.</p>
        <form method="post" action="/contacts/import" enctype="multipart/form-data">
          <label>Contact File<input type="file" name="file" accept=".json,.csv" required></label>
          <button>Import Contacts</button>
        </form>
        <form id="bulkForm" method="post" action="/contacts/bulk-delete" style="margin-top:18px">
          <button class="danger" onclick="return confirm('Delete selected contacts?')">Delete Selected</button>
        </form>
        <h2 style="margin-top:22px">Saved Contacts</h2>
        {cards or '<p class="muted">No contacts yet.</p>'}
      </div>
    </section>"""
    return layout("Contacts", body)


@app.post("/contacts/import")
def contacts_import():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return redirect(url_for("contacts"))

    raw = uploaded.read()
    filename = uploaded.filename.lower()
    imported = []

    try:
        if filename.endswith(".json"):
            payload = json.loads(raw.decode("utf-8-sig"))
            if isinstance(payload, dict):
                payload = payload.get("contacts", [])
            imported = [normalize_contact(row) for row in payload if isinstance(row, dict)]
        elif filename.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            imported = [normalize_contact(dict(row)) for row in reader]
        else:
            return "Only JSON and CSV files are supported.", 400
    except Exception:
        return "Import failed. Check the file format.", 400

    existing = load("contacts")
    index = {contact_key(row): row for row in existing}
    for row in imported:
        key = contact_key(row)
        if key in index:
            index[key].update(merge_contact(index[key], row))
        else:
            existing.append(row)
            index[key] = row

    save("contacts", existing)
    return redirect(url_for("contacts"))


@app.post("/contacts/merge-duplicates")
def contacts_merge_duplicates():
    merged = {}
    for row in load("contacts"):
        row = normalize_contact(row)
        key = contact_key(row)
        merged[key] = merge_contact(merged[key], row) if key in merged else row
    save("contacts", list(merged.values()))
    return redirect(url_for("contacts"))


@app.get("/contacts/export/json")
def contacts_export_json():
    return Response(
        json.dumps(load("contacts"), indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=bring-back-ivy-contacts.json"},
    )


@app.get("/contacts/export/csv")
def contacts_export_csv():
    fields = [
        "id","name","organization","title","email","routing_email","phone","website",
        "category","beat","priority","status","last_contact_date","follow_up_date",
        "personalized_pitch","notes","confidence","created_at"
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in load("contacts"):
        writer.writerow({field: row.get(field, "") for field in fields})
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=bring-back-ivy-contacts.csv"},
    )


@app.post("/contacts/bulk-delete")
def contacts_bulk_delete():
    selected = set(request.form.getlist("selected"))
    save("contacts", [row for row in load("contacts") if row.get("id") not in selected])
    return redirect(url_for("contacts"))


@app.route("/emails", methods=["GET", "POST"])
def emails():
    if request.method == "POST":
        add("emails", request.form.to_dict())
        return redirect(url_for("emails"))
    cards = "".join(
        f'<div class="card"><span class="badge">{esc(row.get("status"))}</span><h3>{esc(row.get("subject"))}</h3><p>{esc(row.get("recipient"))}</p><pre>{esc(row.get("body"))}</pre></div>'
        for row in reversed(load("emails"))
    )
    body = f"""<h1>Email Center</h1><section class="columns"><div class="panel"><form method="post">
    <label>Recipient<input name="recipient" required></label><label>Subject<input name="subject" required></label>
    <label>Status<input name="status" value="Draft"></label><label>Email Body<textarea name="body" rows="14" required></textarea></label>
    <button>Save Email</button></form></div><div class="panel">{cards or '<p class="muted">No emails yet.</p>'}</div></section>"""
    return layout("Emails", body)


@app.route("/evidence", methods=["GET", "POST"])
def evidence():
    if request.method == "POST":
        row = request.form.to_dict()
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename:
            filename = f"{uuid.uuid4()}_{secure_filename(uploaded.filename)}"
            uploaded.save(UPLOADS / filename)
            row["filename"] = filename
        add("evidence", row)
        return redirect(url_for("evidence"))
    cards = "".join(
        f'<div class="card"><h3>{esc(row.get("title"))}</h3><p>{esc(row.get("description"))}</p></div>'
        for row in reversed(load("evidence"))
    )
    body = f"""<h1>Evidence</h1><section class="columns"><div class="panel"><form method="post" enctype="multipart/form-data">
    <label>Title<input name="title" required></label><label>Description<textarea name="description"></textarea></label>
    <label>File<input type="file" name="file"></label><button>Save Evidence</button></form></div><div class="panel">{cards or '<p class="muted">No evidence yet.</p>'}</div></section>"""
    return layout("Evidence", body)


@app.get("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOADS, filename)


def simple_section(name, title):
    if request.method == "POST":
        add(name, request.form.to_dict())
        return redirect(f"/{name}")
    cards = "".join(
        f'<div class="card"><h3>{esc(row.get("title") or row.get("name"))}</h3><p>{esc(row.get("description") or row.get("notes"))}</p></div>'
        for row in reversed(load(name))
    )
    body = f"""<h1>{title}</h1><section class="columns"><div class="panel"><form method="post">
    <label>Title or Name<input name="title"></label><label>Description or Notes<textarea name="description"></textarea></label>
    <button>Save</button></form></div><div class="panel">{cards or '<p class="muted">No records yet.</p>'}</div></section>"""
    return layout(title, body)


@app.route("/timeline", methods=["GET", "POST"])
def timeline():
    return simple_section("timeline", "Case Timeline")


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    return simple_section("tasks", "Tasks")


@app.get("/media-kit")
def media_kit():
    return layout("Media Kit", "<h1>Media Kit</h1><section class='panel'><p>Project email: bringIVhome@gmail.com</p><p>Use verified facts, clearly label allegations, and identify unanswered questions.</p></section>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
