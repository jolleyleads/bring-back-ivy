from pathlib import Path

path = Path("app.py")
app = path.read_text(encoding="utf-8-sig")

if "from execution.add_case_update import add_case_update as doe_add_case_update" not in app:
    app = app.replace(
        "import os, csv, json, datetime, requests, html, uuid",
        "import os, csv, json, datetime, requests, html, uuid\nfrom execution.add_case_update import add_case_update as doe_add_case_update"
    )

if 'CASE_UPDATES = DATA / "case_updates.json"' not in app:
    app = app.replace(
        'TASKS = DATA / "tasks.json"',
        'TASKS = DATA / "tasks.json"\nCASE_UPDATES = DATA / "case_updates.json"'
    )

if "case_updates = load_json(CASE_UPDATES, [])" not in app:
    app = app.replace(
        "tasks = load_json(TASKS, [])",
        "tasks = load_json(TASKS, [])\n    case_updates = load_json(CASE_UPDATES, [])"
    )

if "case_update_items" not in app:
    app = app.replace(
'''    task_items = ""
    for t in tasks:
        task_items += f"<li><b>{html.escape(t.get('priority',''))}</b> — {html.escape(t.get('task',''))} [{html.escape(t.get('status',''))}]</li>"
''',
'''    task_items = ""
    for t in tasks:
        task_items += f"<li><b>{html.escape(t.get('priority',''))}</b> — {html.escape(t.get('task',''))} [{html.escape(t.get('status',''))}]</li>"

    case_update_items = ""
    for u in case_updates[-10:]:
        raw = u.get("raw_text", "")
        preview = raw[:220] + ("..." if len(raw) > 220 else "")
        case_update_items += f"<li><b>{html.escape(u.get('id',''))}</b> — {html.escape(u.get('category',''))} / {html.escape(u.get('case_stage',''))}: {html.escape(preview)}</li>"
'''
    )

card = '''
  <div class="card">
    <h2>Add Case Update to James Jolley Case Files</h2>
    <form method="post" action="/add-case-update">
      <textarea name="raw_text" placeholder="Paste the case update here. Example: Today I spoke with Detective Jackson..."></textarea>

      <input name="date" placeholder="Date if known, example: 2026-06-08">
      <input name="time" placeholder="Time if known, example: 09:30">
      <input name="subcategory" placeholder="Subcategory, example: Detective Call / Court Update / Evidence / Witness">

      <select name="category">
        <option>New Information</option>
        <option>Evidence</option>
        <option>Timeline</option>
        <option>Witness</option>
        <option>Court</option>
        <option>Prosecutor</option>
        <option>Detective</option>
        <option>Media</option>
        <option>Legislative</option>
        <option>Contradiction</option>
      </select>

      <select name="case_stage">
        <option>Needs Review</option>
        <option>New Information</option>
        <option>Evidence Logged</option>
        <option>Timeline Updated</option>
        <option>Contradictions Checked</option>
        <option>Follow-Up Needed</option>
        <option>Attorney or Prosecutor Packet Ready</option>
        <option>Media or Legislative Use</option>
        <option>Closed or Archived</option>
      </select>

      <select name="confidence">
        <option>medium</option>
        <option>high</option>
        <option>low</option>
      </select>

      <input name="source" placeholder="Source, example: Matthew / court / witness / phone call">
      <button>Add Case Update</button>
    </form>

    <h3>Recent Case Updates</h3>
    <ul>{case_update_items}</ul>
  </div>

'''

if "Add Case Update to James Jolley Case Files" not in app:
    marker = '''  <div class="card">
    <h2>Follow-Up Tasks</h2>
'''
    if marker not in app:
        raise SystemExit("Could not find Follow-Up Tasks card marker.")
    app = app.replace(marker, card + marker)

route = '''
@app.post("/add-case-update")
def add_case_update_dashboard(
    raw_text: str = Form(""),
    category: str = Form("New Information"),
    subcategory: str = Form("General Case Update"),
    case_stage: str = Form("Needs Review"),
    date: str = Form("unknown"),
    time: str = Form("unknown"),
    source: str = Form("dashboard"),
    confidence: str = Form("medium")
):
    if not raw_text.strip():
        return HTMLResponse(dashboard_html("Case update cannot be empty."))

    try:
        record = doe_add_case_update(
            raw_text=raw_text.strip(),
            category=category,
            subcategory=subcategory if subcategory.strip() else "General Case Update",
            case_stage=case_stage,
            date=date if date.strip() else "unknown",
            time=time if time.strip() else "unknown",
            source=source if source.strip() else "dashboard",
            confidence=confidence
        )

        payload = {
            "event": "case_update_added",
            "record": record,
            "timestamp": now()
        }

        make_result = make_push(payload)
        log_event("case_update_dashboard_added", f"{record.get('id','unknown')} | Make: {make_result}")

        return HTMLResponse(dashboard_html(f"Case update added: {record.get('id','saved')}"))

    except Exception as e:
        log_event("case_update_dashboard_failed", str(e))
        return HTMLResponse(dashboard_html(f"Could not add case update: {str(e)}"))


'''

if '@app.post("/add-case-update")' not in app:
    marker = '''@app.get("/logs", response_class=PlainTextResponse)
def logs():
'''
    if marker not in app:
        raise SystemExit("Could not find logs route marker.")
    app = app.replace(marker, route + marker)

path.write_text(app, encoding="utf-8")

final = path.read_text(encoding="utf-8")
required = [
    "Add Case Update to James Jolley Case Files",
    '@app.post("/add-case-update")',
    "case_update_items",
    "doe_add_case_update"
]

missing = [x for x in required if x not in final]
if missing:
    raise SystemExit("Patch failed. Missing: " + ", ".join(missing))

print("PATCH VERIFIED: form, route, case_update_items, and add_case_update import are present.")
