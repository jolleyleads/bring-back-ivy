import json
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
LOGS = BASE / "logs"

DATA.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

CASE_UPDATES = DATA / "case_updates.json"
ACTIVITY_LOG = LOGS / "activity.log"

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def log_event(event, detail=""):
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{now()}] {event} | {detail}\n")

def add_case_update(
    raw_text,
    category="New Information",
    subcategory="General Case Update",
    case_stage="Needs Review",
    date="unknown",
    time="unknown",
    source="dashboard",
    confidence="medium"
):
    updates = load_json(CASE_UPDATES, [])

    record = {
        "id": f"case_update_{len(updates) + 1}",
        "created_at": now(),
        "category": category or "New Information",
        "subcategory": subcategory or "General Case Update",
        "case_stage": case_stage or "Needs Review",
        "date": date or "unknown",
        "time": time or "unknown",
        "source": source or "dashboard",
        "confidence": confidence or "medium",
        "raw_text": raw_text,
        "timeline_impact": "needs review",
        "evidence_impact": "needs review",
        "witness_impact": "needs review",
        "court_prosecutor_detective_impact": "needs review",
        "media_legislative_impact": "needs review",
        "contradictions_found": [],
        "follow_up_actions": [],
        "missing_information": [],
        "recommended_next_step": "Review this update under directives/case_workspace_wrapper.md"
    }

    updates.append(record)
    save_json(CASE_UPDATES, updates)
    log_event("case_update_added", record["id"])
    return record

if __name__ == "__main__":
    print("add_case_update module OK")
