from pathlib import Path
import re

path = Path("app.py")
app = path.read_text(encoding="utf-8-sig")

# Add Make payload builder import.
if "from execution.make_payload import build_make_agent_payload, sample_payload" not in app:
    if "from execution.add_case_update import add_case_update as doe_add_case_update" in app:
        app = app.replace(
            "from execution.add_case_update import add_case_update as doe_add_case_update",
            "from execution.add_case_update import add_case_update as doe_add_case_update\nfrom execution.make_payload import build_make_agent_payload, sample_payload"
        )
    else:
        app = app.replace(
            "from pathlib import Path",
            "from pathlib import Path\nfrom execution.make_payload import build_make_agent_payload, sample_payload"
        )

# Replace the old inline Make payload in /add-case-update with AI-agent-ready payload.
old_block = '''        payload = {
            "event": "case_update_added",
            "record": record,
            "timestamp": now()
        }'''

new_block = '''        payload = build_make_agent_payload(record)'''

if old_block in app:
    app = app.replace(old_block, new_block)
elif "payload = build_make_agent_payload(record)" not in app:
    # Try a safer regex fallback.
    app = re.sub(
        r'\n\s*payload\s*=\s*\{\s*\n\s*"event":\s*"case_update_added",\s*\n\s*"record":\s*record,\s*\n\s*"timestamp":\s*now\(\)\s*\n\s*\}',
        "\n        payload = build_make_agent_payload(record)",
        app
    )

# Add Make test payload endpoint.
if '@app.get("/make-test-payload")' not in app:
    insert = '''

@app.get("/make-test-payload")
def make_test_payload():
    return sample_payload()

'''
    marker = '@app.get("/logs", response_class=PlainTextResponse)'
    if marker in app:
        app = app.replace(marker, insert + marker)
    else:
        app += insert

# Add Make setup page.
if '@app.get("/make-setup", response_class=HTMLResponse)' not in app:
    setup_route = '''

@app.get("/make-setup", response_class=HTMLResponse)
def make_setup():
    return """
    <!doctype html>
    <html>
    <head>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>Make AI Agent Setup</title>
      <style>
        body { font-family: Arial, sans-serif; background:#101318; color:#f5f5f5; padding:20px; }
        pre { background:#1b2230; padding:15px; border-radius:10px; white-space:pre-wrap; }
        a { color:#8db7ff; }
      </style>
    </head>
    <body>
      <h1>James Jolley Case Files — Make AI Agent Setup</h1>
      <p>Use this dashboard with Make.com:</p>
      <pre>Custom Webhook → AI Agent</pre>

      <h2>Conversation ID</h2>
      <pre>{{1.record.id}}</pre>

      <h2>Agent Input</h2>
      <pre>{{1}}</pre>

      <h2>Required Render Environment Variable</h2>
      <pre>MAKE_WEBHOOK_URL = your Make Custom Webhook URL</pre>

      <h2>Test Payload</h2>
      <p><a href='/make-test-payload'>Open /make-test-payload</a></p>

      <h2>Automation Level</h2>
      <pre>Level 2 only: log, classify, draft text, task text. Do not send email or SMS automatically.</pre>
    </body>
    </html>
    """

'''
    marker = '@app.get("/make-test-payload")'
    if marker in app:
        app = app.replace(marker, setup_route + marker)
    else:
        app += setup_route

path.write_text(app, encoding="utf-8")

final = path.read_text(encoding="utf-8")

required = [
    "build_make_agent_payload",
    "sample_payload",
    'payload = build_make_agent_payload(record)',
    '@app.get("/make-test-payload")',
    '@app.get("/make-setup", response_class=HTMLResponse)'
]

missing = [x for x in required if x not in final]
if missing:
    raise SystemExit("PATCH FAILED. Missing: " + ", ".join(missing))

print("PATCH VERIFIED: app.py now sends AI-agent-ready Make payload and has setup/test endpoints.")
