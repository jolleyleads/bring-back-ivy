import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_FILE = DATA_DIR / "emails.json"
API_KEY = os.getenv("IVY_API_KEY", "")


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_emails():
    ensure_data_file()
    try:
        value = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_emails(items):
    ensure_data_file()
    temp_file = DATA_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
    temp_file.replace(DATA_FILE)


def authorized():
    if not API_KEY:
        return True
    supplied = request.headers.get("X-API-Key") or request.args.get("api_key")
    return supplied == API_KEY


def clean_email(payload):
    return {
        "id": payload.get("id") or str(uuid.uuid4()),
        "subject": str(payload.get("subject", "Untitled email")).strip(),
        "recipient": str(payload.get("recipient", "")).strip(),
        "recipient_email": str(payload.get("recipient_email", "")).strip(),
        "category": str(payload.get("category", "Media Outreach")).strip(),
        "status": str(payload.get("status", "Draft")).strip(),
        "body": str(payload.get("body", "")).strip(),
        "notes": str(payload.get("notes", "")).strip(),
        "follow_up_date": str(payload.get("follow_up_date", "")).strip(),
        "created_at": payload.get("created_at")
        or datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "bring-back-ivy"})


@app.get("/")
def dashboard():
    emails = load_emails()
    emails.sort(key=lambda item: item.get("created_at", ""), reverse=True)

    stats = {
        "total": len(emails),
        "draft": sum(e.get("status", "").lower() == "draft" for e in emails),
        "approved": sum(e.get("status", "").lower() == "approved" for e in emails),
        "sent": sum(e.get("status", "").lower() == "sent" for e in emails),
        "responses": sum(e.get("status", "").lower() == "response received" for e in emails),
    }
    return render_template("dashboard.html", emails=emails, stats=stats)


@app.route("/emails/new", methods=["GET", "POST"])
def new_email():
    if request.method == "POST":
        emails = load_emails()
        emails.append(clean_email(request.form))
        save_emails(emails)
        return redirect(url_for("dashboard"))
    return render_template("new_email.html")


@app.get("/emails/<email_id>")
def email_detail(email_id):
    email = next((e for e in load_emails() if e.get("id") == email_id), None)
    if email is None:
        return "Email not found", 404
    return render_template("email_detail.html", email=email)


@app.post("/emails/<email_id>/status")
def update_status(email_id):
    emails = load_emails()
    for email in emails:
        if email.get("id") == email_id:
            email["status"] = request.form.get("status", email.get("status", "Draft"))
            email["notes"] = request.form.get("notes", email.get("notes", ""))
            email["follow_up_date"] = request.form.get(
                "follow_up_date", email.get("follow_up_date", "")
            )
            save_emails(emails)
            break
    return redirect(url_for("email_detail", email_id=email_id))


@app.post("/emails/<email_id>/delete")
def delete_email(email_id):
    emails = [e for e in load_emails() if e.get("id") != email_id]
    save_emails(emails)
    return redirect(url_for("dashboard"))


@app.route("/api/emails", methods=["GET", "POST"])
def api_emails():
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "GET":
        return jsonify(load_emails())

    payload = request.get_json(silent=True) or request.form.to_dict()
    email = clean_email(payload)
    emails = load_emails()
    emails.append(email)
    save_emails(emails)
    return jsonify({"ok": True, "email": email}), 201


@app.get("/api/emails/<email_id>")
def api_email(email_id):
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401

    email = next((e for e in load_emails() if e.get("id") == email_id), None)
    if email is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(email)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
