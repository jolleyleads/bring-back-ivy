import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "dashboard_data.json"

def empty_db():
    return {"contacts": [], "emails": [], "followups": [], "case_updates": [], "activity": []}

def load_db():
    if not os.path.exists(DB):
        return empty_db()
    try:
        with open(DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return empty_db()

def save_db(db):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def activity(db, message):
    db["activity"].insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    })

@app.route("/")
def home():
    db = load_db()

    html = """
    <html>
    <body style="font-family:Arial;background:#111;color:white;padding:25px;">
    <h1>James Jolley Command Center</h1>
    <h2>Media Outreach Dashboard</h2>
    <h3>Stats</h3>
    """

    html += "<p>Media Contacts: " + str(len(db["contacts"])) + "</p>"
    html += "<p>Emails Sent: " + str(len(db["emails"])) + "</p>"
    html += "<p>Follow-Ups Due: " + str(len(db["followups"])) + "</p>"
    html += "<p>Case Updates: " + str(len(db["case_updates"])) + "</p>"

    html += "<h3>Recent Activity</h3>"

    if len(db["activity"]) == 0:
        html += "<p>No activity yet.</p>"
    else:
        for a in db["activity"][:20]:
            html += "<p><b>" + a.get("time", "") + "</b> - " + a.get("message", "") + "</p>"

    html += "</body></html>"
    return html

@app.route("/api/case-update", methods=["POST"])
def case_update():
    db = load_db()
    data = request.get_json(silent=True) or {}
    db["case_updates"].insert(0, data)
    activity(db, "New case update received")
    save_db(db)
    return jsonify({"success": True}), 200

@app.route("/api/media-contact", methods=["POST"])
def media_contact():
    db = load_db()
    data = request.get_json(silent=True) or {}
    db["contacts"].insert(0, data)
    activity(db, "New media contact added")
    save_db(db)
    return jsonify({"success": True}), 200

@app.route("/api/email-sent", methods=["POST"])
def email_sent():
    db = load_db()
    data = request.get_json(silent=True) or {}
    db["emails"].insert(0, data)
    activity(db, "Email sent")
    save_db(db)
    return jsonify({"success": True}), 200

@app.route("/api/followup", methods=["POST"])
def followup():
    db = load_db()
    data = request.get_json(silent=True) or {}
    db["followups"].insert(0, data)
    activity(db, "Follow-up scheduled")
    save_db(db)
    return jsonify({"success": True}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
